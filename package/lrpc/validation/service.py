from lrpc.core import LrpcDef, LrpcService
from lrpc.LrpcVisitor import LrpcVisitor

class ServiceChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors = list()
        self.warnings = list()
        self.service_ids = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.errors.clear()
        self.warnings.clear()
        self.service_ids.clear()

    def visit_lrpc_service(self, service: LrpcService):
        id = service.id()

        if id in self.service_ids:
            self.errors.append(f'Duplicate service id: {id}')

        self.service_ids.add(id)