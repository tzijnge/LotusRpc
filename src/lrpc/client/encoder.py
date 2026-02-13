import struct
from typing import Final

from lrpc.core import LrpcDef, LrpcVar
from lrpc.types import LrpcBasicType, LrpcType
from lrpc.types.lrpc_type import LrpcBuffer


def __check_bytearray(value: LrpcType, var: LrpcVar) -> memoryview:
    # Max size that can be expressed in the size field. This does not
    # mean that a message of this size always fits in the transmit buffer
    bytearray_max_size: Final = 255

    if not isinstance(value, LrpcBuffer):
        raise TypeError(f"Type error for {var.name()}: expected bytearray, but got {type(value)}")

    mv = memoryview(value)

    if mv.nbytes > bytearray_max_size:
        raise ValueError(f"Bytearray of length {mv.nbytes} exceeds max length of {bytearray_max_size}")

    return mv


def __check_string(value: LrpcType, var: LrpcVar) -> str:
    if not isinstance(value, str):
        raise TypeError(f"Type error for {var.name()}: expected string, but got {type(value)}")

    return value


def __encode_bytearray(ba: memoryview) -> bytes:
    return struct.pack("<B", ba.nbytes) + ba.tobytes()


def __encode_string(s: str, var: LrpcVar) -> bytes:
    if var.is_fixed_size_string():
        if len(s) > var.string_size():
            raise ValueError(f"String length error for {var.name()}: max length {var.string_size()}, but got {len(s)} ")
        return struct.pack(f"<{var.string_size()}s", s.encode("utf-8")) + b"\x00"

    return struct.pack(f"<{len(s)}s", s.encode("utf-8")) + b"\x00"


def __encode_optional(value: LrpcType | None, var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    if value is None:
        return struct.pack("<?", False)  # noqa: FBT003

    return struct.pack("<?", True) + lrpc_encode(value, var.contained(), lrpc_def)  # noqa: FBT003


def __check_struct(value: LrpcType, var: LrpcVar, lrpc_def: LrpcDef) -> dict[str, LrpcType]:
    if not isinstance(value, dict):
        raise TypeError(f"Type error for {var.name()}: expected dict, but got {type(value)}")

    s = lrpc_def.struct(var.base_type())
    required_fields = [f.name() for f in s.fields()]
    given_fields = list(value.keys())

    missing_fields = set(required_fields) - set(given_fields)
    unknown_fields = set(given_fields) - set(required_fields)

    if len(missing_fields) != 0:
        raise ValueError(f"Missing fields for {var.name()}: {missing_fields}")

    if len(unknown_fields) != 0:
        raise ValueError(f"Unknown fields for {var.name()}: {unknown_fields}")

    return value


def __encode_struct(value: dict[str, LrpcType], var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    encoded = b""
    s = lrpc_def.struct(var.base_type())

    for field in s.fields():
        v = value[field.name()]
        encoded += lrpc_encode(v, field, lrpc_def)

    return encoded


def __check_array(value: LrpcType, var: LrpcVar) -> list[LrpcType]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"Type error for {var.name()}: expected list or tuple, but got {type(value)}")

    if len(value) != var.array_size():
        raise ValueError(f"Length error for {var.name()}: expected {var.array_size()}, but gor {len(value)}")

    return list(value)


def __encode_array(value: list[LrpcType], var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    encoded = b""
    for i in range(var.array_size()):
        item = lrpc_encode(value[i], var.contained(), lrpc_def)
        encoded += item

    return encoded


def __check_enum_field_id(value: LrpcType, var: LrpcVar, lrpc_def: LrpcDef) -> str:
    if not isinstance(value, str):
        raise TypeError(f"Type error for {var.name()}: expected str, but got {type(value)}")

    e = lrpc_def.enum(var.base_type())
    field_id = e.field_id(value)
    if field_id is None:
        raise ValueError(f"Enum error for {var.name()} of type {e.name()}: {value} is not a valid enum value")

    return value


def __encode_basic_type(pack_type: str, value: LrpcBasicType) -> bytes:
    return struct.pack(f"<{pack_type}", value)


# pylint: disable = too-many-return-statements
def lrpc_encode(value: LrpcType, var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    if var.is_array():
        value = __check_array(value, var)
        return __encode_array(value, var, lrpc_def)

    if var.is_optional():
        return __encode_optional(value, var, lrpc_def)

    if var.base_type_is_bytearray():
        value = __check_bytearray(value, var)
        return __encode_bytearray(value)

    if var.base_type_is_string():
        value = __check_string(value, var)
        return __encode_string(value, var)

    if var.base_type_is_struct():
        value = __check_struct(value, var, lrpc_def)
        return __encode_struct(value, var, lrpc_def)

    if var.base_type_is_enum():
        value = __check_enum_field_id(value, var, lrpc_def)
        e = lrpc_def.enum(var.base_type())
        field_id = e.field_id(value)
        if field_id is None:
            raise ValueError(f"{value} is not a field in enum {var.name()}")
        return __encode_basic_type(var.pack_type(), field_id)

    if not isinstance(value, (bool, int, float, str)):
        raise TypeError(f"Type error for {var.name()}: expected bool, int, float or str, but got {type(value)}")

    return __encode_basic_type(var.pack_type(), value)
