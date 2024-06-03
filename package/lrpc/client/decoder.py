import struct
from copy import deepcopy
from typing import Any, Optional, List

from lrpc.core import LrpcDef, LrpcVar

def __decode_string(encoded: bytes, var: LrpcVar) -> str:
    if var.is_auto_string():
        return __decode_auto_string(encoded)
    else:
        return __decode_fixed_size_string(encoded, var)

def __decode_fixed_size_string(encoded: bytes, var: LrpcVar) -> str:
    if len(encoded) != var.string_size() + 1:
        raise ValueError(f'Wrong string size (including string termination): expected {var.string_size() + 1}, got {len(encoded)}')
    
    parts = encoded.split(b'\x00')

    if len(parts) == 1:
        raise ValueError(f'String not terminated: {encoded}')

    return parts[0].decode('utf-8')

def __decode_auto_string(encoded: bytes) -> str:
    parts = encoded.split(b'\x00')

    if (len(parts) == 1):
        raise ValueError(f'String not terminated: {encoded}')
    
    if (len(parts) != 2):
        raise ValueError(f'Invalid string: {encoded}')
    
    return parts[0].decode('utf-8')


def __decode_array_of_strings(encoded: bytes, var: LrpcVar) -> List[str]:
    decoded = list()
    if var.is_auto_string():
        start = 0
        for i in range(0, var.array_size()):
            end = encoded.index(b'\x00', start) + 1
            decoded.append(__decode_auto_string(encoded[start:end]))
            start = end
    else:
        for i in range(0, var.array_size()):
            start = i * (var.string_size() + 1)
            end = start + var.string_size() + 1
            decoded.append(__decode_fixed_size_string(encoded[start:end], var))

    if end != len(encoded):
        raise ValueError('Trailing data for array')

    if len(decoded) != var.array_size():
        raise ValueError(f'Wrong array size. Expected {var.array_size()}, but got {len(decoded)}')

    return decoded



def __decode_optional(encoded: bytes, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> Any:
    has_value = struct.unpack_from('<?', buffer=encoded, offset = 0)[0]
    if has_value:
        contained_var = deepcopy(var)
        contained_var.raw['count'] = 1
        return lrpc_decode(encoded[1:], contained_var, lrpc_def)
    else:
        return None
    
# def __decode_struct(encoded: bytes, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> Any:
#     decoded = dict()
#     s = lrpc_def.struct(var.base_type())
#     for field in s.fields():
#         decoded.update(field.name(), )
#         encoded += lrpc_decode(encoded, field, lrpc_def)

#     return encoded

def lrpc_decode(encoded: bytes, var: LrpcVar, lrpc_def: Optional[LrpcDef] = None) -> Any:
    if var.is_array_of_strings():
        return __decode_array_of_strings(encoded, var)

    if var.is_array():
        f = f'<{var.array_size()}{var.pack_type()}'
        a =  struct.unpack(f, encoded)
        return list(a)

    if var.is_optional():
        return __decode_optional(encoded, var, lrpc_def)

    if var.base_type_is_string():
        return __decode_string(encoded, var)

    # if var.base_type_is_struct():
    #     return __encode_struct(value, var, lrpc_def)

    # if var.base_type_is_enum():
    #     e = lrpc_def.enum(var.base_type())
    #     return struct.pack('<B', e.field_id(value))

    decoded = struct.unpack(f'<{var.pack_type()}', encoded)
    return decoded[0]