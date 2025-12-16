from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcService
from lrpc.visitors import LrpcVisitor


class ServerIncludeVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self.__namespace: str | None
        self.__output = output
        self.__file: CppFile
        self.__server_class: str

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        rx = lrpc_def.rx_buffer_size()
        tx = lrpc_def.tx_buffer_size()
        name = lrpc_def.name()
        max_service_id = lrpc_def.max_service_id()
        self.__server_class = f"using {name} = lrpc::Server<{max_service_id}, LrpcMeta_service, {rx}, {tx}>;"

        self.__namespace = lrpc_def.namespace()
        self.__file = CppFile(f"{self.__output}/{lrpc_def.name()}.hpp")

        write_file_banner(self.__file)
        self.__file.write("#pragma once")
        self.__file.write('#include "lrpccore/Server.hpp"')
        if len(lrpc_def.constants()) != 0:
            self.__file.write(f'#include "{lrpc_def.name()}_Constants.hpp"')
        self.__file.write('#include "LrpcMeta_service.hpp"')

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__file.write(f'#include "{service.name()}_includes.hpp"')
        self.__file.write(f'#include "{service.name()}_shim.hpp"')

    def visit_lrpc_def_end(self) -> None:
        self.__file.newline()
        optionally_in_namespace(self.__file, self.__write_server_class, self.__namespace)

    def __write_server_class(self) -> None:
        self.__file.write(self.__server_class)
