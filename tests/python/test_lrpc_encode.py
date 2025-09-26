import struct
from os import path

import pytest
from lrpc.client import lrpc_encode
from lrpc.core import LrpcVar
from lrpc.utils import load_lrpc_def_from_url
from lrpc.types import LrpcType

definition_file = path.join(path.dirname(path.abspath(__file__)), "test_lrpc_encode_decode.lrpc.yaml")
lrpc_def = load_lrpc_def_from_url(definition_file, warnings_as_errors=False)


def encode_var(value: LrpcType, var: LrpcVar) -> bytes:
    return lrpc_encode(value, var, lrpc_def)


def test_encode_uint8_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint8_t"})

    assert encode_var(0, var) == b"\x00"
    assert encode_var(255, var) == b"\xff"

    with pytest.raises(struct.error):
        encode_var(-1, var)

    with pytest.raises(struct.error):
        encode_var(256, var)

    with pytest.raises(TypeError):
        encode_var({123}, var)


def test_encode_int8_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int8_t"})

    assert encode_var(0, var) == b"\x00"
    assert encode_var(127, var) == b"\x7f"
    assert encode_var(-1, var) == b"\xff"
    assert encode_var(-128, var) == b"\x80"

    with pytest.raises(struct.error):
        encode_var(128, var)

    with pytest.raises(struct.error):
        encode_var(-129, var)

    with pytest.raises(TypeError):
        encode_var((123, 124), var)


def test_encode_uint16_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint16_t"})

    assert encode_var(0, var) == b"\x00\x00"
    assert encode_var(65535, var) == b"\xff\xff"

    with pytest.raises(struct.error):
        encode_var(-1, var)

    with pytest.raises(struct.error):
        encode_var(65536, var)

    with pytest.raises(TypeError):
        encode_var([123], var)


def test_encode_int16_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int16_t"})

    assert encode_var(0, var) == b"\x00\x00"
    assert encode_var(32767, var) == b"\xff\x7f"
    assert encode_var(-1, var) == b"\xff\xff"
    assert encode_var(-32768, var) == b"\x00\x80"

    with pytest.raises(struct.error):
        encode_var(32768, var)

    with pytest.raises(struct.error):
        encode_var(-32769, var)

    with pytest.raises(TypeError):
        encode_var(None, var)


def test_encode_uint32_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint32_t"})

    assert encode_var(0, var) == b"\x00\x00\x00\x00"
    assert encode_var((2**32) - 1, var) == b"\xff\xff\xff\xff"

    with pytest.raises(struct.error):
        encode_var(-1, var)

    with pytest.raises(struct.error):
        encode_var(2**32, var)

    with pytest.raises(struct.error):
        encode_var("123", var)


def test_encode_int32_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int32_t"})

    assert encode_var(0, var) == b"\x00\x00\x00\x00"
    assert encode_var((2**31) - 1, var) == b"\xff\xff\xff\x7f"
    assert encode_var(-1, var) == b"\xff\xff\xff\xff"
    assert encode_var(-(2**31), var) == b"\x00\x00\x00\x80"

    with pytest.raises(struct.error):
        encode_var(2**31, var)

    with pytest.raises(struct.error):
        encode_var(-(2**31) - 1, var)


def test_encode_uint64_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint64_t"})

    assert encode_var(0, var) == b"\x00\x00\x00\x00\x00\x00\x00\x00"
    assert encode_var((2**64) - 1, var) == b"\xff\xff\xff\xff\xff\xff\xff\xff"

    with pytest.raises(struct.error):
        encode_var(-1, var)

    with pytest.raises(struct.error):
        encode_var(2**64, var)


def test_encode_int64_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int64_t"})

    assert encode_var(0, var) == b"\x00\x00\x00\x00\x00\x00\x00\x00"
    assert encode_var((2**63) - 1, var) == b"\xff\xff\xff\xff\xff\xff\xff\x7f"
    assert encode_var(-1, var) == b"\xff\xff\xff\xff\xff\xff\xff\xff"
    assert encode_var(-(2**63), var) == b"\x00\x00\x00\x00\x00\x00\x00\x80"

    with pytest.raises(struct.error):
        encode_var(2**63, var)

    with pytest.raises(struct.error):
        encode_var(-(2**63) - 1, var)


def test_encode_float() -> None:
    var = LrpcVar({"name": "v1", "type": "float"})

    assert encode_var(0, var) == b"\x00\x00\x00\x00"
    assert encode_var(123.456, var) == b"\x79\xe9\xf6\x42"

    with pytest.raises(OverflowError):
        encode_var(3.5e38, var)

    with pytest.raises(OverflowError):
        encode_var(-3.5e38, var)


def test_encode_double() -> None:
    var = LrpcVar({"name": "v1", "type": "double"})

    assert encode_var(0, var) == b"\x00\x00\x00\x00\x00\x00\x00\x00"
    assert encode_var(123.456, var) == b"\x77\xbe\x9f\x1a\x2f\xdd\x5e\x40"

    # no overflows here. Python converts too large value to 'inf'


