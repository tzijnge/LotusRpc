import struct
from typing import Any

from lrpc.core import LrpcDef, LrpcVar
from lrpc.types.lrpc_type import LrpcBasicTypeValidator, LrpcType


# pylint: disable = too-few-public-methods
class LrpcDecoder:
    def __init__(self, encoded: bytes, lrpc_def: LrpcDef) -> None:
        self.encoded: bytes = encoded
        self.start: int = 0
        self.lrpc_def: LrpcDef = lrpc_def

    def __decode_bytearray(self) -> bytes:
        ba_size = self.__unpack("B")
        remaining = len(self.encoded) - self.start
        if remaining < ba_size:
            raise ValueError(f"Incomplete bytearray: expected {ba_size} bytes but got {remaining}")

        ba = self.encoded[self.start : self.start + ba_size]
        self.start += ba_size
        return ba

    def __decode_string(self, var: LrpcVar) -> str:
        if var.is_auto_string():
            return self.__decode_auto_string()

        return self.__decode_fixed_size_string(var)

    def __decode_fixed_size_string(self, var: LrpcVar) -> str:
        if len(self.encoded) < (var.string_size() + 1):
            raise ValueError(
                "Wrong string size (including string termination): "
                f"expected {var.string_size() + 1}, got {len(self.encoded)}",
            )

        s = self.__decode_string_from(var.string_size() + 1)
        self.start += var.string_size() + 1
        return s

    def __decode_auto_string(self) -> str:
        s = self.__decode_string_from(len(self.encoded) - self.start)
        self.start += len(s) + 1
        return s

    def __decode_string_from(self, max_len: int) -> str:
        try:
            end = self.encoded.index(b"\x00", self.start, self.start + max_len)
        except Exception as e:
            raise ValueError(f"String not terminated: {self.encoded!r}") from e

        return self.encoded[self.start : end].decode("utf-8")

    def __decode_array_of_strings(self, var: LrpcVar) -> list[str]:
        decoded = []
        if var.is_auto_string():
            decoded.extend([self.__decode_auto_string() for _ in range(var.array_size())])
        else:
            decoded.extend([self.__decode_fixed_size_string(var) for _ in range(var.array_size())])

        return decoded

    def __decode_array(self, var: LrpcVar) -> list[LrpcType]:
        decoded = []
        for _ in range(var.array_size()):
            item = self.lrpc_decode(var.contained())
            decoded.append(item)

        return decoded

    def __decode_optional(self, var: LrpcVar) -> LrpcType | None:
        has_value = self.__unpack("?")
        if has_value:
            return self.lrpc_decode(var.contained())

        return None

    def __decode_struct(self, var: LrpcVar) -> LrpcType:
        decoded = {}
        s = self.lrpc_def.struct(var.base_type())

        if not s:
            raise ValueError(f"Type {var.base_type()} not found in LRPC definition")

        for field in s.fields():
            decoded_field = self.lrpc_decode(field)
            decoded.update({field.name(): decoded_field})

        return decoded

    def __decode_enum(self, var: LrpcVar) -> str:
        e = self.lrpc_def.enum(var.base_type())

        if not e:
            raise ValueError(f"Type {var.base_type()} not found in LRPC definition")

        fields = e.fields()

        identifier = self.__unpack(var.pack_type())

        for f in fields:
            if f.id() == identifier:
                return f.name()

        raise ValueError(f"Value {identifier} ({hex(identifier)}) is not valid for enum {var.base_type()}")

    def __unpack(self, pack_format: str) -> LrpcType:
        pack_format = "<" + pack_format
        unpacked = struct.unpack_from(pack_format, self.encoded, offset=self.start)
        self.start += struct.calcsize(pack_format)

        return LrpcBasicTypeValidator.validate_python(unpacked[0])

    # pylint: disable = too-many-return-statements
    def lrpc_decode(self, var: LrpcVar) -> LrpcType:
        if var.is_array_of_strings():
            return self.__decode_array_of_strings(var)

        if var.is_array():
            return self.__decode_array(var)

        if var.is_optional():
            return self.__decode_optional(var)

        if var.base_type_is_bytearray():
            return self.__decode_bytearray()

        if var.base_type_is_string():
            return self.__decode_string(var)

        if var.base_type_is_struct():
            return self.__decode_struct(var)

        if var.base_type_is_enum():
            return self.__decode_enum(var)

        return self.__unpack(var.pack_type())

    def remaining(self) -> int:
        return len(self.encoded) - self.start


def lrpc_decode(encoded: bytes, var: LrpcVar, lrpc_def: LrpcDef) -> Any:
    return LrpcDecoder(encoded, lrpc_def).lrpc_decode(var)
