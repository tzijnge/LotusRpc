import os
from typing import Optional

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]
from ..visitors import LrpcVisitor
from ..codegen.utils import optionally_in_namespace
from ..core import LrpcDef, LrpcService


class ServerIncludeVisitor(LrpcVisitor):
    def __init__(self, output: os.PathLike) -> None:
        self.namespace: Optional[str]
        self.output = output
        self.file: CppFile
        self.server_class: str

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        rx = lrpc_def.rx_buffer_size()
        tx = lrpc_def.tx_buffer_size()
        name = lrpc_def.name()
        max_service_id = lrpc_def.max_service_id()
        self.server_class = f"using {name} = lrpc::Server<{max_service_id}, {rx}, {tx}>;"

        self.namespace = lrpc_def.namespace()
        self.file = CppFile(f"{self.output}/{lrpc_def.name()}.hpp")

        self.file.write("#pragma once")
        self.file.write('#include "lrpc/Server.hpp"')

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.file.write(f'#include "{service.name()}.hpp"')

    def visit_lrpc_def_end(self) -> None:
        self.file.newline()
        optionally_in_namespace(self.file, self.__write_server_class, self.namespace)

    def __write_server_class(self) -> None:
        self.file.write(self.server_class)
