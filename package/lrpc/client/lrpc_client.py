import struct

from lrpc.core import LrpcDef
from lrpc.client import lrpc_encode

class LrpcClient(object):
    def __init__(self, lrpc_def: LrpcDef) -> None:
        self.lrpc_def = lrpc_def

    def call(self, service_name: str, function_name: str, **kwargs):
        if kwargs is None:
            kwargs = {}

        service = self.lrpc_def.service(service_name)
        if not service:
            raise ValueError(f'Service {service_name} not found in the LRPC definition file')

        fun = service.function(function_name)
        if not fun:
            raise ValueError(f'Function {function_name} not found in the service {service_name}')

        given_params = kwargs.keys()
        required_params = fun.param_names()

        too_many = given_params - required_params
        if len(too_many) != 0:
            raise ValueError(f'Given parameter(s) {too_many} not found in the parameters of function {function_name}')

        not_enough = required_params - given_params
        if len(not_enough) != 0:
            raise ValueError(f'Required parameter(s) {not_enough} not given')

        encoded = struct.pack('<B', service.id())
        encoded += struct.pack('<B', fun.id())

        for param_name, param_value in kwargs.items():
            param = fun.param(param_name)
            if not param:
                raise ValueError(f'Parameter {param_name} not found in the LRPC definition file')

            encoded += lrpc_encode(param_value, param, self.lrpc_def)

        return encoded
