import struct
from os import path

import pytest
from lrpc.client import LrpcClient
from lrpc.utils import load_lrpc_def_from_url

def_url = path.join(path.dirname(path.abspath(__file__)), "test_lrpc_encode_decode.lrpc.yaml")
lrpc_def = load_lrpc_def_from_url(def_url, warnings_as_errors=False)
client = LrpcClient(lrpc_def)


def test_encode_nested_struct() -> None:
    assert client.encode("s0", "f1", p1={"a": {"a": 4567, "b": 123, "c": True}}) == b"\x07\x00\x01\xD7\x11\x7B\x01"


def test_call() -> None:
    encoded = client.encode("s1", "add5", **{"p0": 123})
    # client: send encoded to server

    # server: copy service ID and function ID and append return value
    response = b"\x04" + encoded[1:2] + encoded[2:3] + struct.pack("<B", encoded[3] + 5)

    # client: receive bytes and decode
    received = client.decode(response)

    assert "r0" in received
    assert received["r0"] == 128


def test_encode_invalid_service() -> None:
    with pytest.raises(ValueError):
        client.encode("invalid_service", "f2")


def test_encode_invalid_function() -> None:
    with pytest.raises(ValueError):
        client.encode("s1", "invalid_function")


def test_encode_too_many_parameters() -> None:
    with pytest.raises(ValueError):
        # function takes no parameters
        client.encode("s1", "f2", invalid=123)


def test_encode_missing_parameter() -> None:
    with pytest.raises(ValueError):
        # function takes one parameter, but none given
        client.encode("s1", "add5")


def test_encode_invalid_parameter_name() -> None:
    with pytest.raises(ValueError):
        # function takes one parameter, but none given
        client.encode("s1", "add5", invalid=5)


def test_decode_invalid_service_id() -> None:
    with pytest.raises(ValueError):
        encoded = b"\x04\xAA\x00\x02"
        client.decode(encoded)


def test_decode_invalid_function_id() -> None:
    with pytest.raises(ValueError):
        encoded = b"\x04\x01\xAA\x02"
        client.decode(encoded)

def test_decode_message_too_short() -> None:
    with pytest.raises(ValueError):
        client.decode(b"")

    with pytest.raises(ValueError):
        client.decode(b"\x04")

    with pytest.raises(ValueError):
        client.decode(b"\x04\x01")

def test_decode_error_response() -> None:
    with pytest.raises(ValueError) as e:
        client.decode(b"\x13\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

    assert str(e.value) == "The LRPC server reported an error"
