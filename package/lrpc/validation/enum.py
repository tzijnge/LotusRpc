from lrpc.core import LrpcDef, LrpcEnumField
from lrpc.LrpcVisitor import LrpcVisitor

class EnumChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors = list()
        self.enum_ids = set()
        self.enum_names = set()
        self.current_enum_name = ""

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.errors.clear()
        self.enum_ids.clear()
        self.enum_names.clear()

    def visit_lrpc_enum(self, enum):
        self.current_enum_name = enum.name()
        self.enum_ids.clear()
        self.enum_names.clear()

    def visit_lrpc_enum_field(self, field: LrpcEnumField):
        id = field.id()
        name = field.name()

        if id in self.enum_ids:
            self.errors.append(f'Duplicate field id in enum {self.current_enum_name}: {id}')

        if name in self.enum_names:
            self.errors.append(f'Duplicate field name in enum {self.current_enum_name}: {name}')

        self.enum_ids.add(id)
        self.enum_names.add(name)