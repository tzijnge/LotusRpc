from typing import List, Set

from lrpc.core import LrpcDef, LrpcService
from lrpc import LrpcVisitor


class ServiceChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.service_ids: Set[str] = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.errors.clear()
        self.warnings.clear()
        self.service_ids.clear()

    def visit_lrpc_service(self, service: LrpcService):
        service_id = service.id()

        if service_id in self.service_ids:
            self.errors.append(f"Duplicate service id: {service_id}")

        self.service_ids.add(service_id)
