from lrpc.core import LrpcDef, LrpcStruct, LrpcVar

from .validator import LrpcValidator


class StructValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self._struct_names: set[str] = set()

    def visit_lrpc_def(self, _lrpc_def: LrpcDef) -> None:
        self.reset()
        self._struct_names.clear()

    def visit_lrpc_struct(self, _struct: LrpcStruct) -> None:
        self._struct_names.clear()

    def visit_lrpc_struct_field(self, struct: LrpcStruct, field: LrpcVar) -> None:
        name = field.name()

        if name in self._struct_names:
            self.add_error(f"Duplicate field name in struct {struct.name()}: {name}")

        self._struct_names.add(name)
