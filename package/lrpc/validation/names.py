from lrpc.core import LrpcStruct, LrpcService, LrpcConstant, LrpcEnum
from lrpc.LrpcVisitor import LrpcVisitor
from typing import Set, List

class NamesChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors: List[str] = list()
        self.names: Set[str] = set()

    def __check(self, name: str):
        if name in self.names:
            self.errors.append(f'Duplicate name: {name}')

        self.names.add(name)

    def visit_lrpc_struct(self, struct: LrpcStruct):
        self.__check(struct.name())

    def visit_lrpc_enum(self, enum: LrpcEnum):
        self.__check(enum.name())

    def visit_lrpc_service(self, service: LrpcService):
        self.__check(service.name())

    def visit_lrpc_constant(self, constant: LrpcConstant):
        self.__check(constant.name())