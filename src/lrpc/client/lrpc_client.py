import struct
from typing import Union, Generator

from ..core.definition import LrpcDef
from ..core import LrpcService, LrpcFun, LrpcStream, LrpcVar
from ..types import LrpcType
from .decoder import LrpcDecoder
from .encoder import lrpc_encode
from .transport import LrpcTransport

LrpcResponse = dict[str, LrpcType]


class LrpcClient:
    # This class is just a tag to signal a kind of result from the process function
    # pylint: disable=too-few-public-methods
    class IncompleteResponse:
        pass

    def __init__(self, lrpc_def: LrpcDef, transport: LrpcTransport) -> None:
        self._transport = transport
        self._lrpc_def = lrpc_def
        self._receive_buffer = b""

    def decode(self, encoded: bytes) -> LrpcResponse:
        if len(encoded) < 3:
            raise ValueError(f"Unable to decode message from {encoded!r}: an LRPC message has at least 3 bytes")

        message_size = encoded[0]
        service_id = encoded[1]
        function_or_stream_id = encoded[2]

        if message_size != len(encoded):
            raise ValueError(f"Incorrect message size. Expected {message_size} but got {len(encoded)}")

        if (service_id == 255) and (function_or_stream_id == 0):
            raise ValueError("The LRPC server reported an error")

        service = self._lrpc_def.service_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found in the LRPC definition file")

        function = service.function_by_id(function_or_stream_id)
        stream = service.stream_by_id(function_or_stream_id)

        decoder = LrpcDecoder(encoded[3:], self._lrpc_def)

        if function:
            return self._decode_variables(function.returns(), decoder, f"{service.name()}.{function.name()}")

        if stream:
            return self._decode_variables(stream.returns(), decoder, f"{service.name()}.{stream.name()}")

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
        self, service_name: str, function_or_stream_name: str, **kwargs: LrpcType
    ) -> Generator[LrpcResponse, None, None]:
        encoded = self.encode(service_name, function_or_stream_name, **kwargs)
        self._transport.write(encoded)

        start_param = ("start" in kwargs) and (kwargs["start"] is True)

        receive_more = self._has_response(service_name, function_or_stream_name, start_param)
        while receive_more:
            response = self._receive_response()

            if self._lrpc_def.function(service_name, function_or_stream_name) is not None:
                receive_more = False
            else:
                stream = self._lrpc_def.stream(service_name, function_or_stream_name)
                assert stream is not None
                if stream.is_finite():
                    receive_more = response["final"] is False
                    response.pop("final")

            yield response

    def _has_response(self, service_name: str, function_or_stream_name: str, start_param: bool) -> bool:
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

    def _decode_response(self, encoded: bytes) -> Union[LrpcResponse, IncompleteResponse]:
        assert len(encoded) != 0

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
    def _decode_variables(variables: list[LrpcVar], decoder: LrpcDecoder, name: str) -> LrpcResponse:
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
        function_or_stream: Union[LrpcFun, LrpcStream],
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
