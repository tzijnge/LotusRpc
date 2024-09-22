from typing import TypedDict, NotRequired

from lrpc import LrpcVisitor


class LrpcConstantDict(TypedDict):
    name: str
    value: int | float | bool | str
    cppType: NotRequired[str]


class LrpcConstant:
    def __init__(self, raw: LrpcConstantDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "value" in raw

        self.__name: str = raw["name"]
        self.__value: int | float | bool | str = raw["value"]
        self.__cpp_type: str = self.__init_cpp_type(raw)

    def __init_cpp_type(self, raw: LrpcConstantDict) -> str:
        if "cppType" in raw:
            return raw["cppType"]

        if isinstance(self.value(), bool):
            return "bool"
        if isinstance(self.value(), int):
            return "int32_t"
        if isinstance(self.value(), float):
            return "float"
        if isinstance(self.value(), str):
            return "string"

        assert False, f"Invalid LrpcConstant type: {self.value()}"

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_constant(self)

    def name(self) -> str:
        return self.__name

    def value(self) -> int | float | bool | str:
        return self.__value

    def cpp_type(self) -> str:
        return self.__cpp_type
