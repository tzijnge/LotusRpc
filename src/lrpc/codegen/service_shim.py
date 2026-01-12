from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.function_shim_writer import FunctionShimWriter
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcFun, LrpcService, LrpcStream, LrpcVar
from lrpc.visitors import LrpcVisitor


class ClientStreamShimWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_shim(self, stream: LrpcStream) -> None:
        with self._file.block(f"void {stream.name()}_shim(Reader& r, Writer&)"):
            for p in stream.params():
                self._write_param_readers(p)

            param_list = ", ".join(stream.param_names())
            self._file.write(f"{stream.name()}({param_list});")

    def _write_param_readers(self, param: LrpcVar) -> None:
        if param.is_array():
            self._file.write(f"{param.field_type()} {param.name()};")
            assignment = ""
        else:
            assignment = f"const auto {param.name()} = "

        self._file.write(f"{assignment}lrpc::read_unchecked<{param.rw_type()}>({self._read_params(param)});")

    @staticmethod
    def _read_params(var: LrpcVar) -> str:
        params = ["r"]
        if var.is_array():
            params.append(f"{var.name()}")
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)


class ServerStreamResponseWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_response(self, stream: LrpcStream) -> None:
        returns = stream.returns()

        with self._file.block(f"void {stream.name()}_response({self._response_params(returns)})"):
            self._file.write("if (server == nullptr) { return; }")
            self._file.newline()
            self._file.write("auto w = server->getWriter();")
            self._file.write(f"writeHeader(w, {stream.id()});")

            for r in returns:
                self._file.write(f"lrpc::write_unchecked<{r.rw_type()}>({self._write_params(r)});")

            self._file.write("updateHeader(w);")
            self._file.write("server->transmit(w);")

    @staticmethod
    def _write_params(var: LrpcVar) -> str:
        params = ["w", var.name()]

        if var.is_array():
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)

    @staticmethod
    def _response_params(params: list[LrpcVar]) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in params])


class ServiceShimVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._file: CppFile
        self._namespace: str | None
        self._output = output
        self._service: LrpcService

    def _write_service_shim(self, output: Path, service: LrpcService, namespace: str | None) -> None:
        self._file = CppFile(f"{output.absolute()}/{service.name()}_shim.hpp")
        self._service = service

        write_file_banner(self._file)
        self.__write_include_guard()
        self.__write_includes()
        optionally_in_namespace(self._file, self.__write_service_shim, namespace)

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self._write_service_shim(self._output, service, self._namespace)

    def __write_service_shim(self) -> None:
        functions = self._service.functions()
        client_streams = [s for s in self._service.streams() if s.origin() == LrpcStream.Origin.CLIENT]
        server_streams = [s for s in self._service.streams() if s.origin() == LrpcStream.Origin.SERVER]

        with self._file.block(f"class {self.__class_name()} : public lrpc::Service", ";"):
            self._file.label("public")
            self._file(f"virtual ~{self.__class_name()}() = default;")
            self._file.newline()
            self._file(f"uint8_t id() const override {{ return {self.__service_id()}; }}")
            self._file.newline()

            with self._file.block("void invoke(Reader &r, Writer &w) override"):
                self._file("const auto functionOrStreamId = r.read_unchecked<uint8_t>();")
                self._file("const auto functionOrStreamShim = shim(functionOrStreamId);")
                self._file("((this)->*(functionOrStreamShim))(r, w);")
                self._file("updateHeader(w);")

            self._file.newline()
            self.__write_server_stream_responses(server_streams)
            self.__write_client_stream_stop_requests(client_streams)

            self._file.label("protected")
            self.__write_function_declarations(functions)
            self.__write_function_shims(functions)

            self.__write_client_stream_declarations(client_streams)
            self.__write_client_stream_shims(client_streams)

            self.__write_server_stream_declarations(server_streams)
            self.__write_server_stream_stop_request_shims(server_streams)

            self._file.label("private")
            self.__write_shim_array(functions, client_streams, server_streams)

    def __write_function_declarations(self, functions: list[LrpcFun]) -> None:
        if len(functions) != 0:
            self._file.write("// Function declarations")

        for function in functions:
            params = self.__params_string(function.params())
            returns = self.__returns_string(function.returns())
            self._file.write(f"virtual {returns} {function.name()}({params}) = 0;")
            self._file.newline()

    def __write_client_stream_declarations(self, client_streams: list[LrpcStream]) -> None:
        if len(client_streams) != 0:
            self._file.write("// Client stream declarations")

        for stream in client_streams:
            params = stream.params()
            param_string = self.__params_string(params)
            self._file.write(f"virtual void {stream.name()}({param_string}) = 0;")

            self._file.newline()

    def __write_server_stream_declarations(self, server_streams: list[LrpcStream]) -> None:
        if len(server_streams) != 0:
            self._file.write("// Server stream declarations")

        for stream in server_streams:
            self._file.write(f"virtual void {stream.name()}() = 0;")
            self._file.write(f"virtual void {stream.name()}_stop() = 0;")
            self._file.newline()

    def __write_function_shims(self, functions: list[LrpcFun]) -> None:
        if len(functions) != 0:
            self._file.write("// Function shims")

        writer = FunctionShimWriter(self._file)
        for function in functions:
            writer.write_function_shim(function)
            self._file.newline()

    def __write_client_stream_shims(self, client_streams: list[LrpcStream]) -> None:
        writer = ClientStreamShimWriter(self._file)

        if len(client_streams) != 0:
            self._file.write("// client stream shims")

        for stream in client_streams:
            writer.write_shim(stream)
            self._file.newline()

    def __write_server_stream_responses(self, server_streams: list[LrpcStream]) -> None:
        writer = ServerStreamResponseWriter(self._file)

        if len(server_streams) != 0:
            self._file.write("// Server stream responses")

        for stream in server_streams:
            writer.write_response(stream)
            self._file.newline()

    def __write_server_stream_stop_request_shims(self, server_streams: list[LrpcStream]) -> None:
        if len(server_streams) != 0:
            self._file.write("// Server stream start/stop shims")

        for stream in server_streams:
            with self._file.block(f"void {stream.name()}_start_stop_shim(Reader& r, Writer&)"):
                self._file.write("const auto start = r.read_unchecked<bool>();")
                with self._file.block("if (start)"):
                    self._file.write(f"{stream.name()}();")
                with self._file.block("else"):
                    self._file.write(f"{stream.name()}_stop();")

            self._file.newline()

    def __write_client_stream_stop_requests(self, client_streams: list[LrpcStream]) -> None:
        if len(client_streams) != 0:
            self._file.write("// Client stream stop requests")

        for stream in client_streams:
            with self._file.block(f"void {stream.name()}_requestStop()"):
                self._file(f"requestStop({stream.id()});")

            self._file.newline()

    def __write_shim_array(
        self,
        functions: list[LrpcFun],
        client_streams: list[LrpcStream],
        server_streams: list[LrpcStream],
    ) -> None:
        max_function_or_stream_id = self.__max_function_or_stream_id(functions, client_streams, server_streams)

        self._file.write(f"using ShimType = void ({self.__class_name()}::*)(Reader &, Writer &);")
        with self._file.block("void missingFunction_shim(Reader& r, Writer&)"):
            self._file.write("const auto data = r.data();")
            self._file.write("const auto functionOrStreamId = data.at(2);")
            self._file.write("server->error(LrpcMetaError::UnknownFunctionOrStream, id(), functionOrStreamId);")
        self._file.newline()

        with self._file.block("static ShimType shim(const size_t functionId)"):
            with self._file.block(f"static constexpr etl::array<ShimType, {max_function_or_stream_id + 1}> shims", ";"):
                function_info = {function.id(): function.name() for function in functions}
                client_stream_info = {stream.id(): stream.name() for stream in client_streams}
                server_stream_info = {stream.id(): stream.name() + "_start_stop" for stream in server_streams}

                for fid in range(max_function_or_stream_id + 1):
                    name = "missingFunction"
                    name = function_info.get(fid, name)
                    name = client_stream_info.get(fid, name)
                    name = server_stream_info.get(fid, name)
                    self._file(f"&{self.__class_name()}::{name}_shim,")

            self._file.newline()

            with self._file.block("if (functionId >= shims.size())"):
                self._file.write(f"return &{self.__class_name()}::missingFunction_shim;")

            self._file.newline()

            self._file.write("return shims.at(functionId);")

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
        self,
        functions: list[LrpcFun],
        client_streams: list[LrpcStream],
        server_streams: list[LrpcStream],
    ) -> int:
        server_stream_ids = [s.id() for s in server_streams]
        client_stream_ids = [s.id() for s in client_streams]
        function_ids = [f.id() for f in functions]
        return max(server_stream_ids + client_stream_ids + function_ids)

    def __write_include_guard(self) -> None:
        self._file("#pragma once")

    def __write_includes(self) -> None:
        self._file('#include "lrpccore/Service.hpp"')
        self._file('#include "lrpccore/EtlRwExtensions.hpp"')
        self._file(f'#include "{self._service.name()}_includes.hpp"')

        self._file.newline()

    def __class_name(self) -> str:
        return self._service.name() + "_shim"

    def __service_id(self) -> int:
        return self._service.id()