def test_encode_bool() -> None:
    var = LrpcVar({"name": "v1", "type": "bool"})

    assert encode_var(False, var) == b"\x00"
    assert encode_var(True, var) == b"\x01"


def test_encode_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string"})

    assert encode_var("test123", var) == b"test123\x00"

    with pytest.raises(TypeError):
        encode_var(["test123"], var)


def test_encode_fixed_size_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string_10"})

    assert encode_var("test123", var) == b"test123\x00\x00\x00\x00"

    with pytest.raises(ValueError):
        encode_var("0123456789_", var)


def test_encode_array() -> None:
    var = LrpcVar({"name": "v1", "type": "uint8_t", "count": 4})

    assert encode_var([1, 2, 3, 4], var) == b"\x01\x02\x03\x04"

    with pytest.raises(TypeError):
        encode_var(0, var)

    with pytest.raises(ValueError):
        encode_var([1, 2, 3], var)

    with pytest.raises(ValueError):
        encode_var([1, 2, 3, 4, 5], var)


def test_encode_optional() -> None:
    var = LrpcVar({"name": "v1", "type": "uint8_t", "count": "?"})

    assert encode_var(None, var) == b"\x00"
    assert encode_var(0xAB, var) == b"\x01\xab"


def test_encode_optional_fixed_size_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string_2", "count": "?"})

    assert encode_var(None, var) == b"\x00"
    assert encode_var("ab", var) == b"\x01ab\x00"


def test_encode_optional_auto_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string", "count": "?"})

    assert encode_var(None, var) == b"\x00"
    assert encode_var("ab", var) == b"\x01ab\x00"


def test_encode_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct1"})

    encoded = encode_var({"b": 123, "a": 4567, "c": True}, var)
    assert encoded == b"\xd7\x11\x7b\x01"

    with pytest.raises(TypeError):
        encode_var((123, 4567, True), var)

    with pytest.raises(ValueError):
        encode_var({1: 123, "a": 4567, "c": True}, var)

    with pytest.raises(ValueError):
        encode_var({"b": 123, "a": 4567}, var)

    with pytest.raises(ValueError):
        encode_var({"b": 123, "a": 4567, "c": True, "d": False}, var)


def test_encode_optional_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct1", "count": "?"})

    encoded = encode_var(None, var)
    assert encoded == b"\x00"
    encoded = encode_var({"b": 123, "a": 4567, "c": True}, var)
    assert encoded == b"\x01\xd7\x11\x7b\x01"


def test_encode_nested_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct2"})

    encoded = encode_var({"a": {"b": 123, "a": 4567, "c": True}}, var)
    assert encoded == b"\xd7\x11\x7b\x01"


def test_encode_unknown_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@UnknownStruct"})

    with pytest.raises(ValueError):
        encode_var({"b": 123, "a": 4567}, var)


def test_encode_enum() -> None:
    var = LrpcVar({"name": "v1", "type": "enum@MyEnum1"})

    encoded = encode_var("test1", var)
    assert encoded == b"\x00"
    encoded = encode_var("test2", var)
    assert encoded == b"\x37"

    with pytest.raises(ValueError):
        encode_var("test3", var)


def test_encode_optional_enum() -> None:
    var = LrpcVar({"name": "v1", "type": "enum@MyEnum1", "count": "?"})

    encoded = encode_var(None, var)
    assert encoded == b"\x00"
    encoded = encode_var("test2", var)
    assert encoded == b"\x01\x37"


def test_encode_enum_invalid_input() -> None:
    var = LrpcVar({"name": "v1", "type": "enum@MyEnum1"})

    encoded = encode_var("test1", var)
    assert encoded == b"\x00"
    encoded = encode_var("test2", var)
    assert encoded == b"\x37"

    with pytest.raises(TypeError):
        encode_var(123, var)


def test_encode_array_of_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct2", "count": 2})

    array_of_structs = [{"a": {"b": 123, "a": 4567, "c": True}}, {"a": {"b": 51, "a": 8721, "c": False}}]
    encoded = encode_var(array_of_structs, var)

    assert encoded == b"\xd7\x11\x7b\x01\x11\x22\x33\x00"


def test_encode_array_of_fixed_size_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string_2", "count": 3})

    assert encode_var(["ab", "cd", "ef"], var) == b"ab\x00cd\x00ef\x00"
    assert encode_var(["a", "cd", ""], var) == b"a\x00\x00cd\x00\x00\x00\x00"


def test_encode_array_of_auto_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string", "count": 3})

    assert encode_var(["abcd", "ef", ""], var) == b"abcd\x00ef\x00\x00"
    assert encode_var(["ab1", "cd23", "ef45"], var) == b"ab1\x00cd23\x00ef45\x00"
