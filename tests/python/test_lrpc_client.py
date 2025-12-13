import re
import struct
from pathlib import Path

import pytest

from lrpc.client import LrpcClient
from lrpc.utils import load_lrpc_def_from_url


class FakeTransport:
    def __init__(self, response: bytes) -> None:
        self.response = response

    def read(self, count: int) -> bytes:
        data = self.response[0:count]
        self.response = self.response[count:]

        return data

    def write(self, data: bytes) -> None:
        # stub
        pass


def_url = Path(__file__).resolve().parent.joinpath("test_lrpc_encode_decode.lrpc.yaml")
lrpc_def = load_lrpc_def_from_url(def_url, warnings_as_errors=False)


# pylint: disable = too-many-public-methods
class TestLrpcClient:
    @staticmethod
    def client(response: bytes = b"") -> LrpcClient:
        transport = FakeTransport(response)
        return LrpcClient(lrpc_def, transport)

    def test_call(self) -> None:
        encoded = self.client().encode("srv1", "add5", p0=123)
        # client: send encoded to server

        # server: copy service ID and function ID and append return value
        response = b"\x04" + encoded[1:2] + encoded[2:3] + struct.pack("<B", encoded[3] + 5)

        # client: receive bytes and decode
        received = self.client().decode(response)

        assert "r0" in received
        assert received["r0"] == 128

    def test_encode_function_nested_struct(self) -> None:
        assert (
            self.client().encode("srv0", "f1", p1={"a": {"a": 4567, "b": 123, "c": True}})
            == b"\x07\x00\x01\xd7\x11\x7b\x01"
        )

    def test_encode_function_invalid_service(self) -> None:
        with pytest.raises(ValueError, match="Service invalid_service not found in the LRPC definition file"):
            self.client().encode("invalid_service", "f2")

    def test_encode_function_invalid_function(self) -> None:
        with pytest.raises(ValueError, match="Function or stream invalid_function not found in service srv1"):
            self.client().encode("srv1", "invalid_function")

    def test_encode_function_too_many_parameters(self) -> None:
        with pytest.raises(ValueError, match=re.escape("No such parameter(s): {'invalid'}")):
            # function takes no parameters
            self.client().encode("srv1", "f2", invalid=123)

    def test_encode_function_missing_parameter(self) -> None:
        with pytest.raises(ValueError, match=re.escape("Required parameter(s) {'p0'} not given")):
            # function takes one parameter, but none given
            self.client().encode("srv1", "add5")

    def test_encode_function_invalid_parameter_name(self) -> None:
        with pytest.raises(ValueError, match=re.escape("No such parameter(s): {'invalid'}")):
            # function takes one parameter, but none given
            self.client().encode("srv1", "add5", invalid=5)

    def test_encode_function(self) -> None:
        encoded = self.client().encode("srv1", "add5", p0=0xAB)
        assert encoded == b"\x04\x01\x00\xab"

    def test_encode_stream_client_infinite(self) -> None:
        encoded = self.client().encode("srv2", "client_infinite", p0=0xAB, p1=0xCDEF)
        assert encoded == b"\x06\x02\x00\xab\xef\xcd"

    def test_encode_stream_client_finite(self) -> None:
        encoded = self.client().encode("srv2", "client_finite", p0=0xAB, p1=0xCDEF, final=True)
        assert encoded == b"\x07\x02\x01\xab\xef\xcd\x01"

    def test_encode_stream_server_infinite_start(self) -> None:
        encoded = self.client().encode("srv2", "server_infinite", start=True)
        assert encoded == b"\x04\x02\x02\x01"

    def test_encode_stream_server_infinite_stop(self) -> None:
        encoded = self.client().encode("srv2", "server_infinite", start=False)
        assert encoded == b"\x04\x02\x02\x00"

    def test_encode_stream_server_finite_start(self) -> None:
        encoded = self.client().encode("srv2", "server_finite", start=True)
        assert encoded == b"\x04\x02\x03\x01"

    def test_encode_stream_server_finite_stop(self) -> None:
        encoded = self.client().encode("srv2", "server_finite", start=False)
        assert encoded == b"\x04\x02\x03\x00"

    def test_decode_stream_client_infinite_request_stop(self) -> None:
        decoded = self.client().decode(b"\x03\x02\x00")
        assert isinstance(decoded, dict)
        assert len(decoded.items()) == 0

    def test_decode_stream_client_infinite_invalid(self) -> None:
        # In a client stream, the server can only send a stop request
        # that is a message with no fields other than message size, service ID and stream ID
        with pytest.raises(ValueError, match=re.escape("1 remaining bytes after decoding srv2.client_infinite")):
            self.client().decode(b"\x04\x02\x00\x00")

    def test_decode_stream_client_finite_request_stop(self) -> None:
        decoded = self.client().decode(b"\x03\x02\x01")
        assert isinstance(decoded, dict)
        assert len(decoded.items()) == 0

    def test_decode_stream_client_finite_invalid(self) -> None:
        # In a client stream, the server can only send a stop request
        # that is a message with no fields other than message size, service ID and stream ID
        with pytest.raises(ValueError, match=re.escape("2 remaining bytes after decoding srv2.client_finite")):
            self.client().decode(b"\x05\x02\x01\xff\x66")

    def test_decode_stream_server_infinite(self) -> None:
        decoded = self.client().decode(b"\x06\x02\x02\x45\x67\x89")
        assert isinstance(decoded, dict)
        assert len(decoded.items()) == 2
        assert "p0" in decoded
        assert decoded.get("p0") == 0x45
        assert "p1" in decoded
        assert decoded.get("p1") == 0x8967

    def test_decode_stream_server_finite(self) -> None:
        decoded = self.client().decode(b"\x07\x02\x03\x45\x67\x89\x00")
        assert isinstance(decoded, dict)
        assert len(decoded.items()) == 3
        assert "p0" in decoded
        assert decoded.get("p0") == 0x45
        assert "p1" in decoded
        assert decoded.get("p1") == 0x8967
        assert "final" in decoded
        assert decoded.get("final") is False

    def test_decode_invalid_service_id(self) -> None:
        encoded = b"\x04\xaa\x00\x02"
        with pytest.raises(ValueError, match="Service with ID 170 not found in the LRPC definition file"):
            self.client().decode(encoded)

    def test_decode_invalid_function_id(self) -> None:
        encoded = b"\x04\x01\xaa\x02"
        with pytest.raises(ValueError, match="No function or stream with ID 170 found in service srv1"):
            self.client().decode(encoded)

    def test_decode_message_too_short(self) -> None:
        with pytest.raises(
            ValueError,
            match=re.escape("Unable to decode message from b'': an LRPC message has at least 3 bytes"),
        ):
            self.client().decode(b"")

        with pytest.raises(
            ValueError,
            match=re.escape("Unable to decode message from b'\\x04': an LRPC message has at least 3 bytes"),
        ):
            self.client().decode(b"\x04")

        with pytest.raises(
            ValueError,
            match=re.escape("Unable to decode message from b'\\x04\\x01': an LRPC message has at least 3 bytes"),
        ):
            self.client().decode(b"\x04\x01")

    def test_decode_incorrect_size(self) -> None:
        with pytest.raises(ValueError, match=re.escape("Incorrect message size. Expected 4 but got 3")):
            self.client().decode(b"\x04\x00\x00")

    def test_decode_error_response_unknown_service(self) -> None:
        decoded = self.client().decode(b"\x0b\xff\x00\x00\x55\x66\x00\x00\x00\x77\x00")
        assert "type" in decoded
        assert decoded["type"] == "UnknownService"
        assert "p1" in decoded
        assert decoded["p1"] == 0x55
        assert "p2" in decoded
        assert decoded["p2"] == 0x66
        assert "p3" in decoded
        assert decoded["p3"] == 0x77000000
        assert "message" in decoded
        assert decoded["message"] == ""

    def test_decode_error_response_unknown_function_or_stream(self) -> None:
        decoded = self.client().decode(b"\x0f\xff\x00\x01\x22\x33\x44\x00\x00\x00\x74\x65\x73\x74\x00")
        assert "type" in decoded
        assert decoded["type"] == "UnknownFunctionOrStream"
        assert "p1" in decoded
        assert decoded["p1"] == 0x22
        assert "p2" in decoded
        assert decoded["p2"] == 0x33
        assert "p3" in decoded
        assert decoded["p3"] == 0x44
        assert "message" in decoded
        assert decoded["message"] == "test"

    def test_decode_void_function(self) -> None:
        # srv0.f0
        decoded = self.client().decode(b"\x03\x00\x00")
        assert isinstance(decoded, dict)
        assert len(decoded.items()) == 0

    def test_remaining_bytes_after_decode(self) -> None:
        with pytest.raises(ValueError, match=re.escape("2 remaining bytes after decoding srv0.f0")):
            self.client().decode(b"\x05\x00\x00\xab\xcd")

    def test_communicate_function(self) -> None:
        response = b"\x04\x01\x00\xcd"
        for r in self.client(response).communicate("srv1", "add5", p0=0xAB):
            assert "r0" in r
            assert isinstance(r["r0"], int)
            assert r["r0"] == 0xCD

    def test_communicate_stream_client_infinite(self) -> None:
        communicator = self.client().communicate("srv2", "client_infinite", p0=0xAB, p1=0xCDEF)
        response = next(communicator, None)
        assert response is None

    def test_communicate_stream_client_finite(self) -> None:
        communicator = self.client().communicate("srv2", "client_finite", p0=0xAB, p1=0xCDEF, final=True)
        response = next(communicator, None)
        assert response is None

    def test_communicate_stream_server_infinite_stop(self) -> None:
        communicator = self.client().communicate("srv2", "server_infinite", start=False)
        response = next(communicator, None)
        assert response is None

    def test_communicate_stream_server_finite_stop(self) -> None:
        communicator = self.client().communicate("srv2", "server_finite", start=False)
        response = next(communicator, None)
        assert response is None

    def test_communicate_stream_server_infinite_start(self) -> None:
        response_bytes = b"\x06\x02\x02\xcd\x01\x02"
        response_generator = self.client(response_bytes).communicate("srv2", "server_infinite", start=True)
        response = next(response_generator)

        assert "p0" in response
        assert isinstance(response["p0"], int)
        assert response["p0"] == 0xCD

        assert "p1" in response
        assert isinstance(response["p1"], int)
        assert response["p1"] == 0x0201

        with pytest.raises(TimeoutError, match="Timeout waiting for response"):
            next(response_generator)

    def test_communicate_stream_server_finite_start(self) -> None:
        response = b"\x07\x02\x03\xcd\x01\x02\x01"
        for r in self.client(response).communicate("srv2", "server_finite", start=True):
            assert "p0" in r
            assert isinstance(r["p0"], int)
            assert r["p0"] == 0xCD

            assert "p1" in r
            assert isinstance(r["p1"], int)
            assert r["p1"] == 0x0201
