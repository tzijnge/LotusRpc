from typing import TypedDict, Union
from typing_extensions import NotRequired

from ..visitors import LrpcVisitor

CPP_TYPES: list[str] = [
    "uint8_t",
    "int8_t",
    "uint16_t",
    "int16_t",
    "uint32_t",
    "int32_t",
    "uint64_t",
    "int64_t",
    "float",
    "double",
    "bool",
    "string",
]


class LrpcConstantDict(TypedDict):
    name: str
    value: Union[int, float, bool, str]
    cppType: NotRequired[str]


class LrpcConstant:
    def __init__(self, raw: LrpcConstantDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "value" in raw

        self.__name: str = raw["name"]
        self.__value: Union[int, float, bool, str] = raw["value"]
        self.__cpp_type: str = self.__init_cpp_type(raw)

    def __init_cpp_type(self, raw: LrpcConstantDict) -> str:
        if "cppType" not in raw:
            if isinstance(self.value(), bool):
                return "bool"
            if isinstance(self.value(), int):
                return "int32_t"
            if isinstance(self.value(), float):
                return "float"
            if isinstance(self.value(), str):
                return "string"

            raise ValueError(f"Unable to infer cppType for LrpcConstant value: {self.value()}")

        cpp_type = raw["cppType"]
        if cpp_type in CPP_TYPES:
            return cpp_type

        raise ValueError(f"Invalid cppType for LrpcConstant {self.__name}: {cpp_type}")

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_constant(self)

    def name(self) -> str:
        return self.__name

    def value(self) -> Union[int, float, bool, str]:
        return self.__value

    def cpp_type(self) -> str:
        return self.__cpp_type
