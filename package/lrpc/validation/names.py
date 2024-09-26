from .validator import LrpcValidator
from ..core import LrpcConstant, LrpcDef, LrpcEnum, LrpcService, LrpcStruct


class NamesValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.__names: set[str] = set()

    def errors(self) -> list[str]:
        return self.__errors

    def warnings(self) -> list[str]:
        return self.__warnings

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__names.clear()
        self.__names.add(lrpc_def.name())

    def __check(self, name: str) -> None:
        if name in self.__names:
            self.__errors.append(f"Duplicate name: {name}")

        self.__names.add(name)

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self.__check(struct.name())

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self.__check(enum.name())

    def visit_lrpc_service(self, service: LrpcService) -> None:
        # A top-level item with the same name as the service is
        # not strictly a problem, because the generated class
        # has the word 'ServiceShim' appended. But it is confusing
        # and therefore both are treated as an invalid name
        self.__check(service.name())
        self.__check(service.name() + "ServiceShim")

    def visit_lrpc_constant(self, constant: LrpcConstant) -> None:
        self.__check(constant.name())
