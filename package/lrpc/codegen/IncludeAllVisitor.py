from code_generation.code_generator import CppFile
from lrpc.core import LrpcDef
from lrpc.LrpcVisitor import LrpcVisitor
from lrpc.core import LrpcService
from lrpc.core import utils

class IncludeAllVisitor(LrpcVisitor):
    def __init__(self, output: str):
        self.lrpc_def = None
        self.output = output

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.lrpc_def = lrpc_def
        self.file = CppFile(f'{self.output}/{self.lrpc_def.name()}.hpp')

        self.file('#pragma once')
        self.file('#include "lrpc/Server.hpp"')

    def visit_lrpc_service(self, service: LrpcService):
        self.__write_service_include(service)
        self.file(f'#include "{service.name()}.hpp"')

    def visit_lrpc_service_end(self):
        self.file.newline()
        self.__write_server_class(self.lrpc_def.namespace())

    @utils.optionally_in_namespace
    def __write_server_class(self):
        rx = self.lrpc_def.rx_buffer_size()
        tx = self.lrpc_def.tx_buffer_size()
        name = self.lrpc_def.name()
        number_services = self.lrpc_def.max_service_id()

        self.file.write(f'using {name} = lrpc::Server<{number_services}, {rx}, {tx}>;')

    def __write_service_include(self, service: LrpcService):
        include_file = CppFile(f'{self.output}/{service.name()}.hpp')
        include_file('#pragma once')

        for i in service.required_includes():
            include_file(f'#include {i}')
