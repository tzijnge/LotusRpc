from lrpc.core import LrpcDef, LrpcEnum, LrpcStruct, LrpcVar
from lrpc import LrpcVisitor


class CustomTypesChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors: set[str] = set()
        self.warnings: set[str] = set()
        self.declared_custom_types: set[str] = set()
        self.used_custom_types: set[str] = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.errors.clear()
        self.warnings.clear()
        self.declared_custom_types.clear()
        self.used_custom_types.clear()

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self.declared_custom_types.add(enum.name())

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self.declared_custom_types.add(struct.name())

    def __handle_used_type(self, lrpc_var: LrpcVar) -> None:
        if not lrpc_var.base_type_is_custom():
            return

        self.used_custom_types.add(lrpc_var.base_type())

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.__handle_used_type(ret)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.__handle_used_type(param)

    def visit_lrpc_struct_field(self, field: LrpcVar) -> None:
        self.__handle_used_type(field)

    def visit_lrpc_def_end(self) -> None:
        for undeclared_custom_type in self.used_custom_types - self.declared_custom_types:
            self.errors.add(f"Undeclared custom type: {undeclared_custom_type}")
        for unused_custom_type in self.declared_custom_types - self.used_custom_types:
            self.warnings.add(f"Unused custom type: {unused_custom_type}")
