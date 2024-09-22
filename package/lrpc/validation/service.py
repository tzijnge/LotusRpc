from lrpc.core import LrpcDef, LrpcService
from lrpc import LrpcVisitor


class ServiceChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.service_ids: set[int] = set()

    def visit_lrpc_def(self, _: LrpcDef) -> None:
        self.errors.clear()
        self.warnings.clear()
        self.service_ids.clear()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        service_id = service.id()

        if service_id in self.service_ids:
            self.errors.append(f"Duplicate service id: {service_id}")

        self.service_ids.add(service_id)
