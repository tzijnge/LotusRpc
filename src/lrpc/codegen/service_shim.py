import os
from typing import Optional
from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..codegen.common import write_file_banner
from ..codegen.utils import optionally_in_namespace
from ..visitors import LrpcVisitor
from ..core import LrpcDef, LrpcService, LrpcFun, LrpcVar, LrpcStream


class ServiceShimVisitor(LrpcVisitor):
    def __init__(self, output: os.PathLike[str]) -> None:
        self.__file: CppFile
        self.__namespace: Optional[str]
        self.__output = output
        self.__service: LrpcService

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__namespace = lrpc_def.namespace()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__file = CppFile(f"{self.__output}/{service.name()}_ServiceShim.hpp")
        self.__service = service

        write_file_banner(self.__file)
        self.__write_include_guard()
        self.__write_includes(service.name())
        optionally_in_namespace(self.__file, self.__write_service_shim, self.__namespace)

    def __write_service_shim(self) -> None:
        functions = self.__service.functions()
        client_streams = [s for s in self.__service.streams() if s.origin() == LrpcStream.Origin.CLIENT]
        server_streams = [s for s in self.__service.streams() if s.origin() == LrpcStream.Origin.SERVER]

        with self.__file.block(f"class {self.__class_name()} : public lrpc::Service", ";"):
            self.__file.label("public")
            self.__file(f"virtual ~{self.__class_name()}() = default;")
            self.__file.newline()
            self.__file(f"uint8_t id() const override {{ return {self.__service_id()}; }}")
            self.__file.newline()

            with self.__file.block("void invoke(Reader &r, Writer &w) override"):
                self.__file("const auto functionOrStreamId = r.read_unchecked<uint8_t>();")
                self.__file("const auto functionOrStreamShim = shim(functionOrStreamId);")
                self.__file("((this)->*(functionOrStreamShim))(r, w);")
                self.__file("updateHeader(w);")

            self.__file.newline()
            self.__write_server_stream_responses(server_streams)
            self.__write_client_stream_stop_requests(client_streams)

            self.__file.label("protected")
            self.__write_function_declarations(functions)
            self.__write_function_shims(functions)

            self.__write_client_stream_declarations(client_streams)
            self.__write_client_stream_shims(client_streams)

            self.__write_server_stream_declarations(server_streams)
            self.__write_server_stream_stop_request_shims(server_streams)

            self.__file.label("private")
            self.__write_shim_array(functions, client_streams, server_streams)

    def __write_function_declarations(self, functions: list[LrpcFun]) -> None:
        if len(functions) != 0:
            self.__file.write("// Function declarations")

        for function in functions:
            params = self.__params_string(function.params())
            returns = self.__returns_string(function.returns())
            self.__file.write(f"virtual {returns} {function.name()}({params}) = 0;")
            self.__file.newline()

    def __write_client_stream_declarations(self, client_streams: list[LrpcStream]) -> None:
        if len(client_streams) != 0:
            self.__file.write("// Client stream declarations")

        for stream in client_streams:
            params = stream.params()
            param_string = self.__params_string(params)
            self.__file.write(f"virtual void {stream.name()}({param_string}) = 0;")

            self.__file.newline()

    def __write_server_stream_declarations(self, server_streams: list[LrpcStream]) -> None:
        if len(server_streams) != 0:
            self.__file.write("// Server stream declarations")

        for stream in server_streams:
            self.__file.write(f"virtual void {stream.name()}() = 0;")
            self.__file.write(f"virtual void {stream.name()}_stop() = 0;")
            self.__file.newline()

    def __write_function_shims(self, functions: list[LrpcFun]) -> None:
        if len(functions) != 0:
            self.__file.write("// Function shims")

        for function in functions:
            params = self.__params_string(function.params())
            reader_param_name = " r" if len(params) != 0 else ""

            with self.__file.block(f"void {function.name()}_shim(Reader&{reader_param_name}, Writer& w)"):
                self.__write_function_shim_body(function)

            self.__file.newline()

    def __write_client_stream_shims(self, client_streams: list[LrpcStream]) -> None:
        if len(client_streams) != 0:
            self.__file.write("// client stream shims")

        for stream in client_streams:
            with self.__file.block(f"void {stream.name()}_shim(Reader& r, Writer&)"):
                self.__write_stream_shim_body(stream)

            self.__file.newline()

    def __write_server_stream_responses(self, server_streams: list[LrpcStream]) -> None:
        if len(server_streams) != 0:
            self.__file.write("// Server stream responses")

        for stream in server_streams:
            returns = stream.returns()

            with self.__file.block(f"void {stream.name()}_response({self.__params_string(returns)})"):
                self.__file.write("if (server == nullptr) { return; }")
                self.__file.newline()
                self.__file.write("auto w = server->getWriter();")
                self.__file.write(f"writeHeader(w, {stream.id()});")

                for r in stream.returns():
                    self.__file.write(f"lrpc::write_unchecked<{r.write_type()}>(w, {r.name()});")

                self.__file.write("updateHeader(w);")
                self.__file.write("server->transmit(w);")

            self.__file.newline()

    def __write_server_stream_stop_request_shims(self, server_streams: list[LrpcStream]) -> None:
        if len(server_streams) != 0:
            self.__file.write("// Server stream start/stop shims")

        for stream in server_streams:
            with self.__file.block(f"void {stream.name()}_start_stop_shim(Reader& r, Writer&)"):
                self.__file.write("const auto start = r.read_unchecked<bool>();")
                with self.__file.block("if (start)"):
                    self.__file.write(f"{stream.name()}();")
                with self.__file.block("else"):
                    self.__file.write(f"{stream.name()}_stop();")

            self.__file.newline()

    def __write_client_stream_stop_requests(self, client_streams: list[LrpcStream]) -> None:
        if len(client_streams) != 0:
            self.__file.write("// Client stream stop requests")

        for stream in client_streams:
            with self.__file.block(f"void {stream.name()}_requestStop()"):
                self.__file(f"requestStop({stream.id()});")

            self.__file.newline()

    def __write_shim_array(
        self, functions: list[LrpcFun], client_streams: list[LrpcStream], server_streams: list[LrpcStream]
    ) -> None:
        max_function_or_stream_id = self.__max_function_or_stream_id(functions, client_streams, server_streams)

        self.__file.write(f"using ShimType = void ({self.__class_name()}::*)(Reader &, Writer &);")
        self.__file.write("void missingFunction_shim(Reader& r, Writer& w) { lrpc::missingFunction(r, w); }")
        self.__file.newline()

        with self.__file.block("static ShimType shim(const size_t functionId)"):
            with self.__file.block(
                f"static constexpr etl::array<ShimType, {max_function_or_stream_id + 1}> shims", ";"
            ):
                function_info = {function.id(): function.name() for function in functions}
                client_stream_info = {stream.id(): stream.name() for stream in client_streams}
                server_stream_info = {stream.id(): stream.name() + "_start_stop" for stream in server_streams}

                for fid in range(0, max_function_or_stream_id + 1):
                    name = "missingFunction"
                    name = function_info.get(fid, name)
                    name = client_stream_info.get(fid, name)
                    name = server_stream_info.get(fid, name)
                    self.__file(f"&{self.__class_name()}::{name}_shim,")

            self.__file.newline()

            with self.__file.block("if (functionId > shims.size())"):
                self.__file.write(f"return &{self.__class_name()}::missingFunction_shim;")

            self.__file.newline()

            self.__file.write("return shims.at(functionId);")

    def __write_function_shim_body(self, function: LrpcFun) -> None:
        self.__file.write(f"writeHeader(w, {function.id()});")

        for p in function.params():
            n = p.name()
            t = p.read_type()
            self.__file.write(f"const auto {n} = lrpc::read_unchecked<{t}>(r);")

        param_list = ", ".join(function.param_names())

        response = "const auto response = " if len(function.returns()) != 0 else ""
        self.__file.write(f"{response}{function.name()}({param_list});")

        returns = function.returns()
        if len(returns) == 1:
            t = returns[0].write_type()
            self.__file.write(f"lrpc::write_unchecked<{t}>(w, response);")
        else:
            for i, r in enumerate(returns):
                t = r.write_type()
                self.__file.write(f"lrpc::write_unchecked<{t}>(w, std::get<{i}>(response));")

    def __write_stream_shim_body(self, stream: LrpcStream) -> None:
        for p in stream.params():
            n = p.name()
            t = p.read_type()
            self.__file.write(f"const auto {n} = lrpc::read_unchecked<{t}>(r);")

        param_list = ", ".join(stream.param_names())

        self.__file.write(f"{stream.name()}({param_list});")

    @staticmethod
    def __params_string(params: list[LrpcVar]) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in params])

    @staticmethod
    def __returns_string(returns: list[LrpcVar]) -> str:
        if len(returns) == 0:
            return "void"

        if len(returns) == 1:
            return returns[0].return_type()

        types = ", ".join([r.return_type() for r in returns])
        return f"std::tuple<{types}>"

    def __max_function_or_stream_id(
        self, functions: list[LrpcFun], client_streams: list[LrpcStream], server_streams: list[LrpcStream]
    ) -> int:
        server_stream_ids = [s.id() for s in server_streams]
        client_stream_ids = [s.id() for s in client_streams]
        function_ids = [f.id() for f in functions]
        return max(server_stream_ids + client_stream_ids + function_ids)

    def __write_include_guard(self) -> None:
        self.__file("#pragma once")

    def __write_includes(self, service_name: str) -> None:
        self.__file('#include "lrpccore/Service.hpp"')
        self.__file('#include "lrpccore/EtlRwExtensions.hpp"')
        self.__file(f'#include "{service_name}.hpp"')

        self.__file.newline()

    def __class_name(self) -> str:
        return self.__service.name() + "ServiceShim"

    def __service_id(self) -> int:
        return self.__service.id()
