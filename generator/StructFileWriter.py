from code_generation.code_generator import CppFile
from LrpcVar import LrpcVar

class StructFileWriter(object):
    def __init__(self, descriptor, structs, output):
        self.descriptor = descriptor
        self.structs = structs
        self.file = CppFile(f'{output}/{self.__name()}.hpp')

    def write(self):
        self.__write_include_guard()
        self.__write_includes()
        self.__write_struct()
        self.__write_codec()

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_includes(self):
        self.file('#include "EtlRwExtensions.hpp"')
        for i in self.__required_includes():
            self.file(f'#include {i}')
        self.file.newline()

    def __write_struct(self):
        with self.file.block(f'struct {self.__name()}', ';'):
            for f in self.descriptor['fields']:
                self.__write_struct_field(f)

            self.file.newline()

            with self.file.block(f'bool operator==(const {self.__name()}& other) const'):
                field_names = [f['name'] for f in self.descriptor['fields']]
                fields_equal = [f'(this->{n} == other.{n})' for n in field_names]
                all_fields_equal = ' && '.join(fields_equal)
                self.file(f'return {all_fields_equal};')

            with self.file.block(f'bool operator!=(const {self.__name()}& other) const'):
                self.file(f'return !(*this == other);')

        self.file.newline()

    def __write_codec(self):
        with self.file.block('namespace etl'):
            name = self.__name()
            self.file('template<>')
            with self.file.block(f'inline {name} read_unchecked<{name}>(byte_stream_reader& reader)'):
                self.__write_decoder_body()

            self.file.newline()

            self.file('template<>')
            with self.file.block(f'inline void write_unchecked<{name}>(byte_stream_writer& writer, const {name}& obj)'):
                self.__write_encoder_body()

    def __write_decoder_body(self):
        self.file(f'{self.__name()} obj;')

        for field in self.descriptor['fields']:
            f = LrpcVar(field)
            if f.is_array():
                self.file(f'obj.{f.name()} = read_unchecked<{f.read_type()}, {f.array_size()}>(reader);')
            else:
                self.file(f'obj.{f.name()} = read_unchecked<{f.read_type()}>(reader);')

        self.file('return obj;')

    def __write_encoder_body(self):
        for field in self.descriptor['fields']:
            f = LrpcVar(field)
            self.file(f'write_unchecked<{f.write_type()}>(writer, obj.{f.name()});')

    def __write_struct_field(self, field):
        f = LrpcVar(field)
        self.file(f'{f.field_type()} {f.name()};')

    def __name(self):
        return self.descriptor['name']

    def __required_includes(self):
        includes = set()
        for f in self.descriptor['fields']:
            includes.update(LrpcVar(f).required_includes())

        return includes
