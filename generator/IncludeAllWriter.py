from code_generation.code_generator import CppFile
from pathlib import Path

class IncludeAllWriter(object):
    def __init__(self, rpc_name, structs, enums, output):
        self.structs = structs
        self.enums = enums

        rpc_name = Path(rpc_name).stem
        rpc_name = rpc_name.replace('.lrpc', '')
        self.file = CppFile(f'{output}/{rpc_name}_all.hpp')

    def write(self):        
        self.file('#pragma once')
        for t in self.structs + self.enums:
            name = t['name']
            self.file(f'#include "{name}.hpp"')