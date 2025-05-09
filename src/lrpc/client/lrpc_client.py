import struct
from typing import Any, Union

from ..core.definition import LrpcDef
from .decoder import LrpcDecoder
from .encoder import lrpc_encode


class LrpcClient:
    # These classes are just tags to signal a kind of result from the process function
    # pylint: disable=too-few-public-methods
    class VoidResponse:
        pass

    # pylint: disable=too-few-public-methods
    class IncompleteResponse:
        pass

    def __init__(self, lrpc_def: LrpcDef) -> None:
        self.lrpc_def = lrpc_def
        self.receive_buffer = b""

    def process(self, encoded: bytes) -> Union[dict[str, Any], VoidResponse, IncompleteResponse]:
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

    def decode(self, encoded: bytes) -> Union[dict[str, Any], VoidResponse]:
        if len(encoded) < 3:
            raise ValueError(f"Unable to decode message from {encoded!r}: an LRPC message has at least 3 bytes")

        # skip packet length at index 0
        service_id = encoded[1]
        function_id = encoded[2]

        if (service_id == 255) and (function_id == 0):
            raise ValueError("The LRPC server reported an error")

        service = self.lrpc_def.service_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found in the LRPC definition file")

        fun = service.function_by_id(function_id)
        if not fun:
            raise ValueError(f"Function with ID {function_id} not found in the service {service.name()}")

        decoder = LrpcDecoder(encoded[3:], self.lrpc_def)

        if fun.number_returns() == 0:
            return LrpcClient.VoidResponse()

        ret = {}
        for r in fun.returns():
            ret[r.name()] = decoder.lrpc_decode(r)

        return ret

    def encode(self, service_name: str, function_name: str, **kwargs: Any) -> bytes:
        service = self.lrpc_def.service_by_name(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found in the LRPC definition file")

        fun = service.function_by_name(function_name)
        if not fun:
            raise ValueError(f"Function {function_name} not found in the service {service_name}")

        given_params = kwargs.keys()
        required_params = fun.param_names()

        too_many = given_params - required_params
        if len(too_many) != 0:
            raise ValueError(f"Given parameter(s) {too_many} not found in function {function_name}")

        not_enough = required_params - given_params
        if len(not_enough) != 0:
            raise ValueError(f"Required parameter(s) {not_enough} not given")

        encoded = struct.pack("<B", service.id())
        encoded += struct.pack("<B", fun.id())

        for param_name, param_value in kwargs.items():
            param = fun.param(param_name)
            encoded += lrpc_encode(param_value, param, self.lrpc_def)

        return struct.pack("<B", len(encoded) + 1) + encoded
