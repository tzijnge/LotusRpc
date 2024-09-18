from code_generation.code_generator import CppFile
from lrpc.core import LrpcDef, LrpcService
from lrpc import LrpcVisitor
from lrpc.codegen.utils import optionally_in_namespace

class ServerIncludeVisitor(LrpcVisitor):
    def __init__(self, output: str) -> None:
        self.lrpc_def = None
        self.output = output
        self.file = None

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.lrpc_def = lrpc_def
        self.file = CppFile(f'{self.output}/{self.lrpc_def.name()}.hpp')

        self.file.write('#pragma once')
        self.file.write('#include "lrpc/Server.hpp"')

    def visit_lrpc_service(self, service: LrpcService):
        self.file.write(f'#include "{service.name()}.hpp"')

    def visit_lrpc_def_end(self):
        self.file.newline()
        self.__write_server_class(self.lrpc_def.namespace())

    @optionally_in_namespace
    def __write_server_class(self):
        rx = self.lrpc_def.rx_buffer_size()
        tx = self.lrpc_def.tx_buffer_size()
        name = self.lrpc_def.name()
        max_service_id = self.lrpc_def.max_service_id()

        self.file.write(f'using {name} = lrpc::Server<{max_service_id}, {rx}, {tx}>;')
