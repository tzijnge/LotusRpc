from LrpcVar import LrpcVar
from abc import ABC

class LrpcVisitor(ABC):
    def visit_lrpc_def(self, lrpc_def):
        pass

    def visit_lrpc_def_end(self):
        pass

    def visit_lrpc_service(self, service):
        pass
    
    def visit_lrpc_service_end(self):
        pass

    def visit_lrpc_struct(self, struct):
        pass

    def visit_lrpc_struct_end(self):
        pass

    def visit_lrpc_struct_field(self, field: LrpcVar):
        pass

    def visit_lrpc_enum(self, enum):
        pass

    def visit_lrpc_enum_end(self):
        pass

    def visit_lrpc_enum_field(self, field):
        pass

    def visit_lrpc_constants(self):
        pass

    def visit_lrpc_constant(self, constant):
        pass

    def visit_lrpc_constants_end(self):
        pass

    def visit_lrpc_function(self, function):
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