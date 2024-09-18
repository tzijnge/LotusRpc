import struct
from copy import deepcopy
from typing import Any, List

from lrpc.core import LrpcDef, LrpcVar

class LrpcDecoder(object):
    def __init__(self, encoded: bytes, lrpc_def: LrpcDef) -> None:
        self.encoded: bytes = encoded
        self.start: int = 0
        self.lrpc_def: LrpcDef = lrpc_def

    def __decode_string(self, var: LrpcVar) -> str:
        if var.is_auto_string():
            return self.__decode_auto_string()
        else:
            return self.__decode_fixed_size_string(var)

    def __decode_fixed_size_string(self, var: LrpcVar) -> str:
        if len(self.encoded) < (var.string_size() + 1) :
            raise ValueError(f'Wrong string size (including string termination): expected {var.string_size() + 1}, got {len(self.encoded)}')

        s = self.__decode_string_from(var.string_size() + 1)
        self.start += var.string_size() + 1
        return s

    def __decode_auto_string(self) -> str:
        s = self.__decode_string_from(len(self.encoded) - self.start)
        self.start += len(s) + 1
        return s

    def __decode_string_from(self, max_len: int) -> str:
        try:
            end = self.encoded.index(b'\x00', self.start, self.start + max_len)
        except:
            raise ValueError(f'String not terminated: {self.encoded}')
        
        return self.encoded[self.start:end].decode('utf-8')

    def __decode_array_of_strings(self, var: LrpcVar) -> List[str]:
        decoded = list()
        if var.is_auto_string():
            for i in range(0, var.array_size()):
                decoded.append(self.__decode_auto_string())
        else:
            for i in range(0, var.array_size()):
                decoded.append(self.__decode_fixed_size_string(var))

        return decoded

    def __decode_array(self, var: LrpcVar) -> Any:
        decoded = list()
        for i in range(0, var.array_size()):
            contained_var = deepcopy(var)
            contained_var.raw['count'] = 1
            item = self.lrpc_decode(contained_var)
            decoded.append(item)
        
        return decoded

    def __decode_optional(self, var: LrpcVar) -> Any:
        has_value = self.__unpack('?')
        if has_value:
            contained_var = deepcopy(var)
            contained_var.raw['count'] = 1
            return self.lrpc_decode(contained_var)
        else:
            return None
        
    def __decode_struct(self, var: LrpcVar) -> Any:
        decoded = dict()
        s = self.lrpc_def.struct(var.base_type())
        for field in s.fields():
            decoded_field = self.lrpc_decode(field)
            decoded.update({field.name(): decoded_field})

        return decoded
    
    def __decode_enum(self, var: LrpcVar) -> Any:
        e = self.lrpc_def.enum(var.base_type())
        fields = e.fields()
        
        id = self.__unpack('B')

        for f in fields:
            if f.id() == id:
                return f.name()
            
        raise ValueError(f'Value {id} ({hex(id)}) is not valid for enum {var.base_type()}')

    def __unpack(self, format: str) -> Any:
        format = '<' + format
        unpacked = struct.unpack_from(format, self.encoded, offset = self.start)
        self.start += struct.calcsize(format)
        return unpacked[0]

    def lrpc_decode(self, var: LrpcVar) -> Any:
        if var.is_array_of_strings():
            return self.__decode_array_of_strings(var)

        if var.is_array():
            return self.__decode_array(var)

        if var.is_optional():
            return self.__decode_optional(var)

        if var.base_type_is_string():
            return self.__decode_string(var)

        if var.base_type_is_struct():
            return self.__decode_struct(var)

        if var.base_type_is_enum():
            return self.__decode_enum(var)

        return self.__unpack(var.pack_type())
    
def lrpc_decode(encoded: bytes, var: LrpcVar, lrpc_def: LrpcDef) -> Any:
    return LrpcDecoder(encoded, lrpc_def).lrpc_decode(var)