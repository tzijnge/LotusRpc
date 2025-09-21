import struct
from typing import Any, Union

from ..core.definition import LrpcDef
from ..core import LrpcService, LrpcFun, LrpcStream
from .decoder import LrpcDecoder
from .encoder import lrpc_encode


class LrpcClient:
    # This class is just a tag to signal a kind of result from the process function
    # pylint: disable=too-few-public-methods
    class IncompleteResponse:
        pass

    def __init__(self, lrpc_def: LrpcDef) -> None:
        self.lrpc_def = lrpc_def
        self.receive_buffer = b""

    def process(self, encoded: bytes) -> Union[dict[str, Any], IncompleteResponse]:
        self.receive_buffer += encoded
        received = len(self.receive_buffer)

        if received == 0:
            return LrpcClient.IncompleteResponse()

        message_length = self.receive_buffer[0]

        if received >= message_length:
            result = self.decode(self.receive_buffer[0:message_length])
            self.receive_buffer = self.receive_buffer[message_length + 1 :]
            return result

        return LrpcClient.IncompleteResponse()

    def decode(self, encoded: bytes) -> dict[str, Any]:
        if len(encoded) < 3:
            raise ValueError(f"Unable to decode message from {encoded!r}: an LRPC message has at least 3 bytes")

        message_size = encoded[0]
        service_id = encoded[1]
        function_or_stream_id = encoded[2]

        if message_size != len(encoded):
            raise ValueError(f"Incorrect message size. Expected {message_size} but got {len(encoded)}")

        if (service_id == 255) and (function_or_stream_id == 0):
            raise ValueError("The LRPC server reported an error")

        service = self.lrpc_def.service_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found in the LRPC definition file")

        function = service.function_by_id(function_or_stream_id)
        stream = service.stream_by_id(function_or_stream_id)

        decoder = LrpcDecoder(encoded[3:], self.lrpc_def)

        if function:
            return self._decode_function(function, decoder, service.name())

        if stream:
            return self._decode_stream(stream, decoder, service.name())

        raise ValueError(f"No function or stream with ID {function_or_stream_id} found in service {service.name()}")

    def encode(self, service_name: str, function_or_stream_name: str, **kwargs: Any) -> bytes:
        service = self.lrpc_def.service_by_name(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found in the LRPC definition file")

        fun = service.function_by_name(function_or_stream_name)
        if fun:
            return self._encode_function(service, fun, **kwargs)

        stream = service.stream_by_name(function_or_stream_name)
        if stream:
            return self._encode_stream(service, stream, **kwargs)

        raise ValueError(f"Function or stream {function_or_stream_name} not found in service {service_name}")

    def has_response(self, service_name: str, function_or_stream_name: str, **kwargs: Any) -> bool:
        service = self.lrpc_def.service_by_name(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found in the LRPC definition file")

        fun = service.function_by_name(function_or_stream_name)
        if fun:
            return True

        stream = service.stream_by_name(function_or_stream_name)
        if stream:
            if stream.origin() == LrpcStream.Origin.CLIENT:
                return False

            if ("start" in kwargs) and (kwargs["start"] is False):
                return False

            return True

        raise ValueError(f"Function or stream {function_or_stream_name} not found in service {service_name}")

    @staticmethod
    def _decode_function(function: LrpcFun, decoder: LrpcDecoder, service_name: str) -> dict[str, Any]:
        if function.number_returns() == 0:
            return {}

        ret = {}
        for r in function.returns():
            ret[r.name()] = decoder.lrpc_decode(r)

        if decoder.remaining() != 0:
            raise ValueError(
                f"{decoder.remaining()} remaining bytes after decoding function {service_name}.{function.name()}"
            )

        return ret

    @staticmethod
    def _decode_stream(stream: LrpcStream, decoder: LrpcDecoder, service_name: str) -> dict[str, Any]:
        ret = {}
        for r in stream.returns():
            ret[r.name()] = decoder.lrpc_decode(r)

        if decoder.remaining() != 0:
            raise ValueError(
                f"{decoder.remaining()} remaining bytes after decoding stream {service_name}.{stream.name()}"
            )

        return ret

    def _encode_function(self, service: LrpcService, function: LrpcFun, **kwargs: Any) -> bytes:
        self._check_parameters(function.param_names(), list(kwargs.keys()))
        encoded = self._encode_parameters(service, function, **kwargs)
        return self._add_message_length(encoded)

    def _encode_stream(self, service: LrpcService, stream: LrpcStream, **kwargs: Any) -> bytes:
        self._check_parameters(stream.param_names(), list(kwargs.keys()))
        encoded = self._encode_parameters(service, stream, **kwargs)
        return self._add_message_length(encoded)

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
        **kwargs: Any,
    ) -> bytes:
        encoded = struct.pack("<B", service.id())
        encoded += struct.pack("<B", function_or_stream.id())

        for param_name, param_value in kwargs.items():
            param = function_or_stream.param(param_name)
            encoded += lrpc_encode(param_value, param, self.lrpc_def)

        return encoded

    @staticmethod
    def _add_message_length(encoded: bytes) -> bytes:
        return struct.pack("<B", len(encoded) + 1) + encoded
