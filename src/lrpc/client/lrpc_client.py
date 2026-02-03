import logging
import struct
from collections.abc import Generator
from dataclasses import dataclass
from importlib.metadata import version
from typing import cast

from lrpc.core import LrpcFun, LrpcService, LrpcStream, LrpcVar
from lrpc.core.definition import LrpcDef
from lrpc.core.meta import MetaVersionResponseDict, MetaVersionResponseValidator
from lrpc.types import LrpcType
from lrpc.types.lrpc_type import LrpcResponseType

from .decoder import LrpcDecoder
from .encoder import lrpc_encode
from .transport import LrpcTransport

LrpcResponsePayload = dict[str, LrpcResponseType]


@dataclass
class LrpcResponse:
    service_name: str
    function_or_stream_name: str
    is_function_response: bool
    is_stream_response: bool
    is_error_response: bool
    is_expected_response: bool
    payload: LrpcResponsePayload


class LrpcClient:
    LRPC_MESSAGE_MIN_LENGTH = 3

    # This class is just a tag to signal a kind of result from the process function
    # pylint: disable=too-few-public-methods
    class IncompleteResponse:
        pass

    def __init__(self, lrpc_def: LrpcDef, transport: LrpcTransport) -> None:
        self._transport = transport
        self._lrpc_def = lrpc_def
        self._receive_buffer = b""
        self._current_service: str = ""
        self._current_function_or_stream: str = ""
        self._log = logging.getLogger(self.__class__.__name__)

    def check_server_version(self) -> bool:
        disabled = "[disabled]"
        client_side_lrpc_version = version("lotusrpc")
        client_side_def_hash = self._lrpc_def.definition_hash() or disabled
        client_side_def_version = self._lrpc_def.version() or disabled

        def get_server_version() -> MetaVersionResponseDict:
            version_response = self.communicate_single("LrpcMeta", "version").payload
            MetaVersionResponseValidator.validate_python(version_response, strict=True, extra="forbid")
            return cast(MetaVersionResponseDict, version_response)

        version_response = get_server_version()

        server_side_def_hash = version_response["definition_hash"]
        server_side_def_version = version_response["definition"] or disabled
        server_side_lrpc_version = version_response["lrpc"] or disabled

        def_hash_mismatch = client_side_def_hash != server_side_def_hash
        def_version_mismatch = client_side_def_version != server_side_def_version
        lrpc_version_mismatch = client_side_lrpc_version != server_side_lrpc_version

        if def_hash_mismatch or lrpc_version_mismatch or def_version_mismatch:
            self._log.warning("Server mismatch detected. Details client vs server:")
            self._log.warning("LotusRPC version: %s vs %s", client_side_lrpc_version, server_side_lrpc_version)
            self._log.warning("Definition version: %s vs %s", client_side_def_version, server_side_def_version)
            self._log.warning("Definition hash: %s... vs %s...", client_side_def_hash[:16], server_side_def_hash[:16])
            return False

        return True

    def _is_error_response(self, service: LrpcService, function_or_stream: LrpcFun | LrpcStream) -> bool:
        return (service.name() == self._lrpc_def.meta_service().name()) and (function_or_stream.name() == "error")

    def _is_expected_response(self, service: LrpcService, function_or_stream: LrpcFun | LrpcStream) -> bool:
        return (service.name() == self._current_service) and (
            function_or_stream.name() == self._current_function_or_stream
        )

    def _make_response(
        self,
        service: LrpcService,
        function_or_stream: LrpcFun | LrpcStream,
        payload: LrpcResponsePayload,
    ) -> LrpcResponse:
        is_expected = False
        is_error = self._is_error_response(service, function_or_stream)

        if is_error:
            self._log.warning(
                "Server reported error '%s' for call to %s.%s",
                payload["type"],
                self._current_service,
                self._current_function_or_stream,
            )
        else:
            is_expected = self._is_expected_response(service, function_or_stream)
            if not is_expected:
                self._log.warning(
                    "Unexpected response. Expected %s.%s, but got %s.%s",
                    self._current_service,
                    self._current_function_or_stream,
                    service.name(),
                    function_or_stream.name(),
                )

        return LrpcResponse(
            service_name=service.name(),
            function_or_stream_name=function_or_stream.name(),
            is_function_response=isinstance(function_or_stream, LrpcFun),
            is_stream_response=isinstance(function_or_stream, LrpcStream),
            is_error_response=is_error,
            is_expected_response=is_expected,
            payload=payload,
        )

    def decode(self, encoded: bytes) -> LrpcResponse:
        if len(encoded) < self.LRPC_MESSAGE_MIN_LENGTH:
            raise ValueError(f"Unable to decode message from {encoded!r}: an LRPC message has at least 3 bytes")

        message_size = encoded[0]
        service_id = encoded[1]
        function_or_stream_id = encoded[2]

        if message_size != len(encoded):
            raise ValueError(f"Incorrect message size. Expected {message_size} but got {len(encoded)}")

        service = self._lrpc_def.service_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found in the LRPC definition file")

        function = service.function_by_id(function_or_stream_id)
        stream = service.stream_by_id(function_or_stream_id)

        decoder = LrpcDecoder(encoded[3:], self._lrpc_def)

        if function:
            payload = self._decode_variables(function.returns(), decoder, f"{service.name()}.{function.name()}")
            return self._make_response(service, function, payload)

        if stream:
            payload = self._decode_variables(stream.returns(), decoder, f"{service.name()}.{stream.name()}")
            return self._make_response(service, stream, payload)

        raise ValueError(f"No function or stream with ID {function_or_stream_id} found in service {service.name()}")

    def encode(self, service_name: str, function_or_stream_name: str, **kwargs: LrpcType) -> bytes:
        service = self._lrpc_def.service_by_name(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found in the LRPC definition file")

        fun = service.function_by_name(function_or_stream_name)
        if fun:
            return self._encode_function(service, fun, **kwargs)

        stream = service.stream_by_name(function_or_stream_name)
        if stream:
            return self._encode_stream(service, stream, **kwargs)

        raise ValueError(f"Function or stream {function_or_stream_name} not found in service {service_name}")

    def communicate(
        self,
        service_name: str,
        function_or_stream_name: str,
        **kwargs: LrpcType,
    ) -> Generator[LrpcResponse, None, None]:
        self._current_service = service_name
        self._current_function_or_stream = function_or_stream_name

        encoded = self.encode(service_name, function_or_stream_name, **kwargs)
        self._transport.write(encoded)

        start_param = ("start" in kwargs) and (kwargs["start"] is True)

        receive_more = self._has_response(service_name, function_or_stream_name, start_param=start_param)
        while receive_more:
            response = self._receive_response()

            if self._lrpc_def.function(service_name, function_or_stream_name) is not None:
                receive_more = False
            else:
                stream = self._lrpc_def.stream(service_name, function_or_stream_name)
                if stream is None:
                    raise ValueError(
                        f"{service_name}.{function_or_stream_name} is not recognized as function or stream",
                    )
                if stream.is_finite():
                    receive_more = response.payload["final"] is False
                    response.payload.pop("final")

            yield response

    def communicate_single(
        self,
        service_name: str,
        function_or_stream_name: str,
        **kwargs: LrpcType,
    ) -> LrpcResponse:
        return next(self.communicate(service_name, function_or_stream_name, **kwargs))

    def _has_response(self, service_name: str, function_or_stream_name: str, *, start_param: bool) -> bool:
        function = self._lrpc_def.function(service_name, function_or_stream_name)
        stream = self._lrpc_def.stream(service_name, function_or_stream_name)

        if function is not None:
            return True

        if stream is not None:
            if stream.origin() == LrpcStream.Origin.CLIENT:
                return False

            # if start parameter is True, a response is expected
            return start_param

        raise ValueError(f"Function or stream {function_or_stream_name} not found in service {service_name}")

    def _decode_response(self, encoded: bytes) -> LrpcResponse | IncompleteResponse:
        self._receive_buffer += encoded
        received = len(self._receive_buffer)

        message_length = self._receive_buffer[0]

        if received >= message_length:
            result = self.decode(self._receive_buffer[0:message_length])
            self._receive_buffer = self._receive_buffer[message_length + 1 :]
            return result

        return LrpcClient.IncompleteResponse()

    def _encode_function(self, service: LrpcService, function: LrpcFun, **kwargs: LrpcType) -> bytes:
        self._check_parameters(function.param_names(), list(kwargs.keys()))
        encoded = self._encode_parameters(service, function, **kwargs)
        return self._add_message_length(encoded)

    def _encode_stream(self, service: LrpcService, stream: LrpcStream, **kwargs: LrpcType) -> bytes:
        self._check_parameters(stream.param_names(), list(kwargs.keys()))
        encoded = self._encode_parameters(service, stream, **kwargs)
        return self._add_message_length(encoded)

    def _receive_response(self) -> LrpcResponse:
        while True:
            received = self._transport.read(1)
            if len(received) == 0:
                raise TimeoutError("Timeout waiting for response")

            response = self._decode_response(received)

            if not isinstance(response, LrpcClient.IncompleteResponse):
                return response

    @staticmethod
    def _decode_variables(variables: list[LrpcVar], decoder: LrpcDecoder, name: str) -> LrpcResponsePayload:
        ret = {}

        for r in variables:
            ret[r.name()] = decoder.lrpc_decode(r)

        if decoder.remaining() != 0:
            raise ValueError(f"{decoder.remaining()} remaining bytes after decoding {name}")

        return ret

    @staticmethod
    def _check_parameters(
        required_params: list[str],
        given_params: list[str],
    ) -> None:
        too_many = set(given_params) - set(required_params)
        if len(too_many) != 0:
            raise ValueError(f"No such parameter(s): {too_many}")

        not_enough = set(required_params) - set(given_params)
        if len(not_enough) != 0:
            raise ValueError(f"Required parameter(s) {not_enough} not given")

    def _encode_parameters(
        self,
        service: LrpcService,
        function_or_stream: LrpcFun | LrpcStream,
        **kwargs: LrpcType,
    ) -> bytes:
        encoded = struct.pack("<B", service.id())
        encoded += struct.pack("<B", function_or_stream.id())

        for param_name, param_value in kwargs.items():
            param = function_or_stream.param(param_name)
            encoded += lrpc_encode(param_value, param, self._lrpc_def)

        return encoded

    @staticmethod
    def _add_message_length(encoded: bytes) -> bytes:
        return struct.pack("<B", len(encoded) + 1) + encoded
