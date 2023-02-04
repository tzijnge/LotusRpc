import click
from SematicAnalyzer import SemanticAnalyzer
from code_generation.code_generator import CppFile
import yaml
import jsonschema
import jsonschema.exceptions
from pathlib import Path
from os import path

def check_input(input, warnings_as_errors):
    errors_found = False

    with open(f'{path.dirname(__file__)}/lotusrpc-schema.json', 'r') as schema_file:
        schema = yaml.safe_load(schema_file)

        definition = yaml.safe_load(input)
        try:
            jsonschema.validate(definition, schema)
        except jsonschema.exceptions.ValidationError as e:
            print('############################################')
            print(f'############### {input.name} ###############')
            print('############################################')
            print(e)

        sa = SemanticAnalyzer()
        sa.analyze(definition)

        if warnings_as_errors:
            for e in sa.errors + sa.warnings:
                errors_found = True
                print(f'Error: {e}')
        else:
            for w in sa.warnings:
                print(f'Warning: {w}')

    return errors_found

class EnumFileWriter(object):
    def __init__(self, descriptor, output):
        self.descriptor = descriptor
        self.file = CppFile(f'{output}/{self.__name()}.hpp')

    def write(self):
        self.__write_include_guard()
        self.__write_includes()
        self.__write_enum()
        self.__write_codec()

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_includes(self):
        self.file('#include <etl/byte_stream.h>')
        self.file.newline()

    def __write_enum(self):
        with self.file.block(f'enum class {self.__name()}', ';'):
            for f in self.descriptor['fields']:
                self.file(f'{f["name"]} = {f["id"]},')

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
        name = self.descriptor['name']
        self.file(f'return static_cast<{name}>(read_unchecked<uint8_t>(reader));')

    def __write_encoder_body(self):
        self.file('write_unchecked<uint8_t>(writer, static_cast<uint8_t>(obj));')

    def __name(self):
        return self.descriptor['name']

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

def generate_structs(structs, output):
    for s in structs:
        sfw = StructFileWriter(s, output)
        sfw.write()

def generate_enums(enums, output):
    for e in enums:
        sfw = EnumFileWriter(e, output)
        sfw.write()

def generate_include_all(rpc_name, structs, enums, output):
    rpc_name = Path(rpc_name).stem
    rpc_name = rpc_name.replace('.lrpc', '')
    file = CppFile(f'{output}/{rpc_name}_all.hpp')
    file('#pragma once')
    for t in structs + enums:
        name = t['name']
        file(f'#include "{name}.hpp"')

def generate_rpc(input, output):
    definition = yaml.safe_load(input)

    structs = definition.get('structs', list())
    enums = definition.get('enums', list())

    generate_include_all(input.name, structs, enums, output)
    generate_structs(structs, output)
    generate_enums(enums, output)

@click.command()
@click.option('-w', '--warnings_as_errors',
                help='Treat warnings as errors',
                required=False,
                default=None,
                is_flag=True,
                type=str)
@click.option('-o', '--output',
                help='Path to put the generated files',
                required=False,
                default='.',
                type=click.Path())
@click.argument('input',
                type=click.File('r'))
def generate(warnings_as_errors, output, input):
    '''Generate code for file(s) INPUTS'''
    errors_found = check_input(input, warnings_as_errors)
    if not errors_found:
        input.seek(0)
        generate_rpc(input, output)

if __name__ == "__main__":
    generate()