from lrpc.core import LrpcDef, LrpcEnum, LrpcEnumField
from lrpc import LrpcVisitor

class EnumChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors = list()
        self.warnings = list()
        self.enum_ids = set()
        self.enum_names = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.errors.clear()
        self.warnings.clear()
        self.enum_ids.clear()
        self.enum_names.clear()

    def visit_lrpc_enum(self, enum: LrpcEnum):
        self.enum_ids.clear()
        self.enum_names.clear()

    def visit_lrpc_enum_field(self, enum: LrpcEnum, field: LrpcEnumField):
        id = field.id()
        name = field.name()

        if id in self.enum_ids:
            self.errors.append(f'Duplicate field id in enum {enum.name()}: {id}')

        if name in self.enum_names:
            self.errors.append(f'Duplicate field name in enum {enum.name()}: {name}')

        self.enum_ids.add(id)
        self.enum_names.add(name)