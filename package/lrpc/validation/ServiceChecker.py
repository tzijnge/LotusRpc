from lrpc.core import LrpcDef, LrpcService
from lrpc.LrpcVisitor import LrpcVisitor

class ServiceChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors = list()
        self.service_ids = set()
        self.service_names = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.errors.clear()
        self.service_ids.clear()
        self.service_names.clear()

    def visit_lrpc_service(self, service: LrpcService):
        id = service.id()
        name = service.name()

        if id in self.service_ids:
            self.errors.append(f'Duplicate service id: {id}')

        if name in self.service_names:
            self.errors.append(f'Duplicate service name: {name}')

        self.service_ids.add(id)
        self.service_names.add(name)