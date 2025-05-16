import pytest
from lrpc.core import LrpcStream, LrpcStreamDict, LrpcVar
from lrpc.visitors import LrpcVisitor


def test_client_stream_no_params() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "client",
    }

    stream = LrpcStream(s)

    assert stream.name() == "s1"
    assert stream.id() == 123
    assert stream.origin() == LrpcStream.Origin.CLIENT

    assert stream.number_params() == 0


def test_client_stream_with_params() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "client",
        "params": [{"name": "p1", "type": "uint8_t"}]
    }

    stream = LrpcStream(s)

    assert stream.name() == "s1"
    assert stream.id() == 123
    assert stream.origin() == LrpcStream.Origin.CLIENT

    assert stream.number_params() == 1
    assert len(stream.params()) == 1
    assert stream.params()[0].name() == "p1"
    assert len(stream.param_names()) == 1
    assert stream.param_names()[0] == "p1"


def test_server_stream_with_params() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "params": [{"name": "p1", "type": "uint8_t"}]
    }

    stream = LrpcStream(s)

    assert stream.name() == "s1"
    assert stream.id() == 123
    assert stream.origin() == LrpcStream.Origin.SERVER

    assert stream.number_params() == 1
    assert len(stream.params()) == 1
    assert stream.params()[0].name() == "p1"
    assert len(stream.param_names()) == 1
    assert stream.param_names()[0] == "p1"


def test_stream_param() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "params": [{"name": "p1", "type": "uint8_t"}]
    }

    stream = LrpcStream(s)

    assert stream.param("p1").name() == "p1"

    with pytest.raises(ValueError):
        stream.param("p2")

class TestVisitor(LrpcVisitor):
    def __init__(self) -> None:
        self.result:str = ""

    def visit_lrpc_stream(self, stream: LrpcStream, origin: LrpcStream.Origin) -> None:
        self.result += f"stream[{stream.name()}+{stream.id()}+{origin.value}]-"

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self.result += f"param[{param.name()}]-"

    def visit_lrpc_stream_param_end(self) -> None:
        self.result += "param_end-"

    def visit_lrpc_stream_end(self) -> None:
        self.result += "stream_end"

def test_visit_stream() -> None:
    tv = TestVisitor()

    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}]
    }

    stream = LrpcStream(s)

    stream.accept(tv)

    assert tv.result == "stream[s1+123+server]-param[p1]-param[p2]-param_end-stream_end"