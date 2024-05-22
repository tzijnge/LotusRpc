from lrpc.core import LrpcVar, LrpcDef
from typing import Any, Optional
import pytest
import struct
import yaml
from importlib import resources
from lrpc import schema as lrpc_schema
import jsonschema
from lrpc.validation import SemanticAnalyzer
from lrpc.client import lrpc_encode

def __load_lrpc_def():
    schema_url = resources.files(lrpc_schema) / 'lotusrpc-schema.json'
    definition_url = 'package/lrpc/tests/test_lrpc_encode.lrpc.yaml'

    with open(definition_url, 'rt') as rpc_def:
        with open(schema_url, 'rt') as schema_file:
            definition = yaml.safe_load(rpc_def)
            schema = yaml.safe_load(schema_file)
            jsonschema.validate(definition, schema)

            lrpc_def = LrpcDef(definition)
            sa = SemanticAnalyzer(lrpc_def)
            sa.analyze()

            assert len(sa.errors) == 0
            assert len(sa.warnings) == 0

            return lrpc_def

def test_encode_uint8_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint8_t' })

    assert lrpc_encode(0, var) == b'\x00'
    assert lrpc_encode(255, var) == b'\xFF'

    with pytest.raises(struct.error):
        lrpc_encode(-1, var)

    with pytest.raises(struct.error):
        lrpc_encode(256, var)

def test_encode_int8_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int8_t' })

    assert lrpc_encode(0, var) == b'\x00'
    assert lrpc_encode(127, var) == b'\x7F'
    assert lrpc_encode(-1, var) == b'\xFF'
    assert lrpc_encode(-128, var) == b'\x80'

    with pytest.raises(struct.error):
        lrpc_encode(128, var)

    with pytest.raises(struct.error):
        lrpc_encode(-129, var)

def test_encode_uint16_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint16_t' })

    assert lrpc_encode(0, var) == b'\x00\x00'
    assert lrpc_encode(65535, var) == b'\xFF\xFF'

    with pytest.raises(struct.error):
        lrpc_encode(-1, var)

    with pytest.raises(struct.error):
        lrpc_encode(65536, var)

def test_encode_int16_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int16_t' })

    assert lrpc_encode(0, var) == b'\x00\x00'
    assert lrpc_encode(32767, var) == b'\xFF\x7F'
    assert lrpc_encode(-1, var) == b'\xFF\xFF'
    assert lrpc_encode(-32768, var) == b'\x00\x80'

    with pytest.raises(struct.error):
        lrpc_encode(32768, var)

    with pytest.raises(struct.error):
        lrpc_encode(-32769, var)

def test_encode_uint32_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint32_t' })

    assert lrpc_encode(0, var) == b'\x00\x00\x00\x00'
    assert lrpc_encode((2**32)-1, var) == b'\xFF\xFF\xFF\xFF'

    with pytest.raises(struct.error):
        lrpc_encode(-1, var)

    with pytest.raises(struct.error):
        lrpc_encode(2**32, var)

def test_encode_int32_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int32_t' })

    assert lrpc_encode(0, var) == b'\x00\x00\x00\x00'
    assert lrpc_encode((2**31)-1, var) == b'\xFF\xFF\xFF\x7F'
    assert lrpc_encode(-1, var) == b'\xFF\xFF\xFF\xFF'
    assert lrpc_encode(-(2**31), var) == b'\x00\x00\x00\x80'

    with pytest.raises(struct.error):
        lrpc_encode(2**31, var)

    with pytest.raises(struct.error):
        lrpc_encode(-(2**31)-1, var)

def test_encode_uint64_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint64_t' })

    assert lrpc_encode(0, var) == b'\x00\x00\x00\x00\x00\x00\x00\x00'
    assert lrpc_encode((2**64)-1, var) == b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'

    with pytest.raises(struct.error):
        lrpc_encode(-1, var)

    with pytest.raises(struct.error):
        lrpc_encode(2**64, var)

def test_encode_int64_t():
    var = LrpcVar({ 'name': 'v1', 'type': 'int64_t' })

    assert lrpc_encode(0, var) == b'\x00\x00\x00\x00\x00\x00\x00\x00'
    assert lrpc_encode((2**63)-1, var) == b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F'
    assert lrpc_encode(-1, var) == b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
    assert lrpc_encode(-(2**63), var) == b'\x00\x00\x00\x00\x00\x00\x00\x80'

    with pytest.raises(struct.error):
        lrpc_encode(2**63, var)

    with pytest.raises(struct.error):
        lrpc_encode(-(2**63)-1, var)

