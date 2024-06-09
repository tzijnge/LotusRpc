from lrpc.core import LrpcVar, LrpcDef
import pytest
import struct
from lrpc.client import lrpc_decode
import math

lrpc_def = LrpcDef.load('package/lrpc/tests/test_lrpc_encode.lrpc.yaml')

def test_decode_uint8_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint8_t' })

    assert lrpc_decode(b'\x00', var) == 0
    assert lrpc_decode(b'\xFF', var) == 255

    # decode with trailing byte
    assert lrpc_decode(b'\xFF\x00', var) == 255

    with pytest.raises(struct.error):
        lrpc_decode(b'', var)

def test_decode_int8_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int8_t' })

    assert lrpc_decode(b'\x00', var) == 0
    assert lrpc_decode(b'\x7F', var) == 127
    assert lrpc_decode(b'\xFF', var) == -1
    assert lrpc_decode(b'\x80', var) == -128

def test_decode_uint16_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint16_t' })

    assert lrpc_decode(b'\x00\x00', var) == 0
    assert lrpc_decode(b'\xFF\xFF', var) == 65535

def test_decode_int16_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int16_t' })

    assert lrpc_decode(b'\x00\x00', var) == 0
    assert lrpc_decode(b'\xFF\x7F', var) == 32767
    assert lrpc_decode(b'\xFF\xFF', var) == -1
    assert lrpc_decode(b'\x00\x80', var) == -32768

def test_decode_uint32_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint32_t' })

    assert lrpc_decode(b'\x00\x00\x00\x00', var) == 0
    assert lrpc_decode(b'\xFF\xFF\xFF\xFF', var) == (2**32)-1

def test_decode_int32_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int32_t' })

    assert lrpc_decode(b'\x00\x00\x00\x00', var) == 0
    assert lrpc_decode(b'\xFF\xFF\xFF\x7F', var) == (2**31)-1
    assert lrpc_decode(b'\xFF\xFF\xFF\xFF', var) == -1
    assert lrpc_decode(b'\x00\x00\x00\x80', var) == -(2**31)

