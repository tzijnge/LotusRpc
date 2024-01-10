from code_generation.code_generator import CppFile
from LrpcVar import LrpcVar
from LrpcDef import LrpcDef
from LrpcStruct import LrpcStruct

class StructFileWriter(object):
    def __init__(self, descriptor: LrpcStruct, lrpc_def: LrpcDef, output: str):
        self.descriptor = descriptor
        self.lrpc_def = lrpc_def
        self.namespace = lrpc_def.namespace()
        self.file = CppFile(f'{output}/{self.__qualified_name()}.hpp')

    def write(self):
        self.__write_include_guard()
        self.__write_includes()
        self.__write_struct()
        self.__write_codec()

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_includes(self):
        self.file('#include <etl/byte_stream.h>')
        self.file('#include "lrpc/EtlRwExtensions.hpp"')
        for i in self.__required_includes():
            self.file(f'#include {i}')
        self.file.newline()

    def __write_struct(self):
        if self.namespace:
            with self.file.block(f'namespace {self.namespace}'):
                self.__write_struct_impl()
        else:
            self.__write_struct_impl()

        self.file.newline()

    def __write_struct_impl(self):
        with self.file.block(f'struct {self.__qualified_name()}', ';'):
            for f in self.descriptor.fields():
                self.__write_struct_field(f)

            self.file.newline()

            with self.file.block(f'bool operator==(const {self.__qualified_name()}& other) const'):
                field_names = [f.name() for f in self.descriptor.fields()]
                fields_equal = [f'(this->{n} == other.{n})' for n in field_names]
                all_fields_equal = ' && '.join(fields_equal)
                self.file(f'return {all_fields_equal};')

            with self.file.block(f'bool operator!=(const {self.__qualified_name()}& other) const'):
                self.file(f'return !(*this == other);')

    def __write_codec(self):
        with self.file.block('namespace lrpc'):
            name = self.__name()
            self.file('template<>')
            with self.file.block(f'inline {name} read_unchecked<{name}>(etl::byte_stream_reader& reader)'):
                self.__write_decoder_body()

            self.file.newline()

            self.file('template<>')
            with self.file.block(f'inline void write_unchecked<{name}>(etl::byte_stream_writer& writer, const {name}& obj)'):
                self.__write_encoder_body()

    def __write_decoder_body(self):
        ns_prefix = f'{self.namespace}::' if self.namespace else ''

        self.file(f'{self.__name()} obj;')

        for f in self.descriptor.fields():
            if f.base_type_is_string():
                self.file(f'const auto {f.name()} = lrpc::read_unchecked<{f.read_type()}>(reader);')
                self.file(f'lrpc::copy<{f.read_type()}>({f.name()}, obj.{f.name()});')
            elif f.base_type_is_custom():
                self.file(f'obj.{f.name()} = lrpc::read_unchecked<{ns_prefix}{f.read_type()}>(reader);')
            else:
                self.file(f'obj.{f.name()} = lrpc::read_unchecked<{f.read_type()}>(reader);')

        self.file('return obj;')

    def __write_encoder_body(self):
        ns_prefix = f'{self.namespace}::' if self.namespace else ''

        for f in self.descriptor.fields():
            if f.base_type_is_custom():
                self.file(f'lrpc::write_unchecked<{ns_prefix}{f.write_type()}>(writer, obj.{f.name()});')
            else:
                self.file(f'lrpc::write_unchecked<{f.write_type()}>(writer, obj.{f.name()});')

    def __write_struct_field(self, f: LrpcVar):
        self.file(f'{f.field_type()} {f.name()};')

    def __name(self):
        ns = self.namespace
        qn = self.__qualified_name()
        return f'{ns}::{qn}' if ns else qn
    
    def __qualified_name(self):
        return self.descriptor.name()

    def __required_includes(self):
        includes = set()
        for f in self.descriptor.fields():
            includes.update(f.required_includes())

        return includes
