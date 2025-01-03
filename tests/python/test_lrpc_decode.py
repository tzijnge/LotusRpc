import math
import struct
from os import path

import pytest
from lrpc.client import lrpc_decode
from lrpc.core import LrpcVar
from lrpc.utils import load_lrpc_def_from_url

definition_file = path.join(path.dirname(path.abspath(__file__)), "test_lrpc_encode_decode.lrpc.yaml")
lrpc_def = load_lrpc_def_from_url(definition_file, warnings_as_errors=False)


def test_decode_uint8_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint8_t"})

    assert lrpc_decode(b"\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\xFF", var, lrpc_def) == 255

    # decode with trailing byte
    assert lrpc_decode(b"\xFF\x00", var, lrpc_def) == 255

    with pytest.raises(struct.error):
        lrpc_decode(b"", var, lrpc_def)


def test_decode_int8_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int8_t"})

    assert lrpc_decode(b"\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\x7F", var, lrpc_def) == 127
    assert lrpc_decode(b"\xFF", var, lrpc_def) == -1
    assert lrpc_decode(b"\x80", var, lrpc_def) == -128


def test_decode_uint16_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint16_t"})

    assert lrpc_decode(b"\x00\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\xFF\xFF", var, lrpc_def) == 65535


def test_decode_int16_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int16_t"})

    assert lrpc_decode(b"\x00\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\xFF\x7F", var, lrpc_def) == 32767
    assert lrpc_decode(b"\xFF\xFF", var, lrpc_def) == -1
    assert lrpc_decode(b"\x00\x80", var, lrpc_def) == -32768


def test_decode_uint32_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint32_t"})

    assert lrpc_decode(b"\x00\x00\x00\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\xFF\xFF\xFF\xFF", var, lrpc_def) == (2**32) - 1


def test_decode_int32_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int32_t"})

    assert lrpc_decode(b"\x00\x00\x00\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\xFF\xFF\xFF\x7F", var, lrpc_def) == (2**31) - 1
    assert lrpc_decode(b"\xFF\xFF\xFF\xFF", var, lrpc_def) == -1
    assert lrpc_decode(b"\x00\x00\x00\x80", var, lrpc_def) == -(2**31)


def test_decode_uint64_t() -> None:
    var = LrpcVar({"name": "v1", "type": "uint64_t"})

    assert lrpc_decode(b"\x00\x00\x00\x00\x00\x00\x00\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF", var, lrpc_def) == (2**64) - 1


