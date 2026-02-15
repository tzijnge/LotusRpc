from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.client_stream_shim_writer import ClientStreamShimWriter
from lrpc.codegen.common import write_file_banner
from lrpc.codegen.function_shim_writer import FunctionShimWriter
from lrpc.codegen.server_stream_response_writer import ServerStreamResponseWriter
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcFun, LrpcService, LrpcStream, LrpcVar
from lrpc.visitors import LrpcVisitor


class ServiceShimVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._file: CppFile
        self._namespace: str | None
        self._output = output
        self._service: LrpcService

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self._file = CppFile(f"{self._output.absolute()}/{service.name()}_shim.hpp")
        self._service = service

        write_file_banner(self._file)
        self._write_include_guard()
        self._write_includes()
        optionally_in_namespace(self._file, self._write_service_shim, self._namespace)

    def _write_service_shim(self) -> None:
        functions = self._service.functions()
        client_streams = [s for s in self._service.streams() if s.origin() == LrpcStream.Origin.CLIENT]
        server_streams = [s for s in self._service.streams() if s.origin() == LrpcStream.Origin.SERVER]

        with self._file.block(f"class {self._class_name()} : public lrpc::Service", ";"):
            self._file.label("public")
            self._file(f"virtual ~{self._class_name()}() = default;")
            self._file.newline()
            self._file(f"uint8_t id() const override {{ return {self._service_id()}; }}")
            self._file.newline()

            with self._file.block("void invoke(Reader &r) override"):
                self._file("const auto functionOrStreamId = r.read_unchecked<uint8_t>();")
                self._file("const auto functionOrStreamShim = shim(functionOrStreamId);")
                self._file("((this)->*(functionOrStreamShim))(r);")

            self._file.newline()
            self._write_server_stream_responses(server_streams)
            self._write_client_stream_stop_requests(client_streams)

            self._file.label("protected")
            self._write_function_declarations(functions)
            self._write_function_shims(functions)

            self._write_client_stream_declarations(client_streams)
            self._write_client_stream_shims(client_streams)

            self._write_server_stream_declarations(server_streams)
            self._write_server_stream_stop_request_shims(server_streams)

            self._file.label("private")
            self._write_shim_array(functions, client_streams, server_streams)

    def _write_function_declarations(self, functions: list[LrpcFun]) -> None:
        if len(functions) != 0:
            self._file.write("// Function declarations")

        for function in functions:
            params = self._params_string(function.params())
            returns = self._returns_string(function.returns())
            self._file.write(f"virtual {returns} {function.name()}({params}) = 0;")
            self._file.newline()

    def _write_client_stream_declarations(self, client_streams: list[LrpcStream]) -> None:
        if len(client_streams) != 0:
            self._file.write("// Client stream declarations")

        for stream in client_streams:
            params = stream.params()
            param_string = self._params_string(params)
            self._file.write(f"virtual void {stream.name()}({param_string}) = 0;")

            self._file.newline()

    def _write_server_stream_declarations(self, server_streams: list[LrpcStream]) -> None:
        if len(server_streams) != 0:
            self._file.write("// Server stream declarations")

        for stream in server_streams:
            self._file.write(f"virtual void {stream.name()}() = 0;")
            self._file.write(f"virtual void {stream.name()}_stop() = 0;")
            self._file.newline()

    def _write_function_shims(self, functions: list[LrpcFun]) -> None:
        if len(functions) != 0:
            self._file.write("// Function shims")

        writer = FunctionShimWriter(self._file)
        for function in functions:
            writer.write_function_shim(function)
            self._file.newline()

    def _write_client_stream_shims(self, client_streams: list[LrpcStream]) -> None:
        writer = ClientStreamShimWriter(self._file)

        if len(client_streams) != 0:
            self._file.write("// client stream shims")

        for stream in client_streams:
            writer.write_shim(stream)
            self._file.newline()

    def _write_server_stream_responses(self, server_streams: list[LrpcStream]) -> None:
        writer = ServerStreamResponseWriter(self._file)

        if len(server_streams) != 0:
            self._file.write("// Server stream responses")

        for stream in server_streams:
            writer.write_response(stream)
            self._file.newline()

    def _write_server_stream_stop_request_shims(self, server_streams: list[LrpcStream]) -> None:
        if len(server_streams) != 0:
            self._file.write("// Server stream start/stop shims")

        for stream in server_streams:
            with self._file.block(f"void {stream.name()}_start_stop_shim(Reader& r)"):
                self._file.write("const auto start = r.read_unchecked<bool>();")
                with self._file.block("if (start)"):
                    self._file.write(f"{stream.name()}();")
                with self._file.block("else"):
                    self._file.write(f"{stream.name()}_stop();")

            self._file.newline()

    def _write_client_stream_stop_requests(self, client_streams: list[LrpcStream]) -> None:
        if len(client_streams) != 0:
            self._file.write("// Client stream stop requests")

        for stream in client_streams:
            with self._file.block(f"void {stream.name()}_requestStop()"):
                self._file(f"requestStop({stream.id()});")

            self._file.newline()

    def _write_shim_array(
        self,
        functions: list[LrpcFun],
        client_streams: list[LrpcStream],
        server_streams: list[LrpcStream],
    ) -> None:
        max_function_or_stream_id = self._max_function_or_stream_id(functions, client_streams, server_streams)

        self._file.write(f"using ShimType = void ({self._class_name()}::*)(Reader &);")
        with self._file.block("void missingFunction_shim(Reader& r)"):
            self._file.write("const auto data = r.data();")
            self._file.write("const auto functionOrStreamId = data.at(2);")
            self._file.write("server().error(LrpcMetaError::UnknownFunctionOrStream, id(), functionOrStreamId);")
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
                    self._file(f"&{self._class_name()}::{name}_shim,")

            self._file.newline()

            with self._file.block("if (functionId >= shims.size())"):
                self._file.write(f"return &{self._class_name()}::missingFunction_shim;")

            self._file.newline()

            self._file.write("return shims.at(functionId);")

    @staticmethod
    def _params_string(params: list[LrpcVar]) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in params])

    @staticmethod
    def _returns_string(returns: list[LrpcVar]) -> str:
        if len(returns) == 0:
            return "void"

        if len(returns) == 1:
            return returns[0].return_type()

        types = ", ".join([r.return_type() for r in returns])
        return f"std::tuple<{types}>"

    def _max_function_or_stream_id(
        self,
        functions: list[LrpcFun],
        client_streams: list[LrpcStream],
        server_streams: list[LrpcStream],
    ) -> int:
        server_stream_ids = [s.id() for s in server_streams]
        client_stream_ids = [s.id() for s in client_streams]
        function_ids = [f.id() for f in functions]
        return max(server_stream_ids + client_stream_ids + function_ids)

    def _write_include_guard(self) -> None:
        self._file("#pragma once")

    def _write_includes(self) -> None:
        self._file('#include "lrpccore/Service.hpp"')
        self._file('#include "lrpccore/EtlRwExtensions.hpp"')
        self._file(f'#include "{self._service.name()}_includes.hpp"')

        self._file.newline()

    def _class_name(self) -> str:
        return self._service.name() + "_shim"

    def _service_id(self) -> int:
        return self._service.id()
