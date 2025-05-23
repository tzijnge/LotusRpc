import pytest
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

    with pytest.raises(ValueError):
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

    with pytest.raises(ValueError):
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
