import pytest
from lrpc.core import LrpcVar, LrpcVarDict


def test_construct_basic() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "uint8_t"}
    var = LrpcVar(v)

    assert var.name() == "v1"
    assert var.base_type() == "uint8_t"
    assert var.base_type_is_integral() is True


def test_base_type_is_bool() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "bool"}
    var = LrpcVar(v)

    assert var.base_type() == "bool"
    assert var.base_type_is_bool() is True


def test_base_type_is_float() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "float"}
    v2: LrpcVarDict = {"name": "v2", "type": "double"}

    var = LrpcVar(v1)
    assert var.base_type() == "float"
    assert var.base_type_is_float() is True

    var = LrpcVar(v2)
    assert var.base_type() == "double"
    assert var.base_type_is_float() is True


def test_base_type_is_string() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "string"}
    v2: LrpcVarDict = {
        "name": "v2",
        "type": "string_10",
        "count": 3,
    }

    var = LrpcVar(v1)
    assert var.base_type() == "string"
    assert var.base_type_is_string() is True
    assert var.is_array_of_strings() is False

    var = LrpcVar(v2)
    assert var.base_type() == "string_10"
    assert var.base_type_is_string() is True
    assert var.is_array_of_strings() is True


def test_contained() -> None:
    v1: LrpcVarDict = {
        "name": "v1",
        "type": "bool",
    }
    v2: LrpcVarDict = {
        "name": "v2",
        "type": "bool",
        "count": "?",
    }
    v3: LrpcVarDict = {
        "name": "v3",
        "type": "bool",
        "count": 3,
    }

    var1 = LrpcVar(v1).contained()
    assert var1.is_array() is False
    assert var1.array_size() == 1

    var2 = LrpcVar(v2).contained()
    assert var2.is_array() is False
    assert var2.array_size() == 1

    var3 = LrpcVar(v3).contained()
    assert var3.is_array() is False
    assert var3.array_size() == 1


def test_bool_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "bool"}
    assert LrpcVar(v1).pack_type() == "?"


def test_uint8_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "uint8_t"}
    assert LrpcVar(v1).pack_type() == "B"


def test_int8_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "int8_t"}
    assert LrpcVar(v1).pack_type() == "b"


def test_uint16_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "uint16_t"}
    assert LrpcVar(v1).pack_type() == "H"


def test_int16_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "int16_t"}
    assert LrpcVar(v1).pack_type() == "h"


def test_uint32_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "uint32_t"}
    assert LrpcVar(v1).pack_type() == "I"


def test_int32_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "int32_t"}
    assert LrpcVar(v1).pack_type() == "i"


def test_uint64_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "uint64_t"}
    assert LrpcVar(v1).pack_type() == "Q"


def test_int64_t_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "int64_t"}
    assert LrpcVar(v1).pack_type() == "q"


def test_float_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "float"}
    assert LrpcVar(v1).pack_type() == "f"


def test_double_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "double"}
    assert LrpcVar(v1).pack_type() == "d"


def test_enum_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "enum@MyEnum"}
    assert LrpcVar(v1).base_type_is_enum() is True
    assert LrpcVar(v1).pack_type() == "B"


def test_struct_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "struct@MyStruct"}
    assert LrpcVar(v1).base_type_is_struct()

    with pytest.raises(TypeError):
        LrpcVar(v1).pack_type()


def test_optional_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "bool", "count": "?"}
    assert LrpcVar(v1).is_optional()

    with pytest.raises(TypeError):
        LrpcVar(v1).pack_type()


def test_array_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "bool", "count": 5}
    assert LrpcVar(v1).is_array()

    with pytest.raises(TypeError):
        LrpcVar(v1).pack_type()


def test_string_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "string"}
    assert LrpcVar(v1).is_string()

    with pytest.raises(TypeError):
        LrpcVar(v1).pack_type()
