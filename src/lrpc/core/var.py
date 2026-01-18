from copy import deepcopy
from typing import Final, Literal

from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict

PACK_TYPES: dict[str, str] = {
    "uint8_t": "B",
    "int8_t": "b",
    "uint16_t": "H",
    "int16_t": "h",
    "uint32_t": "I",
    "int32_t": "i",
    "uint64_t": "Q",
    "int64_t": "q",
    "float": "f",
    "double": "d",
    "bool": "?",
}


class LrpcVarDict(TypedDict):
    name: str
    type: str
    count: NotRequired[int | Literal["?"]]


# pylint: disable=invalid-name
LrpcVarValidator = TypeAdapter(LrpcVarDict)


# pylint: disable = too-many-public-methods
class LrpcVar:
    ETL_STRING_VIEW: Final = "etl::string_view"

    def __init__(self, raw: LrpcVarDict) -> None:
        LrpcVarValidator.validate_python(raw, strict=True, extra="forbid")

        self.__name = raw["name"]
        self.__type = raw["type"].replace("struct@", "").replace("enum@", "").strip("@")
        self.__base_type_is_struct = raw["type"].startswith("struct@")
        self.__base_type_is_enum = raw["type"].startswith("enum@")
        self.__base_type_is_custom = "@" in raw["type"]

        c = raw.get("count", 1)
        if isinstance(c, int):
            self._is_optional = False
            self._count = c
        else:
            self._is_optional = True
            self._count = 1

    def name(self) -> str:
        return self.__name

    def base_type(self) -> str:
        return self.__type

    def field_type(self) -> str:
        if self.base_type_is_string():
            t = LrpcVar.ETL_STRING_VIEW
        elif self.base_type_is_bytearray():
            t = "etl::span<const uint8_t>"
        else:
            t = self.base_type()

        if self.is_optional():
            return f"etl::optional<{t}>"

        if self.is_array():
            return f"etl::array<{t}, {self.array_size()}>"

        return t

    def return_type(self) -> str:
        if self.base_type_is_string():
            t = LrpcVar.ETL_STRING_VIEW
        elif self.base_type_is_bytearray():
            t = "etl::span<const uint8_t>"
        else:
            t = self.base_type()

        if self.is_optional():
            return f"etl::optional<{t}>"

        if self.is_array():
            return f"etl::span<const {t}>"

        return t

    def param_type(self) -> str:
        if self.base_type_is_string():
            t = LrpcVar.ETL_STRING_VIEW
        elif self.base_type_is_bytearray():
            t = "etl::span<const uint8_t>"
        else:
            t = self.base_type()

        if self.is_optional():
            return f"etl::optional<{t}>"

        if self.is_array():
            return f"etl::span<const {t}>"

        if self.base_type_is_struct():
            return f"const {t}&"

        return t

    def rw_type(self, namespace: str | None = None) -> str:
        if self.base_type_is_string():
            t = "lrpc::string_n" if self.is_fixed_size_string() else "lrpc::string_auto"
        elif self.base_type_is_bytearray():
            t = "lrpc::bytearray"
        elif self.base_type_is_custom() and namespace is not None:
            t = f"{namespace}::{self.base_type()}"
        else:
            t = self.base_type()

        if self.is_array():
            return f"lrpc::array_n<{t}>"

        if self.is_optional():
            return f"etl::optional<{t}>"

        return t

    def base_type_is_custom(self) -> bool:
        return self.__base_type_is_custom

    def base_type_is_struct(self) -> bool:
        return self.__base_type_is_struct

    def base_type_is_enum(self) -> bool:
        return self.__base_type_is_enum

    def base_type_is_integral(self) -> bool:
        return self.base_type() in [
            "uint8_t",
            "uint16_t",
            "uint32_t",
            "uint64_t",
            "int8_t",
            "int16_t",
            "int32_t",
            "int64_t",
        ]

    def base_type_is_float(self) -> bool:
        return self.base_type() in ["float", "double"]

    def base_type_is_bool(self) -> bool:
        return self.base_type() == "bool"

    def base_type_is_string(self) -> bool:
        return self.base_type().startswith("string")

    def base_type_is_bytearray(self) -> bool:
        return self.base_type() == "bytearray"

    def is_struct(self) -> bool:
        if self.is_array():
            return False
        if self.is_optional():
            return False

        return self.base_type_is_struct()

    def is_optional(self) -> bool:
        return self._is_optional

    def is_array(self) -> bool:
        return self._count > 1

    def is_array_of_strings(self) -> bool:
        return self.is_array() and self.base_type_is_string()

    def is_string(self) -> bool:
        if self.is_array():
            return False

        if self.is_optional():
            return False

        return self.base_type_is_string()

    def is_auto_string(self) -> bool:
        return self.base_type() == "string"

    def is_fixed_size_string(self) -> bool:
        return self.base_type_is_string() and not self.is_auto_string()

    def string_size(self) -> int:
        if not self.is_fixed_size_string():
            return -1

        return int(self.base_type().strip("string_"))

    def array_size(self) -> int:
        if self.is_optional():
            return -1

        return self._count

    def pack_type(self) -> str:
        message = "Pack type is not defined for LrpcVar of type {}"
        if self.base_type_is_struct():
            raise TypeError(message.format("struct"))
        if self.is_optional():
            raise TypeError(message.format("optional"))
        if self.base_type_is_string():
            raise TypeError(message.format("string"))
        if self.base_type_is_bytearray():
            raise TypeError(message.format("bytearray"))
        if self.is_array():
            raise TypeError(message.format("array"))

        if self.base_type_is_enum():
            return "B"

        return PACK_TYPES[self.base_type()]

    def contained(self) -> "LrpcVar":
        contained_item = deepcopy(self)
        # pylint: disable=protected-access, unused-private-member
        contained_item._is_optional = False  # noqa: SLF001
        contained_item._count = 1  # noqa: SLF001
        return contained_item
