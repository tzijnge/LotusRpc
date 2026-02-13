import re
import struct
import sys
from importlib.metadata import version
from pathlib import Path

import pytest

from lrpc.client import LrpcClient
from lrpc.utils import load_lrpc_def_from_url

if sys.version_info >= (3, 12):
    import array


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

    def test_encode_function_bytearray(self) -> None:
        encoded = self.client().encode("srv1", "bytearray", p0=b"\x11\x22")
        assert encoded == b"\x06\x01\x02\x02\x11\x22"

        encoded = self.client().encode("srv1", "bytearray", p0=bytearray(b"\x11\x22"))
        assert encoded == b"\x06\x01\x02\x02\x11\x22"

        encoded = self.client().encode("srv1", "bytearray", p0=memoryview(b"\x11\x22"))
        assert encoded == b"\x06\x01\x02\x02\x11\x22"

        if sys.version_info >= (3, 12):
            arr = array.array("i", [0x11223344, 0x55667788])
            encoded = self.client().encode("srv1", "bytearray", p0=arr)
            assert encoded == b"\x0c\x01\x02\x08\x44\x33\x22\x11\x88\x77\x66\x55"

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

    def test_communicate_function_bytearray(self) -> None:
        response_bytes = b"\x06\x01\x02\x02\x33\x44"
        response = self.client(response_bytes).communicate_single("srv1", "bytearray", p0=b"\x11\x22")
        payload = response.payload

        assert "r0" in payload
        assert isinstance(payload["r0"], bytes)
        assert payload["r0"] == b"\x33\x44"

        assert response.is_error_response is False
        assert response.is_expected_response
        assert response.is_function_response
        assert response.is_stream_response is False
        assert response.service_name == "srv1"
        assert response.function_or_stream_name == "bytearray"

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
        assert "Definition hash: 03fca218c9a57417... vs [wrong hash]..." in caplog.messages

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
        assert "Definition hash: 03fca218c9a57417... vs 03fca218c9a57417..." in caplog.messages

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
        assert "Definition hash: 03fca218c9a57417... vs 03fca218c9a57417..." in caplog.messages

    def test_from_server_when_not_embedded(self) -> None:
        # meta.definition message with empty bytearray chunk param. final=True
        definition_response = b"\x05\xff\x01\x00\x01"

        transport = FakeTransport(definition_response)

        with pytest.raises(ValueError, match="No embedded definition found on server"):
            LrpcClient.from_server(transport)

    def test_from_server(self) -> None:
        # meta.definition message with definition from TestRetrieveDefinition.lrpc.yaml
        definition_response = b""
        definition_response += b"\x15\xff\x01\x10\xfd\x37\x7a\x58\x5a\x00\x00\x04\xe6\xd6\xb4\x46\x02\x00\x21\x01\x00"
        definition_response += b"\x15\xff\x01\x10\x16\x00\x00\x00\x74\x2f\xe5\xa3\xe0\x03\x98\x01\x64\x5d\x00\x37\x00"
        definition_response += b"\x15\xff\x01\x10\x18\x49\xfd\xfa\xfb\x56\x60\x9f\xc6\xef\x9a\xb1\x72\x37\x10\x50\x00"
        definition_response += b"\x15\xff\x01\x10\x15\xa2\x39\xaf\xd9\xf5\xfe\x63\x42\x9e\xd9\x48\x31\xe9\x89\x0d\x00"
        definition_response += b"\x15\xff\x01\x10\x78\xe5\x1b\x90\x10\x21\xe8\x03\x62\x22\xf2\x83\x2a\x2b\xed\x7e\x00"
        definition_response += b"\x15\xff\x01\x10\x4a\xad\xf8\x1c\xc4\x22\xda\x9f\xc3\xbc\xb7\xb0\x68\x37\xd5\x1e\x00"
        definition_response += b"\x15\xff\x01\x10\x95\x62\x29\x1b\x5d\x5a\xef\xc2\x07\xdf\x55\x7f\xc6\x1f\x28\x9f\x00"
        definition_response += b"\x15\xff\x01\x10\xbc\xda\x78\x17\x66\x0f\xdb\x8d\xf0\x66\x34\x56\xc6\xc5\x71\x06\x00"
        definition_response += b"\x15\xff\x01\x10\x19\x43\x6c\x4f\x19\x01\x4e\xd2\x80\x87\xe9\xda\xc4\xa4\xc1\xdf\x00"
        definition_response += b"\x15\xff\x01\x10\x29\x0b\x69\xb5\x42\xda\x59\x58\x1b\xb5\xec\x36\x3d\xf9\x92\x6f\x00"
        definition_response += b"\x15\xff\x01\x10\xc8\xd7\x63\x60\xb5\x20\x39\x41\x5e\x8f\x54\x17\x22\x84\xb3\x0d\x00"
        definition_response += b"\x15\xff\x01\x10\x1c\x1e\xe3\x58\x5a\x76\xc2\x0e\x7e\xb2\x8b\x10\xa4\x0c\xc3\x58\x00"
        definition_response += b"\x15\xff\x01\x10\x97\x76\xb5\x43\xc2\x04\xdf\x7a\xda\xd7\xe0\xa3\x74\x71\x39\x56\x00"
        definition_response += b"\x15\xff\x01\x10\xc4\x00\x37\xcc\x59\xdf\x46\xc4\x8e\xda\x6f\x0a\x52\xb5\xe2\xb1\x00"
        definition_response += b"\x15\xff\x01\x10\x2c\xb0\xc9\x0d\xc2\xd7\x68\xdc\x5d\xd4\x8a\xdc\x24\x5f\x4f\x30\x00"
        definition_response += b"\x15\xff\x01\x10\x85\x78\x7b\xd9\x9d\x58\x93\xfa\x23\x81\x90\xe7\xda\x45\xf7\xdf\x00"
        definition_response += b"\x15\xff\x01\x10\x52\x31\x20\x04\xda\x1a\x08\x03\x16\xcb\x60\x8e\xec\xce\x8e\x54\x00"
        definition_response += b"\x15\xff\x01\x10\xb6\x21\xd3\xd0\x7b\xc4\x8b\xbc\xbf\xb6\x3b\x6e\x03\xd7\x89\x75\x00"
        definition_response += b"\x15\xff\x01\x10\xec\x13\xe5\xc1\x68\xd9\xe0\x27\xe4\x83\x2f\x3d\x1c\x2d\xe0\x41\x00"
        definition_response += b"\x15\xff\x01\x10\x06\x3e\xbd\xa9\xf6\xd7\x35\x2a\x50\xa7\x2c\x97\x7d\x27\xb5\x1d\x00"
        definition_response += b"\x15\xff\x01\x10\xd2\x11\xe0\x8a\xa2\xc6\xf9\x88\x33\xaf\x1a\xcd\xba\x4d\x5e\x3c\x00"
        definition_response += b"\x15\xff\x01\x10\x05\x81\x6e\x43\x64\x8a\x6e\xb9\xed\x9b\x37\x1e\xdc\x20\xd1\x3f\x00"
        definition_response += b"\x15\xff\x01\x10\x99\x89\xf1\x35\x7a\x99\x44\x65\x05\x84\xeb\x46\xbd\xa3\xbf\x08\x00"
        definition_response += b"\x15\xff\x01\x10\x8a\xb3\x6c\x41\x48\x1d\xc3\x4d\x6e\x89\x7b\xdf\xc4\x3a\xca\xec\x00"
        definition_response += b"\x15\xff\x01\x10\x51\x6b\x00\x00\x81\xd8\x95\x64\xb5\x6d\x99\x56\x00\x01\x80\x03\x00"
        definition_response += b"\x15\xff\x01\x10\x99\x07\x00\x00\x7e\x02\x42\x5f\xb1\xc4\x67\xfb\x02\x00\x00\x00\x00"
        definition_response += b"\x09\xff\x01\x04\x00\x04\x59\x5a\x01"

        transport = FakeTransport(definition_response)

        client = LrpcClient.from_server(transport)

        definition = client.definition()

        assert definition.name() == "RetrieveDefinition"
        assert definition.namespace() == "test_rd"
        assert definition.tx_buffer_size() == 47
        assert definition.embed_definition() is True
        assert len(definition.services()) == 1
        s0 = definition.service_by_id(0)
        assert s0 is not None
        assert s0.name() == "s0"
