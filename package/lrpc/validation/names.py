from lrpc import LrpcVisitor
from lrpc.core import LrpcConstant, LrpcDef, LrpcEnum, LrpcService, LrpcStruct


class NamesChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.names: set[str] = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.errors.clear()
        self.warnings.clear()
        self.names.clear()
        self.names.add(lrpc_def.name())

    def __check(self, name: str) -> None:
        if name in self.names:
            self.errors.append(f"Duplicate name: {name}")

        self.names.add(name)

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
