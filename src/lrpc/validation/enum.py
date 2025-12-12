from ..core import LrpcDef, LrpcEnum, LrpcEnumField
from .validator import LrpcValidator


class EnumValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self.__enum_ids: set[int] = set()
        self.__enum_names: set[str] = set()

    def visit_lrpc_def(self, _lrpc_def: LrpcDef) -> None:
        self.reset()
        self.__enum_ids.clear()
        self.__enum_names.clear()

    def visit_lrpc_enum(self, _enum: LrpcEnum) -> None:
        self.__enum_ids.clear()
        self.__enum_names.clear()

    def visit_lrpc_enum_field(self, enum: LrpcEnum, field: LrpcEnumField) -> None:
        field_id = field.id()
        name = field.name()

        if field_id in self.__enum_ids:
            self.add_error(f"Duplicate field id in enum {enum.name()}: {field_id}")

        if name in self.__enum_names:
            self.add_error(f"Duplicate field name in enum {enum.name()}: {name}")

        self.__enum_ids.add(field_id)
        self.__enum_names.add(name)
