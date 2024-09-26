import os

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]
from lrpc import LrpcVisitor
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcService


class ServerIncludeVisitor(LrpcVisitor):
    def __init__(self, output: os.PathLike) -> None:
        self.lrpc_def: LrpcDef
        self.output = output
        self.file: CppFile

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.lrpc_def = lrpc_def
        self.file = CppFile(f"{self.output}/{self.lrpc_def.name()}.hpp")

        self.file.write("#pragma once")
        self.file.write('#include "lrpc/Server.hpp"')

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.file.write(f'#include "{service.name()}.hpp"')

    def visit_lrpc_def_end(self) -> None:
        self.file.newline()
        self.__write_server_class(self.lrpc_def.namespace())

    @optionally_in_namespace
    def __write_server_class(self) -> None:
        rx = self.lrpc_def.rx_buffer_size()
        tx = self.lrpc_def.tx_buffer_size()
        name = self.lrpc_def.name()
        max_service_id = self.lrpc_def.max_service_id()

        self.file.write(f"using {name} = lrpc::Server<{max_service_id}, {rx}, {tx}>;")
