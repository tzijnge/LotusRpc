from code_generation.code_generator import CppFile

class IncludeAllWriter(object):
    def __init__(self, definition, output):
        self.definition = definition
        self.output = output
        self.file = CppFile(f'{self.output}/{self.definition.name()}.hpp')

    def write(self):
        # write include file for every service, including enums, structs, stdint.h and required etl includes
        # write include all file that includes all service includes
        self.file('#pragma once')
        for s in self.definition.services():
            self.write_service_include(s)
            self.file(f'#include "{s.name()}.hpp"')


    def write_service_include(self, service):
        include_file = CppFile(f'{self.output}/{service.name()}.hpp')
        include_file('#pragma once')

        for i in service.required_includes():
            include_file(f'#include {i}')
