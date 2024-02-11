from code_generation.code_generator import CppFile
from LrpcUtils import optionally_in_namespace
from LrpcVisitor import LrpcVisitor
from LrpcConstantBase import LrpcConstantBase
from LrpcDefBase import LrpcDefBase

class ConstantsFileVisitor(LrpcVisitor):
    def __init__(self, output: str):
        self.output = output
        self.namespace = None
        self.file = None
        self.includes = None
        self.constant_definitions = None

    def visit_lrpc_def(self, lrpc_def: LrpcDefBase):
        self.file = CppFile(f'{self.output}/{lrpc_def.name()}_Constants.hpp')
        self.namespace = lrpc_def.namespace()
        self.constant_definitions = list()
        self.includes = set()

    def visit_lrpc_constant(self, constant: LrpcConstantBase):
        if 'int' in constant.cpp_type():
            self.includes.add('stdint.h')
        if constant.cpp_type() == 'string':
            self.includes.add('etl/string_view.h')

        self.constant_definitions.append(self.__constant_definition(constant))

    def visit_lrpc_constant_end(self):
        self.__write_include_guard()
        self.__write_includes()
        self.file.newline()
        self.__write_constant_definitions(self.namespace)

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_includes(self):
        for i in self.includes:
            self.file.write(f'#include <{i}>')

    @optionally_in_namespace
    def __write_constant_definitions(self):
        for cd in self.constant_definitions:
            self.file.write(cd)

    def __constant_definition(self, constant: LrpcConstantBase):
        n = constant.name()

        if constant.cpp_type() == 'string':
            t = 'etl::string_view'
            v = f'"{constant.value()}"'
        else:
            t = constant.cpp_type()
            v = str(constant.value()).lower()

        return f'constexpr {t} {n} {{{v}}};'
