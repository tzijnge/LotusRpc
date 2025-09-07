import math

import pytest
from lrpc.core import LrpcConstant, LrpcConstantDict


def test_implicit_int() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == 123
    assert constant.cpp_type() == "int32_t"


def test_implicit_float() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123.456}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert math.isclose(float(constant.value()), 123.456)
    assert constant.cpp_type() == "float"


def test_implicit_bool() -> None:
    c: LrpcConstantDict = {"name": "t", "value": True}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() is True
    assert constant.cpp_type() == "bool"


def test_implicit_string() -> None:
    c: LrpcConstantDict = {"name": "t", "value": "This is a string"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == "This is a string"
    assert constant.cpp_type() == "string"


def test_explicit_int() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123, "cppType": "uint64_t"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == 123
    assert constant.cpp_type() == "uint64_t"


def test_explicit_float() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123.456, "cppType": "double"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert math.isclose(float(constant.value()), 123.456)
    assert constant.cpp_type() == "double"


def test_explicit_string() -> None:
    c: LrpcConstantDict = {"name": "t", "value": "This is a string", "cppType": "string"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == "This is a string"
    assert constant.cpp_type() == "string"


def test_explicit_bool() -> None:
    c: LrpcConstantDict = {"name": "t", "value": True, "cppType": "bool"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() is True
    assert constant.cpp_type() == "bool"


def test_invalid_type() -> None:
    c: LrpcConstantDict = {"name": "t", "value": True, "cppType": "invalid_type"}

    with pytest.raises(ValueError) as e:
        LrpcConstant(c)

    assert str(e.value) == "Invalid cppType for LrpcConstant t: invalid_type"


def test_invalid_implicit_type() -> None:
    # Ignite type error because that's what this test is about
    c: LrpcConstantDict = {"name": "t", "value": {"invalid_type": 1}}  # type: ignore

    with pytest.raises(ValueError) as e:
        LrpcConstant(c)

    assert str(e.value) == "Unable to infer cppType for LrpcConstant value: {'invalid_type': 1}"
