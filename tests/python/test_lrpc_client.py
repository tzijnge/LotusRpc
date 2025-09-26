import struct
from os import path

import pytest
from lrpc.client import LrpcClient
from lrpc.utils import load_lrpc_def_from_url

def_url = path.join(path.dirname(path.abspath(__file__)), "test_lrpc_encode_decode.lrpc.yaml")
lrpc_def = load_lrpc_def_from_url(def_url, warnings_as_errors=False)
client = LrpcClient(lrpc_def)


def test_call() -> None:
    encoded = client.encode("srv1", "add5", **{"p0": 123})
    # client: send encoded to server

    # server: copy service ID and function ID and append return value
    response = b"\x04" + encoded[1:2] + encoded[2:3] + struct.pack("<B", encoded[3] + 5)

    # client: receive bytes and decode
    received = client.decode(response)

    assert "r0" in received
    assert received["r0"] == 128


def test_encode_function_nested_struct() -> None:
    assert client.encode("srv0", "f1", p1={"a": {"a": 4567, "b": 123, "c": True}}) == b"\x07\x00\x01\xd7\x11\x7b\x01"


def test_encode_function_invalid_service() -> None:
    with pytest.raises(ValueError):
        client.encode("invalid_service", "f2")


def test_encode_function_invalid_function() -> None:
    with pytest.raises(ValueError) as e:
        client.encode("srv1", "invalid_function")

    assert str(e.value) == "Function or stream invalid_function not found in service srv1"


def test_encode_function_too_many_parameters() -> None:
    with pytest.raises(ValueError) as e:
        # function takes no parameters
        client.encode("srv1", "f2", invalid=123)

    assert str(e.value) == "No such parameter(s): {'invalid'}"


def test_encode_function_missing_parameter() -> None:
    with pytest.raises(ValueError) as e:
        # function takes one parameter, but none given
        client.encode("srv1", "add5")

    assert str(e.value) == "Required parameter(s) {'p0'} not given"


def test_encode_function_invalid_parameter_name() -> None:
    with pytest.raises(ValueError) as e:
        # function takes one parameter, but none given
        client.encode("srv1", "add5", invalid=5)

    assert str(e.value) == "No such parameter(s): {'invalid'}"


def test_encode_function() -> None:
    encoded = client.encode("srv1", "add5", p0=0xAB)
    assert encoded == b"\x04\x01\x00\xab"

    has_response = client.has_response("srv1", "add5", start=True)
    assert has_response is True


def test_encode_stream_client_infinite() -> None:
    encoded = client.encode("srv2", "client_infinite", p0=0xAB, p1=0xCDEF)
    assert encoded == b"\x06\x02\x00\xab\xef\xcd"

    has_response = client.has_response("srv2", "client_infinite", p0=0xAB, p1=0xCDEF)
    assert has_response is False


def test_encode_stream_client_finite() -> None:
    encoded = client.encode("srv2", "client_finite", p0=0xAB, p1=0xCDEF, final=True)
    assert encoded == b"\x07\x02\x01\xab\xef\xcd\x01"

    has_response = client.has_response("srv2", "client_finite", p0=0xAB, p1=0xCDEF)
    assert has_response is False


def test_encode_stream_server_infinite_start() -> None:
    encoded = client.encode("srv2", "server_infinite", start=True)
    assert encoded == b"\x04\x02\x02\x01"

    has_response = client.has_response("srv2", "server_infinite", start=True)
    assert has_response is True


def test_encode_stream_server_infinite_stop() -> None:
    encoded = client.encode("srv2", "server_infinite", start=False)
    assert encoded == b"\x04\x02\x02\x00"

    has_response = client.has_response("srv2", "server_infinite", start=False)
    assert has_response is False


def test_encode_stream_server_finite_start() -> None:
    encoded = client.encode("srv2", "server_finite", start=True)
    assert encoded == b"\x04\x02\x03\x01"

    has_response = client.has_response("srv2", "server_finite", start=True)
    assert has_response is True


def test_encode_stream_server_finite_stop() -> None:
    encoded = client.encode("srv2", "server_finite", start=False)
    assert encoded == b"\x04\x02\x03\x00"

    has_response = client.has_response("srv2", "server_infinite", start=False)
    assert has_response is False