def test_encode_float():
    var = LrpcVar({ 'name': 'v1', 'type': 'float' })

    assert lrpc_encode(0, var) == b'\x00\x00\x00\x00'
    assert lrpc_encode(123.456, var) == b'\x79\xE9\xF6\x42'

    with pytest.raises(OverflowError):
        lrpc_encode(3.5e38, var)

    with pytest.raises(OverflowError):
        lrpc_encode(-3.5e38, var)

def test_encode_double():
    var = LrpcVar({ 'name': 'v1', 'type': 'double' })

    assert lrpc_encode(0, var) == b'\x00\x00\x00\x00\x00\x00\x00\x00'
    assert lrpc_encode(123.456, var) == b'\x77\xBE\x9F\x1A\x2F\xDD\x5E\x40'

    # no overflows here. Python converts too large value to 'inf'

def test_encode_bool():
    var = LrpcVar({ 'name': 'v1', 'type': 'bool' })

    assert lrpc_encode(False, var) == b'\x00'
    assert lrpc_encode(True, var) == b'\x01'

def test_encode_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string' })

    assert lrpc_encode('test123', var) == b'test123\x00'

def test_encode_fixed_size_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string_10' })

    assert lrpc_encode('test123', var) == b'test123\x00\x00\x00\x00'
    assert lrpc_encode('0123456789_', var) == b'0123456789\x00'

def test_encode_array():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint8_t', 'count': 4 })

    assert lrpc_encode([1, 2, 3, 4], var) == b'\x01\x02\x03\x04'

    with pytest.raises(struct.error):
        lrpc_encode([1, 2, 3], var)

    with pytest.raises(struct.error):
        lrpc_encode([1, 2, 3, 4, 5], var)

def test_encode_array_of_fixed_size_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string_2', 'count': 2 })

    assert lrpc_encode(['ab', 'cd'], var) == b'ab\x00cd\x00'

def test_encode_array_of_auto_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string', 'count': 2 })

    assert lrpc_encode(['abcd', 'ef'], var) == b'abcd\x00ef\x00'

def test_encode_optional():
    var = LrpcVar({ 'name': 'v1', 'type': 'uint8_t', 'count': '?' })

    assert lrpc_encode(None, var) == b'\x00'
    assert lrpc_encode(0xAB, var) == b'\x01\xAB'

def test_encode_optional_fixed_size_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string_2', 'count': '?' })

    assert lrpc_encode(None, var) == b'\x00'
    assert lrpc_encode('ab', var) == b'\x01ab\x00'

def test_encode_optional_auto_string():
    var = LrpcVar({ 'name': 'v1', 'type': 'string', 'count': '?' })

    assert lrpc_encode(None, var) == b'\x00'
    assert lrpc_encode('ab', var) == b'\x01ab\x00'

def test_encode_struct():
    lrpc_def = __load_lrpc_def()

    var = LrpcVar({ 'name': 'v1', 'type': '@MyStruct1', 'base_type_is_struct': True})

    encoded = lrpc_encode({'b': 123, 'a': 4567, 'c': True}, var, lrpc_def)
    assert encoded == b'\xD7\x11\x7B\x01'

def test_encode_optional_struct():
    lrpc_def = __load_lrpc_def()

    var = LrpcVar({ 'name': 'v1', 'type': '@MyStruct1', 'base_type_is_struct': True, 'count': '?'})

    encoded = lrpc_encode(None, var, lrpc_def)
    assert encoded == b'\x00'
    encoded = lrpc_encode({'b': 123, 'a': 4567, 'c': True}, var, lrpc_def)
    assert encoded == b'\x01\xD7\x11\x7B\x01'

def test_encode_nested_struct():
    lrpc_def = __load_lrpc_def()

    var = LrpcVar({ 'name': 'v1', 'type': '@MyStruct2', 'base_type_is_struct': True})

    encoded = lrpc_encode({'a': {'b': 123, 'a': 4567, 'c': True}}, var, lrpc_def)
    assert encoded == b'\xD7\x11\x7B\x01'

def test_encode_enum():
    lrpc_def = __load_lrpc_def()

    var = LrpcVar({ 'name': 'v1', 'type': '@MyEnum1', 'base_type_is_enum': True})

    encoded = lrpc_encode('test1', var, lrpc_def)
    assert encoded == b'\x00'
    encoded = lrpc_encode('test2', var, lrpc_def)
    assert encoded == b'\x37'

    with pytest.raises(struct.error):
        lrpc_encode('test3', var, lrpc_def)

def test_encode_optional_enum():
    lrpc_def = __load_lrpc_def()

    var = LrpcVar({ 'name': 'v1', 'type': '@MyEnum1', 'base_type_is_enum': True, 'count': '?'})

    encoded = lrpc_encode(None, var, lrpc_def)
    assert encoded == b'\x00'
    encoded = lrpc_encode('test2', var, lrpc_def)
    assert encoded == b'\x01\x37'
