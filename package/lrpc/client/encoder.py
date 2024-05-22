import struct
from copy import deepcopy
from typing import Any, Optional

from lrpc.core import LrpcDef, LrpcVar

def __encode_string(s: str, var: LrpcVar) -> bytes:
    if var.is_fixed_size_string():
        return struct.pack(f'<{var.string_size()}s', s.encode('utf-8')) + b'\x00'
    else:
        return struct.pack(f'<{len(s)}s', s.encode('utf-8')) + b'\x00'

def __encode_array_of_strings(value, var: LrpcVar) -> bytes:
    encoded = b''
    for s in value:
        encoded += __encode_string(s, var)
    return encoded

def __encode_optional(value, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> bytes:
    if value is None:
        return struct.pack('<?', False)
    else:
        contained_var = deepcopy(var)
        contained_var.raw['count'] = 1
        return struct.pack('<?', True) + lrpc_encode(value, contained_var, lrpc_def)
    
def __encode_struct(value, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> bytes:
    encoded = b''
    s = lrpc_def.struct(var.base_type())
    for field in s.fields():
        v = value[field.name()]
        encoded += lrpc_encode(v, field, lrpc_def)

    return encoded

def lrpc_encode(value: Any, var: LrpcVar, lrpc_def: Optional[LrpcDef] = None) -> bytes:
    if var.is_array_of_strings():
        return __encode_array_of_strings(value, var)

    if var.is_array():
        f = f'<{var.array_size()}{var.pack_type()}'
        return struct.pack(f, *value)

    if var.is_optional():
        return __encode_optional(value, var, lrpc_def)

    if var.base_type_is_string():
        return __encode_string(value, var)

    if var.base_type_is_struct():
        return __encode_struct(value, var, lrpc_def)

    if var.base_type_is_enum():
        e = lrpc_def.enum(var.base_type())
        return struct.pack('<B', e.field_id(value))

    return struct.pack(f'<{var.pack_type()}', value)
