from code_generation.code_generator import CppFile
from LrpcDef import LrpcDef

class IncludeAllWriter(object):
    def __init__(self, lrpc_def: LrpcDef, output: str):
        self.lrpc_def = lrpc_def
        self.output = output
        self.file = CppFile(f'{self.output}/{self.lrpc_def.name()}.hpp')

    def write(self):
        # write include file for every service, including enums, structs, stdint.h and required etl includes
        # write include all file that includes all service includes
        self.file('#pragma once')
        self.file('#include "lrpc/Server.hpp"')
        for s in self.lrpc_def.services():
            self.write_service_include(s)
            self.file(f'#include "{s.name()}.hpp"')

        rx = self.lrpc_def.rx_buffer_size()
        tx = self.lrpc_def.tx_buffer_size()

        self.file.newline()
        
        ns = self.lrpc_def.namespace()
        if ns:
            with self.file.block(f'namespace {ns}'):
                self.file(f'using {self.lrpc_def.name()} = lrpc::Server<{rx}, {tx}>;')
        else:
            self.file(f'using {self.lrpc_def.name()} = lrpc::Server<{rx}, {tx}>;')

    def write_service_include(self, service):
        include_file = CppFile(f'{self.output}/{service.name()}.hpp')
        include_file('#pragma once')

        for i in service.required_includes():
            include_file(f'#include {i}')
