from LrpcVisitor import LrpcVisitor
from typing import Union

from LrpcConstantBase import LrpcConstantBase

class LrpcConstant(LrpcConstantBase):
    def __init__(self, raw) -> None:
        self.raw = raw
        self.__init_cpp_type()

    def __init_cpp_type(self):
        if "cppType" not in self.raw:
            if isinstance(self.value(), int):
                self.raw["cppType"] = "int32_t"
            if isinstance(self.value(), float):
                self.raw["cppType"] = "float"
            if isinstance(self.value(), bool):
                self.raw["cppType"] = "bool"
            if isinstance(self.value(), str):
                self.raw["cppType"] = "string"

    def accept(self, visitor: LrpcVisitor):
        visitor.visit_lrpc_constant(self)

    def name(self):
        return self.raw['name']

    def value(self):
        return self.raw['value']
    
    def cpp_type(self):
        return self.raw['cppType']
