import re

import pytest
from pydantic import ValidationError

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

    with pytest.raises(
        TypeError,
        match=re.escape("Pack type is not defined for LrpcVar of type struct"),
    ):
        LrpcVar(v1).pack_type()


def test_optional_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "bool", "count": "?"}
    assert LrpcVar(v1).is_optional()

    with pytest.raises(
        TypeError,
        match=re.escape("Pack type is not defined for LrpcVar of type optional"),
    ):
        LrpcVar(v1).pack_type()


def test_array_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "bool", "count": 5}
    assert LrpcVar(v1).is_array()

    with pytest.raises(
        TypeError,
        match=re.escape("Pack type is not defined for LrpcVar of type array"),
    ):
        LrpcVar(v1).pack_type()


def test_string_pack_type() -> None:
    v1: LrpcVarDict = {"name": "v1", "type": "string"}
    assert LrpcVar(v1).is_string()

    with pytest.raises(
        TypeError,
        match=re.escape("Pack type is not defined for LrpcVar of type string"),
    ):
        LrpcVar(v1).pack_type()


def test_validation_missing_name() -> None:
    v = {"type": "uint8_t"}

    with pytest.raises(ValidationError, match=re.escape("Field required")):
        LrpcVar(v)  # type: ignore[arg-type]


def test_validation_missing_type() -> None:
    v = {"name": "v1"}

    with pytest.raises(ValidationError, match=re.escape("Field required")):
        LrpcVar(v)  # type: ignore[arg-type]


def test_validation_wrong_type_name() -> None:
    v = {"name": 123, "type": "uint8_t"}

    with pytest.raises(ValidationError, match=re.escape("Input should be a valid string")):
        LrpcVar(v)  # type: ignore[arg-type]


def test_validation_wrong_type_type() -> None:
    v = {"name": "v1", "type": 123}

    with pytest.raises(ValidationError, match=re.escape("Input should be a valid string")):
        LrpcVar(v)  # type: ignore[arg-type]


def test_validation_wrong_type_count() -> None:
    v = {"name": "v1", "type": "uint8_t", "count": "invalid"}

    with pytest.raises(ValidationError, match=re.escape("Input should be a valid integer")):
        LrpcVar(v)  # type: ignore[arg-type]


def test_validation_additional_fields() -> None:
    v = {"name": "v1", "type": "uint8_t", "extra_field": "should_fail"}

    with pytest.raises(ValidationError, match=re.escape("Extra inputs are not permitted")):
        LrpcVar(v)  # type: ignore[arg-type]


def test_rw_type_intrinsic() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "uint8_t"}

    assert LrpcVar(v).rw_type() == "uint8_t"


def test_rw_type_fixed_size_string() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "string_2"}

    assert LrpcVar(v).rw_type() == "lrpc::tags::string_n"


def test_rw_type_auto_string() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "string"}

    assert LrpcVar(v).rw_type() == "lrpc::tags::string_auto"


def test_rw_type_array_of_intrinsic() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "bool", "count": 2}

    assert LrpcVar(v).rw_type() == "lrpc::tags::array_n<bool>"


def test_rw_type_optional_of_intrinsic() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "float", "count": "?"}

    assert LrpcVar(v).rw_type() == "etl::optional<float>"


def test_rw_type_custom() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "@MyType"}

    assert LrpcVar(v).rw_type() == "MyType"


def test_rw_type_intrinsic_with_namespace() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "int64_t"}

    assert LrpcVar(v).rw_type("my_namespace") == "int64_t"


def test_rw_type_custom_with_namespace() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "@MyType"}

    assert LrpcVar(v).rw_type("my_namespace") == "my_namespace::MyType"


def test_rw_type_array_of_custom_with_namespace() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "@MyType", "count": 2}

    assert LrpcVar(v).rw_type("my_namespace") == "lrpc::tags::array_n<my_namespace::MyType>"


def test_rw_type_optional_of_custom_with_namespace() -> None:
    v: LrpcVarDict = {"name": "v1", "type": "@MyType", "count": "?"}

    assert LrpcVar(v).rw_type("my_namespace") == "etl::optional<my_namespace::MyType>"


