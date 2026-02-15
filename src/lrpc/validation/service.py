from lrpc.core import LrpcDef, LrpcService

from .validator import LrpcValidator


class ServiceValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self._service_ids: set[int] = set()

    def visit_lrpc_def(self, _: LrpcDef) -> None:
        self.reset()
        self._service_ids.clear()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        service_id = service.id()

        if service_id in self._service_ids:
            self.add_error(f"Duplicate service id: {service_id}")

        self._service_ids.add(service_id)
