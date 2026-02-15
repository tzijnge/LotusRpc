import struct
from typing import Any, cast

from lrpc.core import LrpcDef, LrpcVar
from lrpc.types.lrpc_type import LrpcResponseBasicTypeValidator, LrpcResponseType


# pylint: disable = too-few-public-methods
class LrpcDecoder:
    def __init__(self, encoded: bytes, lrpc_def: LrpcDef) -> None:
        self.encoded: bytes = encoded
        self.start: int = 0
        self.lrpc_def: LrpcDef = lrpc_def

    def _decode_bytearray(self) -> bytes:
        ba_size = self._unpack_uint8_t()
        remaining = len(self.encoded) - self.start
        if remaining < ba_size:
            raise ValueError(f"Incomplete bytearray: expected {ba_size} bytes but got {remaining}")

        return self._unpack_bytes(ba_size)

    def _decode_string(self, var: LrpcVar) -> str:
        if var.is_auto_string():
            return self._decode_auto_string()

        return self._decode_fixed_size_string(var)

    def _decode_fixed_size_string(self, var: LrpcVar) -> str:
        if len(self.encoded) < (var.string_size() + 1):
            raise ValueError(
                "Wrong string size (including string termination): "
                f"expected {var.string_size() + 1}, got {len(self.encoded)}",
            )

        s = self._decode_string_from(var.string_size() + 1)
        self.start += var.string_size() + 1
        return s

    def _decode_auto_string(self) -> str:
        s = self._decode_string_from(len(self.encoded) - self.start)
        self.start += len(s) + 1
        return s

    def _decode_string_from(self, max_len: int) -> str:
        try:
            end = self.encoded.index(b"\x00", self.start, self.start + max_len)
        except Exception as e:
            raise ValueError(f"String not terminated: {self.encoded!r}") from e

        return self.encoded[self.start : end].decode("utf-8")

    def _decode_array_of_strings(self, var: LrpcVar) -> list[str]:
        decoded = []
        if var.is_auto_string():
            decoded.extend([self._decode_auto_string() for _ in range(var.array_size())])
        else:
            decoded.extend([self._decode_fixed_size_string(var) for _ in range(var.array_size())])

        return decoded

    def _decode_array(self, var: LrpcVar) -> list[LrpcResponseType]:
        decoded = []
        for _ in range(var.array_size()):
            item = self.lrpc_decode(var.contained())
            decoded.append(item)

        return decoded

    def _decode_optional(self, var: LrpcVar) -> LrpcResponseType | None:
        has_value = self._unpack("?")
        if has_value is True:
            return self.lrpc_decode(var.contained())

        return None

    def _decode_struct(self, var: LrpcVar) -> LrpcResponseType:
        decoded = {}
        s = self.lrpc_def.struct(var.base_type())

        if not s:
            raise ValueError(f"Type {var.base_type()} not found in LRPC definition")

        for field in s.fields():
            decoded_field = self.lrpc_decode(field)
            decoded.update({field.name(): decoded_field})

        return decoded

    def _decode_enum(self, var: LrpcVar) -> str:
        e = self.lrpc_def.enum(var.base_type())

        if not e:
            raise ValueError(f"Type {var.base_type()} not found in LRPC definition")

        fields = e.fields()

        identifier = self._unpack_uint8_t()

        for f in fields:
            if f.id() == identifier:
                return f.name()

        raise ValueError(f"Value {identifier} ({hex(identifier)}) is not valid for enum {var.base_type()}")

    def _unpack_bytes(self, size: int) -> bytes:
        return cast(bytes, self._unpack(f"{size}s"))

    def _unpack_uint8_t(self) -> int:
        return cast(int, self._unpack("B"))

    def _unpack(self, pack_format: str) -> LrpcResponseType:
        pack_format = "<" + pack_format
        unpacked = struct.unpack_from(pack_format, self.encoded, offset=self.start)
        self.start += struct.calcsize(pack_format)

        return LrpcResponseBasicTypeValidator.validate_python(unpacked[0])

    # pylint: disable = too-many-return-statements
    def lrpc_decode(self, var: LrpcVar) -> LrpcResponseType:  # noqa: PLR0911
        if var.is_array_of_strings():
            return self._decode_array_of_strings(var)

        if var.is_array():
            return self._decode_array(var)

        if var.is_optional():
            return self._decode_optional(var)

        if var.base_type_is_bytearray():
            return self._decode_bytearray()

        if var.base_type_is_string():
            return self._decode_string(var)

        if var.base_type_is_struct():
            return self._decode_struct(var)

        if var.base_type_is_enum():
            return self._decode_enum(var)

        return self._unpack(var.pack_type())

    def remaining(self) -> int:
        return len(self.encoded) - self.start


def lrpc_decode(encoded: bytes, var: LrpcVar, lrpc_def: LrpcDef) -> Any:
    return LrpcDecoder(encoded, lrpc_def).lrpc_decode(var)
