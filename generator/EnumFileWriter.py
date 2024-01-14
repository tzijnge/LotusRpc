from code_generation.code_generator import CppFile
from LrpcDef import LrpcDef
from LrpcEnum import LrpcEnum

class EnumFileWriter(object):
    def __init__(self, descriptor: LrpcEnum, lrpc_def: LrpcDef, output: str):
        self.descriptor = descriptor
        self.file = CppFile(f'{output}/{self.descriptor.name()}.hpp')
        self.namespace = lrpc_def.namespace()

    def write(self):
        self.__write_include_guard()
        self.__write_enum()

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_enum(self):
        if self.namespace:
            with self.file.block(f'namespace {self.namespace}'):
                self.__write_enum_impl()
        else:
            self.__write_enum_impl()

        self.file.newline()

    def __write_enum_impl(self):
        n = self.descriptor.name()
        with self.file.block(f'enum class {n}', ';'):
            for f in self.descriptor.fields():
                self.file(f'{f.name()} = {f.id()},')