def test_decode_uint64_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint64_t' })

    assert lrpc_decode(b'\x00\x00\x00\x00\x00\x00\x00\x00', var) == 0
    assert lrpc_decode(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF', var) == (2**64)-1

def test_decode_int64_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int64_t' })

    assert lrpc_decode(b'\x00\x00\x00\x00\x00\x00\x00\x00', var) == 0
    assert lrpc_decode(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F', var) == (2**63)-1
    assert lrpc_decode(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF', var) == -1
    assert lrpc_decode(b'\x00\x00\x00\x00\x00\x00\x00\x80', var) == -(2**63)

def test_decode_float():
    var = LrpcVar({ 'name': 'v1', 'type': 'float' })

    assert lrpc_decode(b'\x00\x00\x00\x00', var) == 0
    decoded = lrpc_decode(b'\x79\xE9\xF6\x42', var)
    assert math.isclose(decoded, 123.456, abs_tol=0.00001)

def test_decode_double():
    var = LrpcVar({ 'name': 'v1', 'type': 'double' })

    assert lrpc_decode(b'\x00\x00\x00\x00\x00\x00\x00\x00', var) == 0
    assert lrpc_decode(b'\x77\xBE\x9F\x1A\x2F\xDD\x5E\x40', var) == 123.456

def test_decode_bool():
    var = LrpcVar({ 'name': 'v1', 'type': 'bool' })

    assert lrpc_decode(b'\x00', var) == False
    assert lrpc_decode(b'\x01', var) == True
    assert lrpc_decode(b'\x02', var) == True
    assert lrpc_decode(b'\xFF', var) == True

def test_decode_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string' })

    assert lrpc_decode(b'test123\x00', var) == 'test123'

    # no string termination
    with pytest.raises(ValueError):
        lrpc_decode(b'test123', var)

    # trailing bytes
    assert lrpc_decode(b'test123\x00\x00', var) == 'test123'
    assert lrpc_decode(b'test123\x00test345\x00', var) == 'test123'

def test_decode_fixed_size_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string_10' })

    assert lrpc_decode(b'test123\x00\x00\x00\x00', var) == 'test123'
    assert lrpc_decode(b'0123456789\x00', var) == '0123456789'
    assert lrpc_decode(b'012\x00345\x00\x00\x00\x00', var) == '012'
    assert lrpc_decode(b'012\x00345\x00\x00\x00a', var) == '012'

    # trailing bytes
    assert lrpc_decode(b'0123456789\x00\x00', var) == '0123456789'
    assert lrpc_decode(b'0123456789\x00\x01', var) == '0123456789'

    # no string termination
    with pytest.raises(ValueError):
        lrpc_decode(b'01234567890', var)

    # too short
    with pytest.raises(ValueError):
        lrpc_decode(b'012345678\x00', var)

    # too long
    with pytest.raises(ValueError):
        lrpc_decode(b'01234567890\x00', var)

def test_decode_array():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint8_t', 'count': 4 })

    assert lrpc_decode(b'\x01\x02\x03\x04', var) == [1, 2, 3, 4]
    assert lrpc_decode(b'\x01\x02\x03\x04\x05', var) == [1, 2, 3, 4]

    with pytest.raises(struct.error):
        lrpc_decode(b'\x01\x02\x03', var)

def test_decode_array_of_fixed_size_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string_2', 'count': 2 })

    assert lrpc_decode(b'ab\x00cd\x00', var) == ['ab', 'cd']
    assert lrpc_decode(b'a\x00\x00cd\x00', var) == ['a', 'cd']
    assert lrpc_decode(b'ab\x00cd\x00ef\x00', var) == ['ab', 'cd']

    # last string not terminated
    with pytest.raises(ValueError):
        lrpc_decode(b'ab\x00cd', var)

    # strings too long
    with pytest.raises(ValueError):
        lrpc_decode(b'abc\x00def\x00', var)

    # one string in array
    with pytest.raises(ValueError):
        lrpc_decode(b'ab\x00', var)

def test_decode_array_of_auto_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string', 'count': 3 })

    assert lrpc_decode(b'abcd\x00ef\x00\x00', var) == ['abcd', 'ef', '']
    assert lrpc_decode(b'ab1\x00cd23\x00ef45\x00gh67\x00', var) == ['ab1', 'cd23', 'ef45']

    # last string not terminated
    with pytest.raises(ValueError):
        lrpc_decode(b'abcd\x00ef', var)

    # two strings in array
    with pytest.raises(ValueError):
        lrpc_decode(b'ab\x00cd\x00', var)

def test_decode_optional():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint8_t', 'count': '?' })

    assert lrpc_decode(b'\x00', var) == None
    assert lrpc_decode(b'\x01\xAB', var) == 0xAB
    assert lrpc_decode(b'\xFF\xAB', var) == 0xAB
    assert lrpc_decode(b'\x01\x01\x01', var) == 0x01

    with pytest.raises(struct.error):
        lrpc_decode(b'\x01', var)

def test_decode_optional_fixed_size_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string_2', 'count': '?' })

    assert lrpc_decode(b'\x00', var) == None
    assert lrpc_decode(b'\x01ab\x00', var) == 'ab'

    # trailing bytes
    assert lrpc_decode(b'\x01ab\x00\x00', var) == 'ab'

    with pytest.raises(ValueError):
        lrpc_decode(b'\x01ab', var)

def test_decode_optional_auto_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string', 'count': '?' })

    assert lrpc_decode(b'\x00', var) == None
    assert lrpc_decode(b'\x01ab\x00', var) == 'ab'

    # trailing bytes
    assert lrpc_decode(b'\x01ab\x00\x00', var) == 'ab'

    with pytest.raises(ValueError):
        lrpc_decode(b'\x01ab', var)

#def test_decode_struct():
#    var = LrpcVar({ 'name': 'v1', 'type': '@MyStruct1', 'base_type_is_struct': True})

#    decoded = lrpc_decode(b'\xD7\x11\x7B\x01', var, lrpc_def)
#    assert decoded == {'b': 123, 'a': 4567, 'c': True}

# def test_decode_optional_struct():
#     lrpc_def = __load_lrpc_def()

#     var = LrpcVar({ 'name': 'v1', 'type': '@MyStruct1', 'base_type_is_struct': True, 'count': '?'})

#     encoded = lrpc_decode(None, var, lrpc_def)
#     assert encoded == b'\x00'
#     encoded = lrpc_decode({'b': 123, 'a': 4567, 'c': True}, var, lrpc_def)
#     assert encoded == b'\x01\xD7\x11\x7B\x01'

# def test_decode_nested_struct():
#     lrpc_def = __load_lrpc_def()

#     var = LrpcVar({ 'name': 'v1', 'type': '@MyStruct2', 'base_type_is_struct': True})

#     encoded = lrpc_decode({'a': {'b': 123, 'a': 4567, 'c': True}}, var, lrpc_def)
#     assert encoded == b'\xD7\x11\x7B\x01'

# def test_decode_enum():
#     lrpc_def = __load_lrpc_def()

#     var = LrpcVar({ 'name': 'v1', 'type': '@MyEnum1', 'base_type_is_enum': True})

#     encoded = lrpc_decode('test1', var, lrpc_def)
#     assert encoded == b'\x00'
#     encoded = lrpc_decode('test2', var, lrpc_def)
#     assert encoded == b'\x37'

#     with pytest.raises(struct.error):
#         lrpc_decode('test3', var, lrpc_def)

# def test_decode_optional_enum():
#     lrpc_def = __load_lrpc_def()

#     var = LrpcVar({ 'name': 'v1', 'type': '@MyEnum1', 'base_type_is_enum': True, 'count': '?'})

#     encoded = lrpc_decode(None, var, lrpc_def)
#     assert encoded == b'\x00'
#     encoded = lrpc_decode('test2', var, lrpc_def)
#     assert encoded == b'\x01\x37'


# todo: array of structs and array of strings
