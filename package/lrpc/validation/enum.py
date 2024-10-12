from ..core import LrpcDef, LrpcEnum, LrpcEnumField
from .validator import LrpcValidator


class EnumValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.__enum_ids: set[int] = set()
        self.__enum_names: set[str] = set()

    def errors(self) -> list[str]:
        return self.__errors

    def warnings(self) -> list[str]:
        return self.__warnings

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__enum_ids.clear()
        self.__enum_names.clear()

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self.__enum_ids.clear()
        self.__enum_names.clear()

    def visit_lrpc_enum_field(self, enum: LrpcEnum, field: LrpcEnumField) -> None:
        field_id = field.id()
        name = field.name()

        if field_id in self.__enum_ids:
            self.__errors.append(f"Duplicate field id in enum {enum.name()}: {field_id}")

        if name in self.__enum_names:
            self.__errors.append(f"Duplicate field name in enum {enum.name()}: {name}")

        self.__enum_ids.add(field_id)
        self.__enum_names.add(name)