def test_decode_stream_client_infinite_request_stop() -> None:
    decoded = client.decode(b"\x03\x02\x00")
    assert isinstance(decoded, dict)
    assert len(decoded.items()) == 0


def test_decode_stream_client_infinite_invalid() -> None:
    # In a client stream, the server can only send a stop request
    # that is a message with no fields other than message size, service ID and stream ID
    with pytest.raises(ValueError) as e:
        client.decode(b"\x04\x02\x00\x00")

    assert str(e.value) == "1 remaining bytes after decoding srv2.client_infinite"


def test_decode_stream_client_finite_request_stop() -> None:
    decoded = client.decode(b"\x03\x02\x01")
    assert isinstance(decoded, dict)
    assert len(decoded.items()) == 0


def test_decode_stream_client_finite_invalid() -> None:
    # In a client stream, the server can only send a stop request
    # that is a message with no fields other than message size, service ID and stream ID
    with pytest.raises(ValueError) as e:
        client.decode(b"\x05\x02\x01\xff\x66")

    assert str(e.value) == "2 remaining bytes after decoding srv2.client_finite"


def test_decode_stream_server_infinite() -> None:
    decoded = client.decode(b"\x06\x02\x02\x45\x67\x89")
    assert isinstance(decoded, dict)
    assert len(decoded.items()) == 2
    assert "p0" in decoded
    assert decoded.get("p0") == 0x45
    assert "p1" in decoded
    assert decoded.get("p1") == 0x8967


def test_decode_stream_server_finite() -> None:
    decoded = client.decode(b"\x07\x02\x03\x45\x67\x89\x00")
    assert isinstance(decoded, dict)
    assert len(decoded.items()) == 3
    assert "p0" in decoded
    assert decoded.get("p0") == 0x45
    assert "p1" in decoded
    assert decoded.get("p1") == 0x8967
    assert "final" in decoded
    assert decoded.get("final") is False


def test_decode_invalid_service_id() -> None:
    with pytest.raises(ValueError) as e:
        encoded = b"\x04\xaa\x00\x02"
        client.decode(encoded)

    assert str(e.value) == "Service with ID 170 not found in the LRPC definition file"


def test_decode_invalid_function_id() -> None:
    with pytest.raises(ValueError) as e:
        encoded = b"\x04\x01\xaa\x02"
        client.decode(encoded)

    assert str(e.value) == "No function or stream with ID 170 found in service srv1"


def test_decode_message_too_short() -> None:
    with pytest.raises(ValueError) as e:
        client.decode(b"")

    assert str(e.value) == "Unable to decode message from b'': an LRPC message has at least 3 bytes"

    with pytest.raises(ValueError) as e:
        client.decode(b"\x04")

    assert str(e.value) == "Unable to decode message from b'\\x04': an LRPC message has at least 3 bytes"

    with pytest.raises(ValueError) as e:
        client.decode(b"\x04\x01")

    assert str(e.value) == "Unable to decode message from b'\\x04\\x01': an LRPC message has at least 3 bytes"


def test_decode_incorrect_size() -> None:
    with pytest.raises(ValueError) as e:
        client.decode(b"\x04\x00\x00")

    assert str(e.value) == "Incorrect message size. Expected 4 but got 3"


def test_decode_error_response() -> None:
    with pytest.raises(ValueError) as e:
        client.decode(b"\x13\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

    assert str(e.value) == "The LRPC server reported an error"


def test_has_response_invalid_service() -> None:
    with pytest.raises(ValueError) as e:
        client.encode("invalid_service", "server_finite", start=False)

    assert str(e.value) == "Service invalid_service not found in the LRPC definition file"


def test_has_response_invalid_function_or_stream() -> None:
    with pytest.raises(ValueError) as e:
        client.encode("srv2", "invalid_function_or_stream", start=False)

    assert str(e.value) == "Function or stream invalid_function_or_stream not found in service srv2"


def test_decode_void_function() -> None:
    # srv0.f0
    decoded = client.decode(b"\x03\x00\x00")
    assert isinstance(decoded, dict)
    assert len(decoded.items()) == 0


def test_remaining_bytes_after_decode() -> None:
    with pytest.raises(ValueError) as e:
        client.decode(b"\x05\x00\x00\xab\xcd")

    assert str(e.value) == "2 remaining bytes after decoding srv0.f0"
