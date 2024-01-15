from code_generation.code_generator import CppFile
from LrpcDef import LrpcDef
from LrpcEnum import LrpcEnum
from  LrpcUtils import optionally_in_namespace

class EnumFileWriter(object):
    def __init__(self, descriptor: LrpcEnum, lrpc_def: LrpcDef, output: str):
        self.descriptor = descriptor
        self.file = CppFile(f'{output}/{self.descriptor.name()}.hpp')
        self.namespace = lrpc_def.namespace()
        self.__init_alias()

    def __init_alias(self):
        ns = self.namespace
        ext_ns = self.descriptor.external_namespace()
        name = self.descriptor.name()

        if (not ns) and (not ext_ns):
            self.alias = None
        elif (not ns) and ext_ns:
            self.alias = name
        elif ns and (not ext_ns):
            self.alias = f'{ns}::{name}'
        else:
            self.alias = f'{ns}::{name}'

    def __alias_or_name(self):
        return self.alias or self.descriptor.name()


    def write(self):
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
        if self.alias:
            self.__write_external_alias(self.namespace)
            self.file.newline()

    @optionally_in_namespace
    def __write_external_alias(self):
        ext_ns = self.descriptor.external_namespace()
        name = self.descriptor.name()
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

            with self.file.block(f'void CheckEnum(const {self.__alias_or_name()} v)'):
                with self.file.block('switch (v)'):
                    for f in self.descriptor.fields():
                        self.file.write(f'case {self.__alias_or_name()}::{f.name()}: break;')

    @optionally_in_namespace
    def __write_enum(self):
        n = self.descriptor.name()
        with self.file.block(f'enum class {n}', ';'):
            for f in self.descriptor.fields():
                self.file.write(f'{f.name()} = {f.id()},')
