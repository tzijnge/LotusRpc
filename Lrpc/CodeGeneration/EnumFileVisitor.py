from code_generation.code_generator import CppFile
from Lrpc.Core.LrpcUtils import optionally_in_namespace
from Lrpc.LrpcVisitor import LrpcVisitor
from Lrpc.Core.LrpcDef import LrpcDef
from Lrpc.Core.LrpcEnum import LrpcEnum

class EnumFileVisitor(LrpcVisitor):
    def __init__(self, output: str):
        self.descriptor = None
        self.file = None
        self.namespace = None
        self.output = output

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.namespace = lrpc_def.namespace()

    def visit_lrpc_enum(self, enum: LrpcEnum):
        self.descriptor = enum
        self.file = CppFile(f'{self.output}/{self.descriptor.name()}.hpp')

        self.__write_include_guard()

        if self.descriptor.is_external():
            self.__write_external_enum_include()
            self.file.newline()
            self.__write_external_alias_if_needed()
            self.__write_external_enum_checks()
        else:
            self.file.newline()
            self.__write_enum(self.namespace)

    def __write_external_alias_if_needed(self):
        if self.namespace or self.descriptor.external_namespace():
            self.__write_external_alias(self.namespace)
            self.file.newline()

    @optionally_in_namespace
    def __write_external_alias(self):
        name = self.__qualified_name()
        ext_ns = self.descriptor.external_namespace()
        ext_full_name = f'{ext_ns}::{name}' if ext_ns else f'::{name}'
        self.file.write(f'using {name} = {ext_full_name};')

    def __write_include_guard(self):
        self.file.write('#pragma once')

    def __write_external_enum_include(self):
        self.file.write(f'#include "{self.descriptor.external_file()}"')

    def __write_external_enum_checks(self):
        with self.file.block('namespace lrpc_private'):
            for f in self.descriptor.fields():
                ns = self.namespace
                enum_name = self.descriptor.name()
                field_name = f.name()
                field_id = f.id()
                if ns:
                    self.file.write(f'static_assert(static_cast<uint8_t>({ns}::{enum_name}::{field_name}) == {field_id}, "External enum value {field_name} is not as specified in LRPC");')
                else:
                    self.file.write(f'static_assert(static_cast<uint8_t>({enum_name}::{field_name}) == {field_id}, "External enum value {field_name} is not as specified in LRPC");')

            self.file.newline()

            self.file.write('// With the right compiler settings this function generates a compiler warning')
            self.file.write('// if the external enum declaration has fields that are not known to LRPC')
            self.file.write('// This function does not serve any purpose and is optimized out with the right compiler/linker settings')

            with self.file.block(f'void CheckEnum(const {self.__name()} v)'):
                with self.file.block('switch (v)'):
                    for f in self.descriptor.fields():
                        self.file.write(f'case {self.__name()}::{f.name()}: break;')

    @optionally_in_namespace
    def __write_enum(self):
        n = self.descriptor.name()
        with self.file.block(f'enum class {n}', ';'):
            for f in self.descriptor.fields():
                self.file.write(f'{f.name()} = {f.id()},')

    def __name(self):
        ns = self.namespace
        qn = self.__qualified_name()
        return f'{ns}::{qn}' if ns else qn
    
    def __qualified_name(self):
        return self.descriptor.name()
