from ..core import LrpcDef, LrpcStruct, LrpcVar
from .validator import LrpcValidator


class StructValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.__struct_names: set[str] = set()

    def errors(self) -> list[str]:
        return self.__errors

    def warnings(self) -> list[str]:
        return self.__warnings

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__struct_names.clear()

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self.__struct_names.clear()

    def visit_lrpc_struct_field(self, struct: LrpcStruct, field: LrpcVar) -> None:
        name = field.name()

        if name in self.__struct_names:
            self.__errors.append(f"Duplicate field name in struct {struct.name()}: {name}")

        self.__struct_names.add(name)
