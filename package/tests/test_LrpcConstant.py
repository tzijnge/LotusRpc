from lrpc.core import LrpcConstant, LrpcConstantDict


def test_default_int() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == 123
    assert constant.cpp_type() == "int32_t"


def test_default_float() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123.456}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == 123.456
    assert constant.cpp_type() == "float"


def test_default_bool() -> None:
    c: LrpcConstantDict = {"name": "t", "value": True}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() is True
    assert constant.cpp_type() == "bool"


def test_default_string() -> None:
    c: LrpcConstantDict = {"name": "t", "value": "This is a string"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == "This is a string"
    assert constant.cpp_type() == "string"


def test_non_default_int() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123, "cppType": "uint64_t"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == 123
    assert constant.cpp_type() == "uint64_t"


def test_non_default_float() -> None:
    c: LrpcConstantDict = {"name": "t", "value": 123.456, "cppType": "double"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == 123.456
    assert constant.cpp_type() == "double"


def test_non_default_string() -> None:
    c: LrpcConstantDict = {"name": "t", "value": "This is a string", "cppType": "string"}

    constant = LrpcConstant(c)

    assert constant.name() == "t"
    assert constant.value() == "This is a string"
    assert constant.cpp_type() == "string"
