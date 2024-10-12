from ..core import LrpcDef, LrpcService
from .validator import LrpcValidator


class ServiceValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.__service_ids: set[int] = set()

    def errors(self) -> list[str]:
        return self.__errors

    def warnings(self) -> list[str]:
        return self.__warnings

    def visit_lrpc_def(self, _: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__service_ids.clear()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        service_id = service.id()

        if service_id in self.__service_ids:
            self.__errors.append(f"Duplicate service id: {service_id}")

        self.__service_ids.add(service_id)
