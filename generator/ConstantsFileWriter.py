from code_generation.code_generator import CppFile
from LrpcDef import LrpcDef

class ConstantsFileWriter(object):
    def __init__(self, lrpc_def: LrpcDef, output: str):
        self.lrpc_def = lrpc_def
        self.file = CppFile(f'{output}/{self.lrpc_def.name()}_Constants.hpp')

    def write(self):
        self.__write_include_guard()
        self.__write_includes()
        self.__write_constants()

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_includes(self):
        self.file('#include <stdint.h>')
        self.file.newline()

    def __write_constants(self):
        if self.lrpc_def.namespace():
            with self.file.block(f'namespace {self.lrpc_def.namespace()}'):
                self.__write_constants_impl()
        else:
            self.__write_constants_impl()

    def __write_constants_impl(self):
        for c in self.lrpc_def.constants():
            t = c.cpp_type()
            n = c.name()
            v = str(c.value()).lower()
            self.file.write(f'constexpr {t} {n} {{{v}}};')
