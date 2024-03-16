from lrpc.core import LrpcDef, LrpcService
from lrpc.LrpcVisitor import LrpcVisitor

class DuplicateServiceIdChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.service_ids = list()
        self.duplicate_ids = list()

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.service_ids = list()
        self.duplicate_ids = list()

    def visit_lrpc_service(self, service: LrpcService):
        id = service.id()
        if id in self.service_ids:
            self.duplicate_ids.append(id)
        else:
            self.service_ids.append(id)

    def error(self):
        if len(self.duplicate_ids) > 0:
            return f'Duplicate service id(s): {self.duplicate_ids}'
        else:
            return None