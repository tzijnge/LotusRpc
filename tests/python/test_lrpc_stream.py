from lrpc.core import LrpcStream, LrpcStreamDict


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
    assert stream.number_returns() == 0


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

    assert stream.number_returns() == 0


def test_client_stream_with_params_and_returns() -> None:
    s: LrpcStreamDict = {
        "name": "s1",
        "id": 123,
        "origin": "client",
        "params": [{"name": "p1", "type": "uint8_t"}],
        "returns": [{"name": "r1", "type": "uint8_t"}],
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

    assert stream.number_returns() == 1
    assert len(stream.returns()) == 1
    assert stream.returns()[0].name() == "r1"


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

    assert stream.number_returns() == 0
