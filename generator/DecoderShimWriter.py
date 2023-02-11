from code_generation.code_generator import CppFile
from LrpcVar import LrpcVar
from LrpcFun import LrpcFun

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
        f = LrpcFun(function, self.structs)

        for p in f.params():
            n = p.name()
            t = p.read_type()
            if p.is_array():
                s = p.array_size()
                self.file(f'const auto {n} = etl::read_unchecked<{t}, {s}>(r);')
            else:
                self.file(f'const auto {n} = etl::read_unchecked<{t}>(r);')

        param_list = ', '.join(f.param_names())

        response = 'const auto response = ' if f.number_returns() != 0 else ''
        self.file(f'{response}{f.name()}({param_list});')

        returns = f.returns()
        if f.number_returns() == 1:
            t = returns[0].write_type()
            self.file(f'etl::write_unchecked<{t}>(w, response);')
        else:
            for i, r in enumerate(returns):
                t = r.write_type()
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
        t = param.param_type()
        n = param.name()
        return f'{t} {n}'

    def __returns_string(self, function):
        returns = self.__function_returns(function)
        returns_list = [r.return_type() for r in returns]

        if len(returns_list) == 0:
            return 'void'
        elif len (returns_list) == 1:
            return returns_list[0]
        else:
            return 'std::tuple<{}>'.format(', '.join(returns_list))

    def __function_params(self, function):
        return LrpcFun(function, self.structs).params()

    def __function_returns(self, function):
        return LrpcFun(function, self.structs).returns()

    def __write_include_guard(self):
        self.file('#pragma once')

    def required_includes(self):
        includes = set()
        for f in self.interface['functions']:
            func = LrpcFun(f, self.structs)
            includes.update(func.required_includes())

        return includes

    def __write_includes(self):
        for i in self.required_includes():
            self.file(f'#include {i}')

        self.file('#include <stdint.h>')
        self.file('#include "Decoder.hpp"')
        self.file('#include "TestDecoder_all.hpp"')

        self.file.newline()

    def __name(self):
        return self.interface['name']

    def __id(self):
        return self.interface['id']