import struct
from typing import Any

from ..core import LrpcDef, LrpcVar


def __check_string(value: Any, var: LrpcVar) -> None:
    if not isinstance(value, str):
        raise TypeError(f"Type error for {var.name()}: expected string, but got {type(value)}")


def __encode_string(s: str, var: LrpcVar) -> bytes:
    if var.is_fixed_size_string():
        if len(s) > var.string_size():
            raise ValueError(f"String length error for {var.name()}: max length {var.string_size()}, but got {len(s)} ")
        return struct.pack(f"<{var.string_size()}s", s.encode("utf-8")) + b"\x00"

    return struct.pack(f"<{len(s)}s", s.encode("utf-8")) + b"\x00"


def __encode_optional(value: Any, var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    if value is None:
        return struct.pack("<?", False)

    return struct.pack("<?", True) + lrpc_encode(value, var.contained(), lrpc_def)


def __check_struct(value: Any, var: LrpcVar, lrpc_def: LrpcDef) -> None:
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


def __encode_struct(value: Any, var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    encoded = b""
    s = lrpc_def.struct(var.base_type())

    if not s:
        raise ValueError(f"Type {var.base_type()} not found in LRPC definition")

    for field in s.fields():
        v = value[field.name()]
        encoded += lrpc_encode(v, field, lrpc_def)

    return encoded


def __check_array(value: Any, var: LrpcVar) -> None:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"Type error for {var.name()}: expected list or tuple, but got {type(value)}")

    if len(value) != var.array_size():
        raise ValueError(f"Length error for {var.name()}: expected {var.array_size()}, but gor {len(value)}")


def __encode_array(value: list[Any], var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    encoded = b""
    for i in range(0, var.array_size()):
        item = lrpc_encode(value[i], var.contained(), lrpc_def)
        encoded += item

    return encoded


def __check_enum_field_id(value: Any, var: LrpcVar, lrpc_def: LrpcDef) -> None:
    e = lrpc_def.enum(var.base_type())
    field_id = e.field_id(value)
    if field_id is None:
        raise ValueError(f"Enum error for {var.name()} of type {e.name()}: {value} is not a valid enum value")


def __encode_basic_type(pack_type: str, value: Any) -> bytes:
    return struct.pack(f"<{pack_type}", value)


def lrpc_encode(value: Any, var: LrpcVar, lrpc_def: LrpcDef) -> bytes:
    if var.is_array():
        __check_array(value, var)
        return __encode_array(value, var, lrpc_def)

    if var.is_optional():
        return __encode_optional(value, var, lrpc_def)

    if var.base_type_is_string():
        __check_string(value, var)
        return __encode_string(value, var)

    if var.base_type_is_struct():
        __check_struct(value, var, lrpc_def)
        return __encode_struct(value, var, lrpc_def)

    if var.base_type_is_enum():
        __check_enum_field_id(value, var, lrpc_def)
        e = lrpc_def.enum(var.base_type())
        field_id = e.field_id(value)
        return __encode_basic_type(var.pack_type(), field_id)

    return __encode_basic_type(var.pack_type(), value)
