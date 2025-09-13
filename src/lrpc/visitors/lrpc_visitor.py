from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import (
        LrpcDef,
        LrpcService,
        LrpcStruct,
        LrpcVar,
        LrpcEnum,
        LrpcEnumField,
        LrpcFun,
        LrpcConstant,
        LrpcStream,
    )


# pylint: disable = too-many-public-methods
class LrpcVisitor(ABC):
    def visit_lrpc_def(self, lrpc_def: "LrpcDef") -> None:
        """Called before visiting the LRPC definition"""

    def visit_lrpc_def_end(self) -> None:
        """Called after visiting the LRPC definition"""

    def visit_lrpc_service(self, service: "LrpcService") -> None:
        """Called before each service in the LRPC definition"""

    def visit_lrpc_service_end(self) -> None:
        """Called after each service  in the LRPC definition"""

    def visit_lrpc_struct(self, struct: "LrpcStruct") -> None:
        """Called before each struct in the LRPC definition. All
        structs are visited before the first service"""

    def visit_lrpc_struct_end(self) -> None:
        """Called after visiting each field of the current struct"""

    def visit_lrpc_struct_field(self, struct: "LrpcStruct", field: "LrpcVar") -> None:
        """Called for each field in the current struct"""

    def visit_lrpc_enum(self, enum: "LrpcEnum") -> None:
        """Called before each enum in the LRPC definition. All
        enums are visited before the first service"""

    def visit_lrpc_enum_end(self, enum: "LrpcEnum") -> None:
        """Called after visiting each field of the current enum"""

    def visit_lrpc_enum_field(self, enum: "LrpcEnum", field: "LrpcEnumField") -> None:
        """Called for each field in the current enum"""

    def visit_lrpc_constants(self) -> None:
        """Called before visiting the constants in the LRPC definition. All
        constants are visited before the first service"""

    def visit_lrpc_constant(self, constant: "LrpcConstant") -> None:
        """Called for each constant in the LRPC definition"""

    def visit_lrpc_constants_end(self) -> None:
        """Called after visiting the constants in the LRPC definition"""

    def visit_lrpc_function(self, function: "LrpcFun") -> None:
        """Called for each function in the current service"""

    def visit_lrpc_function_end(self) -> None:
        """Called after visiting all parameters and returns of the current function"""

    def visit_lrpc_function_return(self, ret: "LrpcVar") -> None:
        """Called for each return of the current function"""

    def visit_lrpc_function_return_end(self) -> None:
        """Called after visiting all returns of the current function"""

    def visit_lrpc_function_param(self, param: "LrpcVar") -> None:
        """Called for each parameter of the current function"""

    def visit_lrpc_function_param_end(self) -> None:
        """Called after visiting all parameters of the current function"""

    def visit_lrpc_stream(self, stream: "LrpcStream") -> None:
        """Called for each stream in the current service"""

    def visit_lrpc_stream_param(self, param: "LrpcVar") -> None:
        """Called for each parameter of the current stream"""

    def visit_lrpc_stream_param_end(self) -> None:
        """Called after visiting all parameters of the current stream"""

    def visit_lrpc_stream_return(self, ret: "LrpcVar") -> None:
        """Called for each return of the current stream"""

    def visit_lrpc_stream_return_end(self) -> None:
        """Called after visiting all returns of the current stream"""

    def visit_lrpc_stream_end(self) -> None:
        """Called after visiting all parameters of the current stream"""
