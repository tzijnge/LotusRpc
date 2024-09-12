import struct
from copy import deepcopy
from typing import Any, Optional, List

from lrpc.core import LrpcDef, LrpcVar


def __encode_string(s: str, var: LrpcVar) -> bytes:
    if var.is_fixed_size_string():
        if len(s) > var.string_size():
            raise ValueError(
                f"String length error for {var.name()}: max length {var.string_size()}, but got {len(s)} "
            )
        return struct.pack(f"<{var.string_size()}s", s.encode("utf-8")) + b"\x00"

    return struct.pack(f"<{len(s)}s", s.encode("utf-8")) + b"\x00"


def __encode_optional(value: Any, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> bytes:
    if value is None:
        return struct.pack("<?", False)

    contained_var = deepcopy(var)
    contained_var.raw["count"] = 1
    return struct.pack("<?", True) + lrpc_encode(value, contained_var, lrpc_def)


def __encode_struct(value: Any, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> bytes:
    encoded = b""
    s = lrpc_def.struct(var.base_type())

    if not s:
        raise ValueError(f"Type {var.base_type()} not found in LRPC definition")

    for field in s.fields():
        v = value[field.name()]
        encoded += lrpc_encode(v, field, lrpc_def)

    return encoded


def __encode_array(
    value: List[Any], var: LrpcVar, lrpc_def: Optional[LrpcDef]
) -> bytes:
    encoded = b""
    for i in range(0, var.array_size()):
        contained_var = deepcopy(var)
        contained_var.raw["count"] = 1
        item = lrpc_encode(value[i], contained_var, lrpc_def)
        encoded += item

    return encoded


def lrpc_encode(value: Any, var: LrpcVar, lrpc_def: Optional[LrpcDef] = None) -> bytes:
    if var.is_array():
        if not isinstance(value, list):
            raise TypeError(
                f"Type error for {var.name()}: expected array/list, but got {type(value)}"
            )

        if len(value) != var.array_size():
            raise ValueError(
                f"Length error for {var.name()}: expected {var.array_size()}, but gor {len(value)}"
            )

        return __encode_array(value, var, lrpc_def)

    if var.is_optional():
        return __encode_optional(value, var, lrpc_def)

    if var.base_type_is_string():
        if not isinstance(value, str):
            raise TypeError(
                f"Type error for {var.name()}: expected string, but got {type(value)}"
            )

        return __encode_string(value, var)

    if var.base_type_is_struct():
        if not isinstance(value, dict):
            raise TypeError(
                f"Type error for {var.name()}: expected dict, but got {type(value)}"
            )

        s = lrpc_def.struct(var.base_type())
        required_fields = [f.name() for f in s.fields()]
        given_fields = list(value.keys())

        missing_fields = set(required_fields) - set(given_fields)
        unknown_fields = set(given_fields) - set(required_fields)

        if len(missing_fields) != 0:
            raise ValueError(f"Missing fields for {var.name()}: {missing_fields}")

        if len(unknown_fields) != 0:
            raise ValueError(f"Unknown fields for {var.name()}: {unknown_fields}")

        return __encode_struct(value, var, lrpc_def)

    if var.base_type_is_enum():
        e = lrpc_def.enum(var.base_type())
        field_id = e.field_id(value)
        if field_id is None:
            raise ValueError(
                f"Enum error for {var.name()} of type {e.name()}: {value} is not a valid enum value"
            )
        return struct.pack("<B", field_id)

    return struct.pack(f"<{var.pack_type()}", value)
