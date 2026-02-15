from lrpc.core import LrpcConstant, LrpcDef, LrpcEnum, LrpcService, LrpcStruct

from .validator import LrpcValidator


class NamesValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self._names: set[str] = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.reset()
        self._names.clear()
        self._names.add(lrpc_def.name())

    def _check(self, name: str) -> None:
        if name in self._names:
            self.add_error(f"Duplicate name: {name}")

        self._names.add(name)

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self._check(struct.name())

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self._check(enum.name())

    def visit_lrpc_service(self, service: LrpcService) -> None:
        # A top-level item with the same name as the service is
        # not strictly a problem, because the generated class
        # has the word 'ServiceShim' appended. But it is confusing
        # and therefore both are treated as an invalid name
        self._check(service.name())
        self._check(service.name() + "ServiceShim")

    def visit_lrpc_constant(self, constant: LrpcConstant) -> None:
        self._check(constant.name())
