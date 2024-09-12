from typing import List, Set

from lrpc.core import LrpcDef, LrpcEnum, LrpcEnumField
from lrpc import LrpcVisitor

class EnumChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.enum_ids: Set = set()
        self.enum_names: Set[str] = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.errors.clear()
        self.warnings.clear()
        self.enum_ids.clear()
        self.enum_names.clear()

    def visit_lrpc_enum(self, enum: LrpcEnum):
        self.enum_ids.clear()
        self.enum_names.clear()

    def visit_lrpc_enum_field(self, enum: LrpcEnum, field: LrpcEnumField):
        field_id = field.id()
        name = field.name()

        if field_id in self.enum_ids:
            self.errors.append(f'Duplicate field id in enum {enum.name()}: {field_id}')

        if name in self.enum_names:
            self.errors.append(f'Duplicate field name in enum {enum.name()}: {name}')

        self.enum_ids.add(field_id)
        self.enum_names.add(name)
