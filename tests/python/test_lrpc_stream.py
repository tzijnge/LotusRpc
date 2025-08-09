import pytest
from lrpc.core import LrpcStream, LrpcStreamDict
from .utilities import StringifyVisitor


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

    assert not stream.is_finite()


def test_client_stream_with_params() -> None:
    s: LrpcStreamDict = {"name": "s1", "id": 123, "origin": "client", "params": [{"name": "p1", "type": "uint8_t"}]}

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
    s: LrpcStreamDict = {"name": "s1", "id": 123, "origin": "server", "params": [{"name": "p1", "type": "uint8_t"}]}

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
    s: LrpcStreamDict = {"name": "s1", "id": 123, "origin": "server", "params": [{"name": "p1", "type": "uint8_t"}]}

    stream = LrpcStream(s)

    assert stream.param("p1").name() == "p1"

    with pytest.raises(ValueError):
        stream.param("p2")


def test_visit_stream() -> None:
    v = StringifyVisitor()

    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    stream = LrpcStream(s)

    stream.accept(v)

    assert v.result == "stream[s1+123+server]-param[p1]-param[p2]-param_end-stream_end"


def test_finite_stream() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "finite": True,
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    assert LrpcStream(s).is_finite()


def test_infinite_stream() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "finite": False,
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    assert not LrpcStream(s).is_finite()
