from code_generation.code_generator import CppFile
from LrpcVar import LrpcVar

class DecoderShimWriter(object):
    def __init__(self, interface, structs, output):
        self.interface = interface
        self.structs = structs
        self.file = CppFile(f'{output}/{self.__name()}_DecoderShim.hpp')

    def write(self):        
        self.__write_include_guard()
        self.__write_includes()
        self.__write_shim()

    def __write_shim(self):
        with self.file.block(f'class {self.__name()}DecoderShim : public Decoder', ';'):
            self.file.label('public')
            self.file(f'uint32_t id() const override {{ return {self.__id()}; }}')
            self.file.newline()

            with self.file.block('void decode(Reader &reader, Writer &writer) override'):
                self.file('auto messageId = reader.read_unchecked<uint8_t>();')
                self.file('((this)->*(functionShims.at(messageId)))(reader, writer);')
            
            self.file.newline()
            self.file.label('protected')
            for f in self.interface['functions']:
                self.__write_function_decl(f)

            self.file.newline()

            for f in self.interface['functions']:
                function_name = f['name']
                with self.file.block(f'void {function_name}_shim(Reader &r, Writer &w)'):
                    self.__write_function_shim(f)

                self.file.newline()

            self.file.newline()
            self.file.label('private')
            with self.file.block('inline static const etl::array functionShims', ';'):
                for f in self.interface['functions']:
                    function_name = f['name']
                    self.file(f'&{self.__name()}DecoderShim::{function_name}_shim,')

    def __write_function_shim(self, function):
        function_name = function['name']

        params = self.__function_params(function)
        param_names = [p['name'] for p in params]
        returns = self.__function_returns(function)
        number_returns = len(returns)

        for p in params:
            n = p['name']
            var = LrpcVar(p, self.structs)
            t = var.read_type()
            if var.is_array():
                s = var.array_size()
                self.file(f'const auto {n} = etl::read_unchecked<{t}, {s}>(r);')
            else:
                self.file(f'const auto {n} = etl::read_unchecked<{t}>(r);')

        param_list = ', '.join(param_names)
        response = 'const auto response = ' if number_returns != 0 else ''
        self.file(f'{response}{function_name}({param_list});')

        if number_returns == 1:
            t = LrpcVar(returns[0], self.structs).write_type()
            self.file(f'etl::write_unchecked<{t}>(w, response);')
        else:
            for i, r in enumerate(returns):
                t = LrpcVar(r, self.structs).write_type()
                self.file(f'etl::write_unchecked<{t}>(w, std::get<{i}>(response));')

    def __write_function_decl(self, function):
        name = function['name']
        params = self.__params_string(function)
        returns = self.__returns_string(function)
        self.file(f'virtual {returns} {name}({params}) = 0;')

    def __params_string(self, function):
        params = self.__function_params(function)
        params_list = [self.__param_string(p) for p in params]
        return ', '.join(params_list)

    def __param_string(self, param):
        t = LrpcVar(param, self.structs).param_type()
        n = param['name']
        return f'{t} {n}'

    def __returns_string(self, function):
        returns = self.__function_returns(function)
        returns_list = [LrpcVar(r, self.structs).return_type() for r in returns]

        if len(returns_list) == 0:
            return 'void'
        elif len (returns_list) == 1:
            return returns_list[0]
        else:
            return 'std::tuple<{}>'.format(', '.join(returns_list))

    def __function_params(self, function):
        return function.get('params', list())

    def __function_returns(self, function):
        return function.get('returns', list())

    def __write_include_guard(self):
        self.file('#pragma once')

    def __interface_has_strings(self):
        for f in self.interface['functions']:
            for p in self.__function_params(f) + self.__function_returns(f):
                var = LrpcVar(p, self.structs)
                if var.is_string() or var.is_array_of_strings():
                    return True

        return False

    def __interface_has_arrays(self):
        for f in self.interface['functions']:
            for p in self.__function_params(f) + self.__function_returns(f):
                var = LrpcVar(p, self.structs)
                if var.is_array():
                    return True

        return False

    def __write_includes(self):
        if self.__interface_has_strings():
            self.file('#include <etl/string_view.h>')
        if self.__interface_has_arrays():
            self.file('#include <etl/span.h>')
        self.file('#include <stdint.h>')
        self.file('#include "Decoder.hpp"')
        self.file('#include "TestDecoder_all.hpp"')

        self.file.newline()

    def __name(self):
        return self.interface['name']

    def __id(self):
        return self.interface['id']