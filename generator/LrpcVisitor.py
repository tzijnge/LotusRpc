from LrpcDefBase import LrpcDefBase
from LrpcStructBase import LrpcStructBase
from LrpcFunBase import LrpcFunBase
from LrpcConstantBase import LrpcConstantBase
from LrpcEnumBase import LrpcEnumBase, LrpcEnumFieldBase
from LrpcServiceBase import LrpcServiceBase
from LrpcVar import LrpcVar
from abc import ABC

class LrpcVisitor(ABC):
    def visit_lrpc_def(self, lrpc_def: LrpcDefBase):
        pass

    def visit_lrpc_def_end(self):
        pass

    def visit_lrpc_service(self, service: LrpcServiceBase):
        pass
    
    def visit_lrpc_service_end(self):
        pass

    def visit_lrpc_struct(self, struct: LrpcStructBase):
        pass

    def visit_lrpc_struct_end(self):
        pass

    def visit_lrpc_struct_field(self, field: LrpcVar):
        pass

    def visit_lrpc_enum(self, enum: LrpcEnumBase):
        pass

    def visit_lrpc_enum_end(self):
        pass

    def visit_lrpc_enum_field(self, field: LrpcEnumFieldBase):
        pass

    def visit_lrpc_constant(self, constant: LrpcConstantBase):
        pass

    def visit_lrpc_constant_end(self):
        pass

    def visit_lrpc_function(self, function: LrpcFunBase):
        pass

    def visit_lrpc_function_end(self):
        pass

    def visit_lrpc_function_return(self, ret: LrpcVar):
        pass

    def visit_lrpc_function_return_end(self):
        pass

    def visit_lrpc_function_param(self, param: LrpcVar):
        pass

    def visit_lrpc_function_param_end(self):
        pass