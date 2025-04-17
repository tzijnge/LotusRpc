from copy import deepcopy
from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired

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
    count: NotRequired[Union[int, Literal["?"]]]


# pylint: disable = too-many-public-methods
class LrpcVar:
    def __init__(self, raw: LrpcVarDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "type" in raw and isinstance(raw["type"], str)

        self.__name = raw["name"]
        self.__type = raw["type"].replace("struct@", "").replace("enum@", "").strip("@")
        self.__base_type_is_struct = raw["type"].startswith("struct@")
        self.__base_type_is_enum = raw["type"].startswith("enum@")
        self.__base_type_is_custom = "@" in raw["type"]

        c = raw.get("count", 1)
        if isinstance(c, int):
            self.__is_optional = False
            self.__count = c
        else:
            self.__is_optional = True
            self.__count = 1

    def name(self) -> str:
        return self.__name

    def base_type(self) -> str:
        return self.__type

    def field_type(self) -> str:
        t = self.base_type()

        if self.is_auto_string():
            t = "etl::string_view"
        elif self.base_type_is_string():
            t = f"etl::string<{self.string_size()}>"

        if self.is_optional():
            return f"etl::optional<{t}>"

        if self.is_array():
            s = self.array_size()
            return f"etl::array<{t}, {s}>"

        return t

    def return_type(self) -> str:
        t = self.base_type()

        if self.is_auto_string():
            t = "etl::string_view"
        elif self.base_type_is_string():
            t = f"etl::string<{self.string_size()}>"

        if self.is_optional():
            return f"etl::optional<{t}>"

        if self.is_array():
            return f"etl::array<{t}, {self.array_size()}>"

        return t

    def param_type(self) -> str:
        if self.base_type_is_string():
            t = "etl::string_view"
        else:
            t = self.base_type()

        if self.is_array():
            return f"const etl::span<const {t}>&"

        if self.is_optional():
            return f"const etl::optional<{t}>&"

        if self.base_type_is_struct() or self.base_type_is_string():
            return f"const {t}&"

        return t

    def read_type(self) -> str:
        if self.base_type_is_string():
            if self.is_fixed_size_string():
                s = self.string_size()
                t = f"etl::string<{s}>"
            else:
                t = "etl::string_view"
        else:
            t = self.base_type()

        if self.is_array():
            return f"etl::array<{t}, {self.array_size()}>"

        if self.is_optional():
            return f"etl::optional<{t}>"

        return t

    def write_type(self) -> str:
        t = self.base_type()

        if self.is_auto_string():
            t = "etl::string_view"
        elif self.base_type_is_string():
            t = f"etl::string<{self.string_size()}>"

        if self.is_array():
            return f"etl::array<{t}, {self.array_size()}>"

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

    def is_struct(self) -> bool:
        if self.is_array():
            return False
        if self.is_optional():
            return False

        return self.base_type_is_struct()

    def is_optional(self) -> bool:
        return self.__is_optional

    def is_array(self) -> bool:
        return self.__count > 1

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
        if self.is_auto_string():
            return -1

        return int(self.base_type().strip("string_"))

    def array_size(self) -> int:
        if self.is_optional():
            return -1

        return self.__count

    def pack_type(self) -> str:
        if self.base_type_is_struct():
            raise TypeError("Pack type is not defined for LrpcVar of type struct")
        if self.is_optional():
            raise TypeError("Pack type is not defined for LrpcVar of type optional")
        if self.base_type_is_string():
            raise TypeError("Pack type is not defined for LrpcVar of type string")
        if self.is_array():
            raise TypeError("Pack type is not defined for LrpcVar of type array")

        if self.base_type_is_enum():
            return "B"

        return PACK_TYPES[self.base_type()]

    def contained(self) -> "LrpcVar":
        contained_item = deepcopy(self)
        # pylint: disable=protected-access, unused-private-member
        contained_item.__is_optional = False
        contained_item.__count = 1
        return contained_item
