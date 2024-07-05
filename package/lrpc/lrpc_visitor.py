from abc import ABC

class LrpcVisitor(ABC):
    '''Called before visiting the LRPC definition'''
    def visit_lrpc_def(self, lrpc_def: 'LrpcDef') -> None:
        pass

    '''Called after visiting the LRPC definition'''
    def visit_lrpc_def_end(self) -> None:
        pass

    '''Called before each service in the LRPC definition'''
    def visit_lrpc_service(self, service: 'LrpcService') -> None:
        pass

    '''Called after each service  in the LRPC definition'''
    def visit_lrpc_service_end(self) -> None:
        pass

    '''Called before each struct in the LRPC definition. All
    structs are visited before the first service'''
    def visit_lrpc_struct(self, struct: 'LrpcStruct') -> None:
        pass

    '''Called after visiting each field of the current struct'''
    def visit_lrpc_struct_end(self) -> None:
        pass

    '''Called for each field in the current struct'''
    def visit_lrpc_struct_field(self, field: 'LrpcVar') -> None:
        pass

    '''Called before each enum in the LRPC definition. All
    enums are visited before the first service'''
    def visit_lrpc_enum(self, enum: 'LrpcEnum') -> None:
        pass

    '''Called after visiting each field of the current enum'''
    def visit_lrpc_enum_end(self, enum: 'LrpcEnum') -> None:
        pass

    '''Called for each field in the current enum'''
    def visit_lrpc_enum_field(self, enum: 'LrpcEnum', field: 'LrpcEnumField') -> None:
        pass

    '''Called before visiting the constants in the LRPC definition. All
    constants are visited before the first service'''
    def visit_lrpc_constants(self) -> None:
        pass

    '''Called for each constant in the LRPC definition'''
    def visit_lrpc_constant(self, constant: 'LrpcVar') -> None:
        pass

    '''Called after visiting the constants in the LRPC definition'''
    def visit_lrpc_constants_end(self) -> None:
        pass

    '''Called for each function in the current service'''
    def visit_lrpc_function(self, function: 'LrpcFun') -> None:
        pass

    '''Called after visiting all parameters and returns of the current function'''
    def visit_lrpc_function_end(self) -> None:
        pass

    '''Called for each return of the current function'''
    def visit_lrpc_function_return(self, ret: 'LrpcVar') -> None:
        pass

    '''Called after visiting all returns of the current function'''
    def visit_lrpc_function_return_end(self) -> None:
        pass

    '''Called for each parameter of the current function'''
    def visit_lrpc_function_param(self, param: 'LrpcVar') -> None:
        pass

    '''Called after visiting all parameters of the current function'''
    def visit_lrpc_function_param_end(self) -> None:
        pass