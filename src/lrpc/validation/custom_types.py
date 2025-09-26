from ..core import LrpcDef, LrpcEnum, LrpcStruct, LrpcVar
from .validator import LrpcValidator


class CustomTypesValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: set[str] = set()
        self.__warnings: set[str] = set()
        self.__declared_custom_types: set[str] = set()
        self.__used_custom_types: set[str] = set()

    def errors(self) -> list[str]:
        return list(self.__errors)

    def warnings(self) -> list[str]:
        return list(self.__warnings)

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__declared_custom_types.clear()
        self.__used_custom_types.clear()

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self.__declared_custom_types.add(enum.name())

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self.__declared_custom_types.add(struct.name())

    def __handle_used_type(self, lrpc_var: LrpcVar) -> None:
        if not lrpc_var.base_type_is_custom():
            return

        self.__used_custom_types.add(lrpc_var.base_type())

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.__handle_used_type(ret)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.__handle_used_type(param)

    def visit_lrpc_struct_field(self, struct: LrpcStruct, field: LrpcVar) -> None:
        self.__handle_used_type(field)

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self.__handle_used_type(param)

    def visit_lrpc_stream_return(self, ret: LrpcVar) -> None:
        self.__handle_used_type(ret)

    def visit_lrpc_def_end(self) -> None:
        for undeclared_custom_type in self.__used_custom_types - self.__declared_custom_types:
            self.__errors.add(f"Undeclared custom type: {undeclared_custom_type}")
        for unused_custom_type in self.__declared_custom_types - self.__used_custom_types:
            self.__warnings.add(f"Unused custom type: {unused_custom_type}")
