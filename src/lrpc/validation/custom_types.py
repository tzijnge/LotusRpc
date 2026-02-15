from lrpc.core import LrpcDef, LrpcEnum, LrpcStruct, LrpcVar

from .validator import LrpcValidator


class CustomTypesValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self._declared_custom_types: set[str] = set()
        self._used_custom_types: set[str] = set()

    def visit_lrpc_def(self, _lrpc_def: LrpcDef) -> None:
        self.reset()
        self._declared_custom_types.clear()
        self._used_custom_types.clear()

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self._declared_custom_types.add(enum.name())

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self._declared_custom_types.add(struct.name())

    def _handle_used_type(self, lrpc_var: LrpcVar) -> None:
        if not lrpc_var.base_type_is_custom():
            return

        self._used_custom_types.add(lrpc_var.base_type())

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self._handle_used_type(ret)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self._handle_used_type(param)

    def visit_lrpc_struct_field(self, _struct: LrpcStruct, field: LrpcVar) -> None:
        self._handle_used_type(field)

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self._handle_used_type(param)

    def visit_lrpc_stream_return(self, ret: LrpcVar) -> None:
        self._handle_used_type(ret)

    def visit_lrpc_def_end(self) -> None:
        for undeclared_custom_type in self._used_custom_types - self._declared_custom_types:
            self.add_error(f"Undeclared custom type: {undeclared_custom_type}")
        for unused_custom_type in self._declared_custom_types - self._used_custom_types:
            self.add_warning(f"Unused custom type: {unused_custom_type}")
