import pytest
from lrpc.core import LrpcFun, LrpcFunDict, LrpcVar
from lrpc.visitors import LrpcVisitor


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


class TestVisitor(LrpcVisitor):
    def __init__(self) -> None:
        self.result: str = ""

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self.result += f"function[{function.name()}+{function.id()}]-"

    def visit_lrpc_function_end(self) -> None:
        self.result += "function_end"

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.result += f"return[{ret.name()}]-"

    def visit_lrpc_function_return_end(self) -> None:
        self.result += "return_end-"

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.result += f"param[{param.name()}]-"

    def visit_lrpc_function_param_end(self) -> None:
        self.result += "param_end-"


def test_visit_stream() -> None:
    tv = TestVisitor()

    s: LrpcFunDict = {
        "name": "f1",
        "id": 123,
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
        "returns": [{"name": "r1", "type": "uint8_t"}, {"name": "r2", "type": "bool"}],
    }

    stream = LrpcFun(s)

    stream.accept(tv)

    assert tv.result == "function[f1+123]-return[r1]-return[r2]-return_end-param[p1]-param[p2]-param_end-function_end"
