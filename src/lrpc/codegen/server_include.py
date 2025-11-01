import os
from typing import Optional

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]
from ..visitors import LrpcVisitor
from ..codegen.common import write_file_banner
from ..codegen.utils import optionally_in_namespace
from ..core import LrpcDef, LrpcService


class ServerIncludeVisitor(LrpcVisitor):
    def __init__(self, output: os.PathLike[str]) -> None:
        self.__namespace: Optional[str]
        self.__output = output
        self.__file: CppFile
        self.__server_class: str

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        rx = lrpc_def.rx_buffer_size()
        tx = lrpc_def.tx_buffer_size()
        name = lrpc_def.name()
        max_service_id = lrpc_def.max_service_id()
        self.__server_class = f"using {name} = lrpc::Server<{max_service_id}, {rx}, {tx}>;"

        self.__namespace = lrpc_def.namespace()
        self.__file = CppFile(f"{self.__output}/{lrpc_def.name()}.hpp")

        write_file_banner(self.__file)
        self.__file.write("#pragma once")
        self.__file.write('#include "lrpccore/Server.hpp"')
        if len(lrpc_def.constants()) != 0:
            self.__file.write(f'#include "{lrpc_def.name()}_Constants.hpp"')
        self.__file.write(f'#include "{lrpc_def.name()}_Meta.hpp"')

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__file.write(f'#include "{service.name()}.hpp"')
        self.__file.write(f'#include "{service.name()}_ServiceShim.hpp"')

    def visit_lrpc_def_end(self) -> None:
        self.__file.newline()
        optionally_in_namespace(self.__file, self.__write_server_class, self.__namespace)

    def __write_server_class(self) -> None:
        self.__file.write(self.__server_class)
