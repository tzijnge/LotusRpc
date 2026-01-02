import re
import struct
from importlib.metadata import version
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
        response_bytes = b"\x04" + encoded[1:2] + encoded[2:3] + struct.pack("<B", encoded[3] + 5)

        # client: receive bytes and decode
        response = self.client().decode(response_bytes)
        payload = response.payload

        assert "r0" in payload
        assert payload["r0"] == 128

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
        response = self.client().decode(b"\x03\x02\x00")
        payload = response.payload

        assert isinstance(payload, dict)
        assert len(payload.items()) == 0

    def test_decode_stream_client_infinite_invalid(self) -> None:
        # In a client stream, the server can only send a stop request
        # that is a message with no fields other than message size, service ID and stream ID
        with pytest.raises(ValueError, match=re.escape("1 remaining bytes after decoding srv2.client_infinite")):
            self.client().decode(b"\x04\x02\x00\x00")

    def test_decode_stream_client_finite_request_stop(self) -> None:
        response = self.client().decode(b"\x03\x02\x01")
        payload = response.payload

        assert isinstance(payload, dict)
        assert len(payload.items()) == 0

    def test_decode_stream_client_finite_invalid(self) -> None:
        # In a client stream, the server can only send a stop request
        # that is a message with no fields other than message size, service ID and stream ID
        with pytest.raises(ValueError, match=re.escape("2 remaining bytes after decoding srv2.client_finite")):
            self.client().decode(b"\x05\x02\x01\xff\x66")

    def test_decode_stream_server_infinite(self) -> None:
        response = self.client().decode(b"\x06\x02\x02\x45\x67\x89")
        payload = response.payload

        assert isinstance(payload, dict)
        assert len(payload.items()) == 2
        assert "p0" in payload
        assert payload.get("p0") == 0x45
        assert "p1" in payload
        assert payload.get("p1") == 0x8967

    def test_decode_stream_server_finite(self) -> None:
        response = self.client().decode(b"\x07\x02\x03\x45\x67\x89\x00")
        payload = response.payload

        assert isinstance(payload, dict)
        assert len(payload.items()) == 3
        assert "p0" in payload
        assert payload.get("p0") == 0x45
        assert "p1" in payload
        assert payload.get("p1") == 0x8967
        assert "final" in payload
        assert payload.get("final") is False

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

    def test_error_response(self) -> None:
        # unknown service
        response = self.client().decode(b"\x0b\xff\x00\x00\x55\x66\x00\x00\x00\x77\x00")

        assert response.is_error_response
        assert not response.is_expected_response
        assert not response.is_function_response
        assert response.is_stream_response
        assert response.service_name == "LrpcMeta"
        assert response.function_or_stream_name == "error"

    def test_decode_error_response_unknown_service(self) -> None:
        response = self.client().decode(b"\x0b\xff\x00\x00\x55\x66\x00\x00\x00\x77\x00")
        payload = response.payload

        assert "type" in payload
        assert payload["type"] == "UnknownService"
        assert "p1" in payload
        assert payload["p1"] == 0x55
        assert "p2" in payload
        assert payload["p2"] == 0x66
        assert "p3" in payload
        assert payload["p3"] == 0x77000000
        assert "message" in payload
        assert payload["message"] == ""

    def test_decode_error_response_unknown_function_or_stream(self) -> None:
        response = self.client().decode(b"\x0f\xff\x00\x01\x22\x33\x44\x00\x00\x00\x74\x65\x73\x74\x00")
        payload = response.payload

        assert "type" in payload
        assert payload["type"] == "UnknownFunctionOrStream"
        assert "p1" in payload
        assert payload["p1"] == 0x22
        assert "p2" in payload
        assert payload["p2"] == 0x33
        assert "p3" in payload
        assert payload["p3"] == 0x44
        assert "message" in payload
        assert payload["message"] == "test"

    def test_decode_error_response_invalid_type(self) -> None:
        with pytest.raises(ValueError, match=re.escape("Value 255 (0xff) is not valid for enum LrpcMetaError")):
            self.client().decode(b"\x0f\xff\x00\xff\x22\x33\x44\x00\x00\x00\x74\x65\x73\x74\x00")

    def test_decode_void_function(self) -> None:
        # srv0.f0
        response = self.client().decode(b"\x03\x00\x00")
        payload = response.payload
        assert isinstance(payload, dict)
        assert len(payload.items()) == 0

    def test_remaining_bytes_after_decode(self) -> None:
        with pytest.raises(ValueError, match=re.escape("2 remaining bytes after decoding srv0.f0")):
            self.client().decode(b"\x05\x00\x00\xab\xcd")

    def test_communicate_function(self) -> None:
        response_bytes = b"\x04\x01\x00\xcd"
        response = self.client(response_bytes).communicate_single("srv1", "add5", p0=0xAB)
        payload = response.payload

        assert "r0" in payload
        assert isinstance(payload["r0"], int)
        assert payload["r0"] == 0xCD

        assert response.is_error_response is False
        assert response.is_expected_response
        assert response.is_function_response
        assert response.is_stream_response is False
        assert response.service_name == "srv1"
        assert response.function_or_stream_name == "add5"

    def test_communicate_function_wrong_response(self, caplog: pytest.LogCaptureFixture) -> None:
        # response belongs to srv0.f0
        response_bytes = b"\x03\x00\x00"
        response = self.client(response_bytes).communicate_single("srv1", "add5", p0=0xAB)
        payload = response.payload

        assert len(payload.items()) == 0

        assert response.is_error_response is False
        assert response.is_expected_response is False
        assert response.is_function_response is True
        assert response.is_stream_response is False
        assert response.service_name == "srv0"
        assert response.function_or_stream_name == "f0"

        assert len(caplog.messages) == 1
        assert caplog.messages[0] == "Unexpected response. Expected srv1.add5, but got srv0.f0"

    def test_communicate_function_error_response(self, caplog: pytest.LogCaptureFixture) -> None:
        response_bytes = b"\x0b\xff\x00\x00\x55\x66\x00\x00\x00\x77\x00"
        response = self.client(response_bytes).communicate_single("srv1", "add5", p0=0xAB)

        assert response.is_error_response
        assert response.is_expected_response is False
        assert response.is_function_response is False
        assert response.is_stream_response is True
        assert response.service_name == "LrpcMeta"
        assert response.function_or_stream_name == "error"

        assert len(caplog.messages) == 1
        assert caplog.messages[0] == "Server reported error 'UnknownService' for call to srv1.add5"

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
        payload = response.payload

        assert "p0" in payload
        assert isinstance(payload["p0"], int)
        assert payload["p0"] == 0xCD

        assert "p1" in payload
        assert isinstance(payload["p1"], int)
        assert payload["p1"] == 0x0201

        assert response.is_error_response is False
        assert response.is_expected_response
        assert response.is_function_response is False
        assert response.is_stream_response
        assert response.service_name == "srv2"
        assert response.function_or_stream_name == "server_infinite"

        with pytest.raises(TimeoutError, match="Timeout waiting for response"):
            next(response_generator)

    def test_communicate_stream_server_finite_start(self) -> None:
        response_bytes = b"\x07\x02\x03\xcd\x01\x02\x01"
        response = self.client(response_bytes).communicate_single("srv2", "server_finite", start=True)
        payload = response.payload

        assert "p0" in payload
        assert isinstance(payload["p0"], int)
        assert payload["p0"] == 0xCD

        assert "p1" in payload
        assert isinstance(payload["p1"], int)
        assert payload["p1"] == 0x0201

        assert response.is_error_response is False
        assert response.is_expected_response
        assert response.is_function_response is False
        assert response.is_stream_response
        assert response.service_name == "srv2"
        assert response.function_or_stream_name == "server_finite"

    @staticmethod
    def make_version_response(def_version: str, def_hash: str, lrpc_version: str) -> bytes:
        message_length = 3 + len(def_version) + 1 + len(def_hash) + 1 + len(lrpc_version) + 1
        msg_len = message_length.to_bytes(length=1, byteorder="little")

        return (
            msg_len
            + b"\xff\x80"
            + def_version.encode("utf-8")
            + b"\x00"
            + def_hash.encode("utf-8")
            + b"\x00"
            + lrpc_version.encode("utf-8")
            + b"\x00"
        )

    def test_check_server_version_ok(self, caplog: pytest.LogCaptureFixture) -> None:
        def_version = lrpc_def.version() or ""
        def_hash = lrpc_def.definition_hash() or ""
        lrpc_version = version("lotusrpc")

        response = self.make_version_response(def_version, def_hash, lrpc_version)
        client = self.client(response)
        server_ok = client.check_server_version()

        assert server_ok
        assert len(caplog.messages) == 0

    def test_check_server_version_mismatch_def_hash(self, caplog: pytest.LogCaptureFixture) -> None:
        def_version = lrpc_def.version() or ""
        def_hash = "[wrong hash]"
        lrpc_version = version("lotusrpc")

        response = self.make_version_response(def_version, def_hash, lrpc_version)
        client = self.client(response)
        server_ok = client.check_server_version()

        assert not server_ok
        assert len(caplog.messages) == 4
        assert "Server mismatch detected. Details client vs server:" in caplog.messages
        assert f"LotusRPC version: {lrpc_version} vs {lrpc_version}" in caplog.messages
        assert "Definition version: [disabled] vs [disabled]" in caplog.messages
        assert "Definition hash: 686d3ba44ae73e14... vs [wrong hash]..." in caplog.messages

    def test_check_server_version_mismatch_lrpc_version(self, caplog: pytest.LogCaptureFixture) -> None:
        def_version = lrpc_def.version() or ""
        def_hash = lrpc_def.definition_hash() or ""
        lrpc_version = "[wrong version]"

        response = self.make_version_response(def_version, def_hash, lrpc_version)
        client = self.client(response)
        server_ok = client.check_server_version()

        assert not server_ok
        assert len(caplog.messages) == 4
        assert "Server mismatch detected. Details client vs server:" in caplog.messages
        assert f"LotusRPC version: {version('lotusrpc')} vs [wrong version]" in caplog.messages
        assert "Definition version: [disabled] vs [disabled]" in caplog.messages
        assert "Definition hash: 686d3ba44ae73e14... vs 686d3ba44ae73e14..." in caplog.messages

    def test_check_server_version_mismatch_def_version(self, caplog: pytest.LogCaptureFixture) -> None:
        def_version = "[wrong version]"
        def_hash = lrpc_def.definition_hash() or ""
        lrpc_version = version("lotusrpc")

        response = self.make_version_response(def_version, def_hash, lrpc_version)
        client = self.client(response)
        server_ok = client.check_server_version()

        assert not server_ok
        assert len(caplog.messages) == 4
        assert "Server mismatch detected. Details client vs server:" in caplog.messages
        assert f"LotusRPC version: {lrpc_version} vs {lrpc_version}" in caplog.messages
        assert "Definition version: [disabled] vs [wrong version]" in caplog.messages
        assert "Definition hash: 686d3ba44ae73e14... vs 686d3ba44ae73e14..." in caplog.messages
