from code_generation.code_generator import CppFile

class StructFileWriter(object):
    def __init__(self, descriptor, output):
        self.descriptor = descriptor
        self.file = CppFile(f'{output}/{self.__name()}.hpp')

    def write(self):
        self.__write_include_guard()
        self.__write_includes()
        self.__write_struct()
        self.__write_codec()

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_includes(self):
        self.file('#include <stdint.h>')
        self.file('#include <etl/byte_stream.h>')
        if self.__has_array_fields():
            self.file('#include <etl/array.h>')
        if self.__has_optional_fields():
            self.file('#include <etl/optional.h>')
        self.file('#include "EtlRwExtensions.hpp"')
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

        for f in self.descriptor['fields']:
            name = f['name']
            if self.__field_is_array(f):
                count = f['count']
                array_type = self.__field_array_type(f)
                self.file(f'obj.{name} = read_unchecked<{array_type}, {count}>(reader);')
            else:
                self.file(f'obj.{name} = read_unchecked<{self.__field_type(f)}>(reader);')

        self.file('return obj;')

    def __write_encoder_body(self):
        for f in self.descriptor['fields']:
            name = f['name']
            if self.__field_is_array(f):
                array_type = self.__field_array_type(f)
                self.file(f'write_unchecked<const {array_type}>(writer, obj.{name});')
            else:
                self.file(f'write_unchecked<{self.__field_type(f)}>(writer, obj.{name});')

    def __write_struct_field(self, field):
        field_name = field['name']
        field_type = self.__field_type(field)
        self.file(f'{field_type} {field_name};')

    def __field_type(self, field):
        t = field['type'].strip('@')

        if self.__field_is_optional(field):
            return f'etl::optional<{t}>'

        if self.__field_is_array(field):
            count = field['count']
            return f'etl::array<{t}, {count}>'

        return t

    def __field_array_type(self, field):
        return field['type'].strip('@')

    def __name(self):
        return self.descriptor['name']

    def __has_array_fields(self):
        for f in self.descriptor['fields']:
            if self.__field_is_array(f):
                return True

        return False

    def __has_optional_fields(self):
        for f in self.descriptor['fields']:
            if self.__field_is_optional(f):
                return True

        return False

    def __field_is_optional(self, field):
        count = field.get('count', 1)
        return count == '*'

    def __field_is_array(self, field):
        count = field.get('count', 1)
        return count != '*' and count > 1
