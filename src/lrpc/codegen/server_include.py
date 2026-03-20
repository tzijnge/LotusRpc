from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcService, RpcSettings
from lrpc.visitors import LrpcVisitor


class ServerIncludeVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._namespace: str | None
        self._output = output
        self._file: CppFile
        self._server_class: str
        self._def_name: str
        self._max_service_id: int

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._def_name = lrpc_def.name()
        self._max_service_id = lrpc_def.max_service_id()
        self._file = CppFile(f"{self._output}/{lrpc_def.name()}.hpp")

        write_file_banner(self._file)
        self._file.write("#pragma once")
        self._file.write('#include "lrpccore/Server.hpp"')
        if len(lrpc_def.constants()) != 0:
            self._file.write(f'#include "{lrpc_def.name()}_Constants.hpp"')
        self._file.write('#include "LrpcMeta_service.hpp"')

    def visit_rpc_settings(self, settings: RpcSettings) -> None:
        rx = settings.rx_buffer_size()
        tx = settings.tx_buffer_size()
        self._server_class = (
            f"using {self._def_name} = lrpc::Server<{self._max_service_id}, LrpcMeta_service, {rx}, {tx}>;"
        )
        self._namespace = settings.namespace()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        if service.name() != "LrpcMeta":
            self._file.write(f'#include "{service.name()}_includes.hpp"')
            self._file.write(f'#include "{service.name()}_shim.hpp"')

    def visit_lrpc_def_end(self) -> None:
        self._file.newline()
        optionally_in_namespace(self._file, self._write_server_class, self._namespace)

    def _write_server_class(self) -> None:
        self._file.write(self._server_class)
