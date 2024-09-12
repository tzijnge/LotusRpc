from code_generation.code_generator import CppFile
from lrpc.core import LrpcFun, LrpcService, LrpcVar
from lrpc import LrpcVisitor
from typing import Set
from lrpc.codegen.common import lrpc_var_includes

class ServiceIncludeVisitor(LrpcVisitor):
    def __init__(self, output: str) -> None:
        self.output = output
        self.file: CppFile
        self.includes: Set = set()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.file = CppFile(f'{self.output}/{service.name()}.hpp')
        self.file.write('#pragma once')

    def visit_lrpc_service_end(self) -> None:
        for i in sorted(self.includes):
            self.file.write(f'#include {i}')

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        if function.number_returns() > 1:
            self.includes.add('<tuple>')

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.includes.update(lrpc_var_includes(ret))

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.includes.update(lrpc_var_includes(param))
