from ..core import LrpcDef, LrpcService, LrpcFun, LrpcStream
from .validator import LrpcValidator


class FunctionAndStreamIdValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.__ids: set[int] = set()
        self.__current_service: str = ""

    def errors(self) -> list[str]:
        return self.__errors

    def warnings(self) -> list[str]:
        return self.__warnings

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__ids.clear()
        self.__current_service = ""

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        function_id = function.id()

        if function_id in self.__ids:
            self.__errors.append(f"Duplicate function id in service {self.__current_service}: {function_id}")

        self.__ids.add(function_id)

    def visit_lrpc_stream(self, stream: LrpcStream) -> None:
        stream_id = stream.id()

        if stream_id in self.__ids:
            self.__errors.append(f"Duplicate stream id in service {self.__current_service}: {stream_id}")

        self.__ids.add(stream_id)

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__current_service = service.name()
        self.__ids.clear()


class FunctionAndStreamNameValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.__function_names: set[str] = set()
        self.__current_service: str = ""
        self.__param_names: set[str] = set()
        self.__return_names: set[str] = set()

    def errors(self) -> list[str]:
        return self.__errors

    def warnings(self) -> list[str]:
        return self.__warnings

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__function_names.clear()
        self.__current_service = ""
        self.__param_names.clear()
        self.__return_names.clear()

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        name = function.name()

        if name in self.__function_names:
            self.__errors.append(f"Duplicate function name in service {self.__current_service}: {name}")

        if name == (self.__current_service + "ServiceShim"):
            self.__errors.append(
                f"Invalid function name: {name}. This name is incompatible with the generated code for the containing service"
            )

        self.__function_names.add(name)

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__current_service = service.name()
        self.__function_names.clear()