class TestLrpcVarByteArray:
    def test_bytearray(self) -> None:
        var_dict: LrpcVarDict = {"name": "v1", "type": "bytearray"}
        v = LrpcVar(var_dict)

        assert v.name() == "v1"
        assert v.base_type() == "bytearray"
        assert v.field_type() == "etl::span<const uint8_t>"
        assert v.return_type() == "etl::span<const uint8_t>"
        assert v.param_type() == "etl::span<const uint8_t>"
        assert v.rw_type() == "lrpc::bytearray"
        assert not v.base_type_is_custom()
        assert not v.base_type_is_struct()
        assert not v.base_type_is_enum()
        assert not v.base_type_is_integral()
        assert not v.base_type_is_float()
        assert not v.base_type_is_bool()
        assert not v.base_type_is_string()
        assert v.base_type_is_bytearray()
        assert not v.is_struct()
        assert not v.is_optional()
        assert not v.is_array()
        assert not v.is_array_of_strings()
        assert not v.is_string()
        assert not v.is_auto_string()
        assert not v.is_fixed_size_string()
        assert v.string_size() == -1
        assert v.array_size() == 1
        with pytest.raises(TypeError, match="Pack type is not defined for LrpcVar of type bytearray"):
            v.pack_type()

    def test_array_of_bytearray(self) -> None:
        var_dict: LrpcVarDict = {"name": "v1", "type": "bytearray", "count": 2}
        v = LrpcVar(var_dict)

        assert v.name() == "v1"
        assert v.base_type() == "bytearray"
        assert v.field_type() == "etl::array<etl::span<const uint8_t>, 2>"
        assert v.return_type() == "etl::span<const etl::span<const uint8_t>>"
        assert v.param_type() == "etl::span<const etl::span<const uint8_t>>"
        assert v.rw_type() == "lrpc::tags::array_n<lrpc::bytearray>"
        assert not v.base_type_is_custom()
        assert not v.base_type_is_struct()
        assert not v.base_type_is_enum()
        assert not v.base_type_is_integral()
        assert not v.base_type_is_float()
        assert not v.base_type_is_bool()
        assert not v.base_type_is_string()
        assert v.base_type_is_bytearray()
        assert not v.is_struct()
        assert not v.is_optional()
        assert v.is_array()
        assert not v.is_array_of_strings()
        assert not v.is_string()
        assert not v.is_auto_string()
        assert not v.is_fixed_size_string()
        assert v.string_size() == -1
        assert v.array_size() == 2
        with pytest.raises(TypeError, match="Pack type is not defined for LrpcVar of type bytearray"):
            v.pack_type()

    def test_optional_of_bytearray(self) -> None:
        var_dict: LrpcVarDict = {"name": "v1", "type": "bytearray", "count": "?"}
        v = LrpcVar(var_dict)

        assert v.name() == "v1"
        assert v.base_type() == "bytearray"
        assert v.field_type() == "etl::optional<etl::span<const uint8_t>>"
        assert v.return_type() == "etl::optional<etl::span<const uint8_t>>"
        assert v.param_type() == "etl::optional<etl::span<const uint8_t>>"
        assert v.rw_type() == "etl::optional<lrpc::bytearray>"
        assert not v.base_type_is_custom()
        assert not v.base_type_is_struct()
        assert not v.base_type_is_enum()
        assert not v.base_type_is_integral()
        assert not v.base_type_is_float()
        assert not v.base_type_is_bool()
        assert not v.base_type_is_string()
        assert v.base_type_is_bytearray()
        assert not v.is_struct()
        assert v.is_optional()
        assert not v.is_array()
        assert not v.is_array_of_strings()
        assert not v.is_string()
        assert not v.is_auto_string()
        assert not v.is_fixed_size_string()
        assert v.string_size() == -1
        assert v.array_size() == -1
        with pytest.raises(TypeError, match="Pack type is not defined for LrpcVar of type optional"):
            v.pack_type()
