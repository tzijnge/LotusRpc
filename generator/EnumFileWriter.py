from code_generation.code_generator import CppFile

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
        with self.file.block('namespace lrpc'):
            name = self.__name()
            self.file('template<>')
            with self.file.block(f'inline {name} read_unchecked<{name}>(etl::byte_stream_reader& reader)'):
                self.__write_decoder_body()

            self.file.newline()

            self.file('template<>')
            with self.file.block(f'inline void write_unchecked<{name}>(etl::byte_stream_writer& writer, const {name}& value)'):
                self.__write_encoder_body()

    def __write_decoder_body(self):
        name = self.descriptor['name']
        self.file(f'return static_cast<{name}>(reader.read_unchecked<uint8_t>());')

    def __write_encoder_body(self):
        self.file('writer.write_unchecked<uint8_t>(static_cast<uint8_t>(value));')

    def __name(self):
        return self.descriptor['name']
