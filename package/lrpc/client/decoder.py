import struct
from copy import deepcopy
from typing import Any, Optional

from lrpc.core import LrpcDef, LrpcVar

def __decode_string(encoded: bytes, var: LrpcVar) -> str:
    s = encoded.split(b'\x00')[0]
    return s.decode('utf-8')

def __decode_array_of_strings(encoded, var: LrpcVar) -> bytes:
    parts = encoded.split(b'\x00')

    a = parts[-1]
    if parts[-1] != b'':
        raise ValueError('Last string in array is not terminated')
    
    parts.pop() # final string termination causes empty part

    if len(parts) != var.array_size():
        raise ValueError(f'Wrong array size. Expected {var.array_size()}, but got {len(parts)}')
    
    if not var.is_auto_string():
        for p in parts:
            if len(p) != var.string_size():
                raise ValueError(f'Wrong string size. Expected {var.string_size()}, but got {len(p)}')

    return [s.decode('utf-8') for s in parts]


# def __encode_optional(value, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> bytes:
#     if value is None:
#         return struct.pack('<?', False)
#     else:
#         contained_var = deepcopy(var)
#         contained_var.raw['count'] = 1
#         return struct.pack('<?', True) + lrpc_encode(value, contained_var, lrpc_def)
    
# def __encode_struct(value, var: LrpcVar, lrpc_def: Optional[LrpcDef]) -> bytes:
#     encoded = b''
#     s = lrpc_def.struct(var.base_type())
#     for field in s.fields():
#         v = value[field.name()]
#         encoded += lrpc_encode(v, field, lrpc_def)

#     return encoded

def lrpc_decode(encoded: bytes, var: LrpcVar, lrpc_def: Optional[LrpcDef] = None) -> Any:
    if var.is_array_of_strings():
        return __decode_array_of_strings(encoded, var)

    if var.is_array():
        f = f'<{var.array_size()}{var.pack_type()}'
        a =  struct.unpack(f, encoded)
        return list(a)

    # if var.is_optional():
    #     return __encode_optional(value, var, lrpc_def)

    if var.base_type_is_string():
        return __decode_string(encoded, var)

    # if var.base_type_is_struct():
    #     return __encode_struct(value, var, lrpc_def)

    # if var.base_type_is_enum():
    #     e = lrpc_def.enum(var.base_type())
    #     return struct.pack('<B', e.field_id(value))

    decoded = struct.unpack(f'<{var.pack_type()}', encoded)
    return decoded[0]