def test_decode_int64_t() -> None:
    var = LrpcVar({"name": "v1", "type": "int64_t"})

    assert lrpc_decode(b"\x00\x00\x00\x00\x00\x00\x00\x00", var, lrpc_def) == 0
    assert lrpc_decode(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F", var, lrpc_def) == (2**63) - 1
    assert lrpc_decode(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF", var, lrpc_def) == -1
    assert lrpc_decode(b"\x00\x00\x00\x00\x00\x00\x00\x80", var, lrpc_def) == -(2**63)


def test_decode_float() -> None:
    var = LrpcVar({"name": "v1", "type": "float"})

    assert lrpc_decode(b"\x00\x00\x00\x00", var, lrpc_def) == 0
    decoded = lrpc_decode(b"\x79\xE9\xF6\x42", var, lrpc_def)
    assert math.isclose(decoded, 123.456, abs_tol=0.00001)


def test_decode_double() -> None:
    var = LrpcVar({"name": "v1", "type": "double"})

    assert lrpc_decode(b"\x00\x00\x00\x00\x00\x00\x00\x00", var, lrpc_def) == 0
    v = lrpc_decode(b"\x77\xBE\x9F\x1A\x2F\xDD\x5E\x40", var, lrpc_def)
    assert math.isclose(float(v), 123.456)


def test_decode_bool() -> None:
    var = LrpcVar({"name": "v1", "type": "bool"})

    assert not lrpc_decode(b"\x00", var, lrpc_def)
    assert lrpc_decode(b"\x01", var, lrpc_def)
    assert lrpc_decode(b"\x02", var, lrpc_def)
    assert lrpc_decode(b"\xFF", var, lrpc_def)


def test_decode_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string"})

    assert lrpc_decode(b"test123\x00", var, lrpc_def) == "test123"

    # no string termination
    with pytest.raises(ValueError):
        lrpc_decode(b"test123", var, lrpc_def)

    # trailing bytes
    assert lrpc_decode(b"test123\x00\x00", var, lrpc_def) == "test123"
    assert lrpc_decode(b"test123\x00test345\x00", var, lrpc_def) == "test123"


def test_decode_fixed_size_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string_10"})

    assert lrpc_decode(b"test123\x00\x00\x00\x00", var, lrpc_def) == "test123"
    assert lrpc_decode(b"0123456789\x00", var, lrpc_def) == "0123456789"
    assert lrpc_decode(b"012\x00345\x00\x00\x00\x00", var, lrpc_def) == "012"
    assert lrpc_decode(b"012\x00345\x00\x00\x00a", var, lrpc_def) == "012"

    # trailing bytes
    assert lrpc_decode(b"0123456789\x00\x00", var, lrpc_def) == "0123456789"
    assert lrpc_decode(b"0123456789\x00\x01", var, lrpc_def) == "0123456789"

    # no string termination
    with pytest.raises(ValueError):
        lrpc_decode(b"01234567890", var, lrpc_def)

    # too short
    with pytest.raises(ValueError):
        lrpc_decode(b"012345678\x00", var, lrpc_def)

    # too long
    with pytest.raises(ValueError):
        lrpc_decode(b"01234567890\x00", var, lrpc_def)


def test_decode_array() -> None:
    var = LrpcVar({"name": "v1", "type": "uint8_t", "count": 4})

    assert lrpc_decode(b"\x01\x02\x03\x04", var, lrpc_def) == [1, 2, 3, 4]
    assert lrpc_decode(b"\x01\x02\x03\x04\x05", var, lrpc_def) == [1, 2, 3, 4]

    with pytest.raises(struct.error):
        lrpc_decode(b"\x01\x02\x03", var, lrpc_def)


def test_decode_array_of_fixed_size_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string_2", "count": 3})

    assert lrpc_decode(b"ab\x00cd\x00ef\x00", var, lrpc_def) == ["ab", "cd", "ef"]
    assert lrpc_decode(b"a\x00\x00cd\x00\x00\x00\x00", var, lrpc_def) == ["a", "cd", ""]
    assert lrpc_decode(b"ab\x00cd\x00ef\x00gh\x00", var, lrpc_def) == ["ab", "cd", "ef"]

    # last string not terminated
    with pytest.raises(ValueError):
        lrpc_decode(b"ab\x00cd", var, lrpc_def)

    # strings too long
    with pytest.raises(ValueError):
        lrpc_decode(b"abc\x00def\x00", var, lrpc_def)

    # one string in array
    with pytest.raises(ValueError):
        lrpc_decode(b"ab\x00", var, lrpc_def)


def test_decode_array_of_auto_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string", "count": 3})

    assert lrpc_decode(b"abcd\x00ef\x00\x00", var, lrpc_def) == ["abcd", "ef", ""]
    assert lrpc_decode(b"ab1\x00cd23\x00ef45\x00gh67\x00", var, lrpc_def) == [
        "ab1",
        "cd23",
        "ef45",
    ]

    # last string not terminated
    with pytest.raises(ValueError):
        lrpc_decode(b"abcd\x00ef", var, lrpc_def)

    # two strings in array
    with pytest.raises(ValueError):
        lrpc_decode(b"ab\x00cd\x00", var, lrpc_def)


def test_decode_optional() -> None:
    var = LrpcVar({"name": "v1", "type": "uint8_t", "count": "?"})

    assert lrpc_decode(b"\x00", var, lrpc_def) is None
    assert lrpc_decode(b"\x01\xAB", var, lrpc_def) == 0xAB
    assert lrpc_decode(b"\xFF\xAB", var, lrpc_def) == 0xAB
    assert lrpc_decode(b"\x01\x01\x01", var, lrpc_def) == 0x01

    with pytest.raises(struct.error):
        lrpc_decode(b"\x01", var, lrpc_def)


def test_decode_optional_fixed_size_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string_2", "count": "?"})

    assert lrpc_decode(b"\x00", var, lrpc_def) is None
    assert lrpc_decode(b"\x01ab\x00", var, lrpc_def) == "ab"

    # trailing bytes
    assert lrpc_decode(b"\x01ab\x00\x00", var, lrpc_def) == "ab"

    with pytest.raises(ValueError):
        lrpc_decode(b"\x01ab", var, lrpc_def)


def test_decode_optional_auto_string() -> None:
    var = LrpcVar({"name": "v1", "type": "string", "count": "?"})

    assert lrpc_decode(b"\x00", var, lrpc_def) is None
    assert lrpc_decode(b"\x01ab\x00", var, lrpc_def) == "ab"

    # trailing bytes
    assert lrpc_decode(b"\x01ab\x00\x00", var, lrpc_def) == "ab"

    with pytest.raises(ValueError):
        lrpc_decode(b"\x01ab", var, lrpc_def)

def test_decode_struct_not_in_def() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@not_in_def"})

    with pytest.raises(ValueError) as e:
        lrpc_decode(b"\xD7\x11\x7B\x01", var, lrpc_def)

    assert  "No struct not_in_def in LRPC definition" in str(e.value)

def test_decode_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct1"})

    assert lrpc_decode(b"\xD7\x11\x7B\x01", var, lrpc_def) == {
        "b": 123,
        "a": 4567,
        "c": True,
    }

    #  trailing bytes
    assert lrpc_decode(b"\xD7\x11\x7B\x01\x00", var, lrpc_def) == {
        "b": 123,
        "a": 4567,
        "c": True,
    }

    with pytest.raises(struct.error):
        lrpc_decode(b"\xD7\x11\x7B", var, lrpc_def)


def test_decode_optional_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct1", "count": "?"})

    assert lrpc_decode(b"\x00", var, lrpc_def) is None
    assert lrpc_decode(b"\x01\xD7\x11\x7B\x01", var, lrpc_def) == {
        "b": 123,
        "a": 4567,
        "c": True,
    }


def test_decode_nested_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct2"})

    assert lrpc_decode(b"\xD7\x11\x7B\x01", var, lrpc_def) == {"a": {"b": 123, "a": 4567, "c": True}}


def test_decode_enum() -> None:
    var = LrpcVar({"name": "v1", "type": "enum@MyEnum1"})

    assert lrpc_decode(b"\x00", var, lrpc_def) == "test1"
    assert lrpc_decode(b"\x37", var, lrpc_def) == "test2"

    with pytest.raises(ValueError):
        lrpc_decode(b"\x22", var, lrpc_def)


def test_decode_optional_enum() -> None:
    var = LrpcVar({"name": "v1", "type": "enum@MyEnum1", "count": "?"})

    assert lrpc_decode(b"\x00", var, lrpc_def) is None
    assert lrpc_decode(b"\x01\x37", var, lrpc_def) == "test2"


def test_decode_array_of_struct() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct2", "count": 2})

    decoded = lrpc_decode(b"\xD7\x11\x7B\x01\x11\x22\x33\x00", var, lrpc_def)

    assert len(decoded) == 2
    assert decoded[0] == {"a": {"b": 123, "a": 4567, "c": True}}
    assert decoded[1] == {"a": {"b": 51, "a": 8721, "c": False}}
