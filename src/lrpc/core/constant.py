from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict

from lrpc.visitors import LrpcVisitor

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
    "bytearray",
]


class LrpcConstantDict(TypedDict):
    name: str
    value: int | float | bool | str
    cppType: NotRequired[str]


# pylint: disable=invalid-name
LrpcConstantValidator = TypeAdapter(LrpcConstantDict)


class LrpcConstant:
    def __init__(self, raw: LrpcConstantDict) -> None:
        LrpcConstantValidator.validate_python(raw, strict=True, extra="forbid")

        self.__name: str = raw["name"]
        self.__value = self.__init_value(raw)
        self.__cpp_type = self.__init_cpp_type(raw)

    @staticmethod
    def __init_value(raw: LrpcConstantDict) -> int | float | bool | str | bytes:
        value = raw["value"]
        if "cppType" in raw and raw["cppType"] == "bytearray":
            if not isinstance(value, str):
                raise ValueError("Constant with cppType 'bytearray' must have a string value")
            return bytes.fromhex(value)

        return value

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

            raise ValueError(f"Unable to infer cppType for LrpcConstant value: {self.value()!s}")

        cpp_type = raw["cppType"]
        if cpp_type in CPP_TYPES:
            return cpp_type

        raise ValueError(f"Invalid cppType for LrpcConstant {self.__name}: {cpp_type}")

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_constant(self)

    def name(self) -> str:
        return self.__name

    def value(self) -> int | float | bool | str | bytes:
        return self.__value

    def cpp_type(self) -> str:
        return self.__cpp_type
