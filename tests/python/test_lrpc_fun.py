import re

import pytest
from pydantic import ValidationError

from lrpc.core import LrpcFun, LrpcFunDict

from .utilities import StringifyVisitor


def test_short_notation() -> None:
    f: LrpcFunDict = {"name": "f1", "id": 123}

    fun = LrpcFun(f)

    assert fun.name() == "f1"
    assert len(fun.params()) == 0
    assert len(fun.param_names()) == 0
    assert fun.number_returns() == 0
    assert len(fun.returns()) == 0
    assert fun.id() == 123


def test_full_notation() -> None:
    f: LrpcFunDict = {
        "name": "f1",
        "id": 123,
        "params": [{"name": "p1", "type": "uint8_t"}],
        "returns": [{"name": "r1", "type": "uint8_t"}],
    }

    fun = LrpcFun(f)

    assert fun.name() == "f1"
    assert len(fun.params()) == 1
    assert fun.params()[0].name() == "p1"
    assert len(fun.param_names()) == 1
    assert fun.param_names()[0] == "p1"
    assert fun.number_returns() == 1
    assert len(fun.returns()) == 1
    assert fun.returns()[0].name() == "r1"
    assert fun.id() == 123


def test_get_param_by_name() -> None:
    f: LrpcFunDict = {
        "name": "f1",
        "id": 123,
        "params": [{"name": "p1", "type": "uint8_t"}],
        "returns": [{"name": "r1", "type": "uint8_t"}],
    }

    fun = LrpcFun(f)

    with pytest.raises(ValueError, match=re.escape("No parameter  in function f1")):
        fun.param("")
    p1 = fun.param("p1")
    assert p1 is not None
    assert p1.name() == "p1"


def test_get_return_by_name() -> None:
    f: LrpcFunDict = {
        "name": "f1",
        "id": 123,
        "params": [{"name": "p1", "type": "uint8_t"}],
        "returns": [{"name": "r1", "type": "uint8_t"}],
    }

    fun = LrpcFun(f)

    with pytest.raises(ValueError, match=re.escape("No return value  in function f1")):
        fun.ret("")
    r1 = fun.ret("r1")
    assert r1 is not None
    assert r1.name() == "r1"


def test_visit_stream() -> None:
    v = StringifyVisitor()

    s: LrpcFunDict = {
        "name": "f1",
        "id": 123,
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
        "returns": [{"name": "r1", "type": "uint8_t"}, {"name": "r2", "type": "bool"}],
    }

    stream = LrpcFun(s)

    stream.accept(v)

    assert v.result == "function[f1+123]-return[r1]-return[r2]-return_end-param[p1]-param[p2]-param_end-function_end"


def test_validate_additional_fields() -> None:
    f = {
        "name": "f1",
        "id": 123,
        "additional_field": "not_allowed",
    }

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        LrpcFun(f)  # type: ignore[arg-type]


def test_validate_missing_name() -> None:
    f = {"id": 123}

    with pytest.raises(ValidationError, match="Field required"):
        LrpcFun(f)  # type: ignore[arg-type]


def test_validate_missing_id() -> None:
    f = {"name": "f1"}

    with pytest.raises(ValidationError, match="Field required"):
        LrpcFun(f)  # type: ignore[arg-type]


def test_validate_wrong_type_name() -> None:
    f = {"name": 123, "id": 123}

    with pytest.raises(ValidationError, match="Input should be a valid string"):
        LrpcFun(f)  # type: ignore[arg-type]


def test_validate_wrong_type_id() -> None:
    f = {"name": "f1", "id": "not_an_int"}

    with pytest.raises(ValidationError, match="Input should be a valid integer"):
        LrpcFun(f)  # type: ignore[arg-type]
