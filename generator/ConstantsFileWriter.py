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
        if self.__has_integer_constants():
            self.file('#include <stdint.h>')
        if self.__has_string_constants():
            self.file('#include <etl/string_view.h>')
        self.file.newline()

    def __write_constants(self):
        if self.lrpc_def.namespace():
            with self.file.block(f'namespace {self.lrpc_def.namespace()}'):
                self.__write_constants_impl()
        else:
            self.__write_constants_impl()

    def __write_constants_impl(self):
        for c in self.lrpc_def.constants():
            n = c.name()

            if c.cpp_type() == 'string':
                t = 'etl::string_view'
            else:
                t = c.cpp_type()

            if c.cpp_type() == 'string':
                v = f'"{c.value()}"'
            else:
                v = str(c.value()).lower()

            self.file.write(f'constexpr {t} {n} {{{v}}};')

    def __has_integer_constants(self):
        int_types = [t.cpp_type() for t in self.lrpc_def.constants() if 'int' in t.cpp_type()]
        return len(int_types) != 0

    def __has_string_constants(self):
        types = [t.cpp_type() for t in self.lrpc_def.constants()]
        return 'string' in types
