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


def test_client_stream_infinite_with_params() -> None:
    s: LrpcStreamDict = {"name": "s1", "id": 123, "origin": "client", "params": [{"name": "p1", "type": "uint8_t"}]}

    stream = LrpcStream(s)

    assert stream.name() == "s1"
    assert stream.id() == 123
    assert stream.origin() == LrpcStream.Origin.CLIENT
    assert not stream.is_finite()

    assert stream.number_params() == 1
    assert len(stream.params()) == 1
    assert stream.params()[0].name() == "p1"
    assert len(stream.param_names()) == 1
    assert stream.param_names()[0] == "p1"

    assert stream.number_returns() == 0
    assert len(stream.returns()) == 0


def test_client_stream_finite_with_params() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "client",
        "finite": True,
        "params": [{"name": "p1", "type": "uint8_t"}],
    }

    stream = LrpcStream(s)

    assert stream.name() == "s1"
    assert stream.id() == 123
    assert stream.origin() == LrpcStream.Origin.CLIENT
    assert stream.is_finite()

    assert stream.number_params() == 2
    assert len(stream.params()) == 2
    assert stream.params()[0].name() == "p1"
    assert stream.params()[1].name() == "final"
    assert len(stream.param_names()) == 2
    assert stream.param_names()[0] == "p1"
    assert stream.param_names()[1] == "final"

    assert stream.number_returns() == 0
    assert len(stream.returns()) == 0


def test_server_stream_infinite_with_params() -> None:
    s: LrpcStreamDict = {"name": "s1", "id": 123, "origin": "server", "params": [{"name": "p1", "type": "uint8_t"}]}

    stream = LrpcStream(s)

    assert stream.name() == "s1"
    assert stream.id() == 123
    assert stream.origin() == LrpcStream.Origin.SERVER
    assert not stream.is_finite()

    assert stream.number_params() == 1
    assert len(stream.params()) == 1
    assert stream.params()[0].name() == "start"
    assert len(stream.param_names()) == 1
    assert stream.param_names()[0] == "start"

    assert stream.number_returns() == 1
    assert len(stream.returns()) == 1
    assert stream.returns()[0].name() == "p1"


def test_server_stream_finite_with_params() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "finite": True,
        "params": [{"name": "p1", "type": "uint8_t"}],
    }

    stream = LrpcStream(s)

    assert stream.name() == "s1"
    assert stream.id() == 123
    assert stream.origin() == LrpcStream.Origin.SERVER
    assert stream.is_finite()

    assert stream.number_params() == 1
    assert len(stream.params()) == 1
    assert stream.params()[0].name() == "start"
    assert len(stream.param_names()) == 1
    assert stream.param_names()[0] == "start"

    assert stream.number_returns() == 2
    assert len(stream.returns()) == 2
    assert stream.returns()[0].name() == "p1"
    assert stream.returns()[1].name() == "final"


def test_stream_param() -> None:
    s: LrpcStreamDict = {"name": "s1", "id": 123, "origin": "server", "params": [{"name": "p1", "type": "uint8_t"}]}

    stream = LrpcStream(s)

    assert stream.returns()[0].name() == "p1"

    with pytest.raises(ValueError):
        stream.param("p2")


def test_visit_server_stream_infinite() -> None:
    v = StringifyVisitor()

    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    stream = LrpcStream(s)

    stream.accept(v)

    assert v.result == "stream[s1+123+server]-param[start]-param_end-return[p1]-return[p2]-return_end-stream_end"


def test_visit_server_stream_finite() -> None:
    v = StringifyVisitor()

    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "finite": True,
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    stream = LrpcStream(s)

    assert stream.is_finite()
    stream.accept(v)

    assert (
        v.result
        == "stream[s1+123+server]-param[start]-param_end-return[p1]-return[p2]-return[final]-return_end-stream_end"
    )


def test_visit_client_stream_infinite() -> None:
    v = StringifyVisitor()

    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "client",
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    stream = LrpcStream(s)

    assert not stream.is_finite()
    stream.accept(v)

    assert v.result == "stream[s1+123+client]-param[p1]-param[p2]-param_end-return_end-stream_end"


def test_visit_client_stream_finite() -> None:
    v = StringifyVisitor()

    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "client",
        "finite": True,
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    stream = LrpcStream(s)

    assert stream.is_finite()
    stream.accept(v)

    assert v.result == "stream[s1+123+client]-param[p1]-param[p2]-param[final]-param_end-return_end-stream_end"


def test_visit_infinite_stream() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "server",
        "finite": False,
        "params": [{"name": "p1", "type": "uint8_t"}, {"name": "p2", "type": "bool"}],
    }

    assert not LrpcStream(s).is_finite()
