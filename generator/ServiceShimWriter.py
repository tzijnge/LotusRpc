from code_generation.code_generator import CppFile
from LrpcService import LrpcService

class ServiceShimWriter(object):
    def __init__(self, service, output):
        self.service = service
        self.file = CppFile(f'{output}/{self.service.name()}_ServiceShim.hpp')

    def write(self):        
        self.__write_include_guard()
        self.__write_includes()
        self.__write_shim()

    def __write_shim(self):
        with self.file.block(f'class {self.service.name()}ServiceShim : public lrpc::Service', ';'):
            self.file.label('public')
            self.file(f'uint32_t id() const override {{ return {self.service.id()}; }}')
            self.file.newline()

            with self.file.block('void decode(Reader &reader, Writer &writer) override'):
                self.file('auto messageId = reader.read_unchecked<uint8_t>();')
                self.file('((this)->*(functionShims.at(messageId)))(reader, writer);')
            
            self.file.newline()
            self.file.label('protected')
            for f in self.service.functions():
                self.__write_function_decl(f)

            self.file.newline()

            for f in self.service.functions():
                with self.file.block(f'void {f.name()}_shim(Reader &r, Writer &w)'):
                    self.__write_function_shim(f)

                self.file.newline()

            self.file.newline()
            self.file.label('private')
            with self.file.block('inline static const etl::array functionShims', ';'):
                for f in self.service.functions():
                    self.file(f'&{self.service.name()}ServiceShim::{f.name()}_shim,')

    def __write_function_shim(self, function):
        for p in function.params():
            n = p.name()
            t = p.read_type()
            self.file(f'const auto {n} = lrpc::read_unchecked<{t}>(r);')

        param_list = ', '.join(function.param_names())

        response = 'const auto response = ' if function.number_returns() != 0 else ''
        self.file(f'{response}{function.name()}({param_list});')

        returns = function.returns()
        if function.number_returns() == 1:
            t = returns[0].write_type()
            self.file(f'lrpc::write_unchecked<{t}>(w, response);')
        else:
            for i, r in enumerate(returns):
                t = r.write_type()
                self.file(f'lrpc::write_unchecked<{t}>(w, std::get<{i}>(response));')

    def __write_function_decl(self, function):
        name = function.name()
        params = self.__params_string(function)
        returns = self.__returns_string(function)
        self.file(f'virtual {returns} {name}({params}) = 0;')

    def __params_string(self, function):
        params_list = [self.__param_string(p) for p in function.params()]
        return ', '.join(params_list)

    def __param_string(self, param):
        t = param.param_type()
        n = param.name()
        return f'{t} {n}'

    def __returns_string(self, function):
        returns_list = [r.return_type() for r in function.returns()]

        if len(returns_list) == 0:
            return 'void'
        elif len (returns_list) == 1:
            return returns_list[0]
        else:
            return 'std::tuple<{}>'.format(', '.join(returns_list))

    def __write_include_guard(self):
        self.file('#pragma once')

    def __write_includes(self):
        self.file('#include "lrpc/Service.hpp"')
        self.file('#include "lrpc/EtlRwExtensions.hpp"')
        self.file(f'#include "{self.service.name()}.hpp"')

        self.file.newline()