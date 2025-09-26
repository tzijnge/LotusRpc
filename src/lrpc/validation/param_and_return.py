from ..core import LrpcDef, LrpcService, LrpcFun, LrpcVar, LrpcStream
from .validator import LrpcValidator


class ParamAndReturnValidator(LrpcValidator):
    def __init__(self) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.__current_service: str = ""
        self.__current_function: str = ""
        self.__current_stream: str = ""
        self.__param_names: set[str] = set()
        self.__return_names: set[str] = set()

    def errors(self) -> list[str]:
        return self.__errors

    def warnings(self) -> list[str]:
        return self.__warnings

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__errors.clear()
        self.__warnings.clear()
        self.__current_service = ""
        self.__current_function = ""
        self.__current_stream = ""
        self.__param_names.clear()
        self.__return_names.clear()

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self.__current_function = function.name()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__current_service = service.name()

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        name = param.name()
        if name in self.__param_names:
            self.__errors.append(f"Duplicate name in {self.__current_service}.{self.__current_function}: {name}")

        self.__param_names.add(name)

    def visit_lrpc_function_param_end(self) -> None:
        self.__param_names.clear()

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        name = ret.name()
        if name in self.__param_names:
            self.__errors.append(f"Duplicate name in {self.__current_service}.{self.__current_function}: {name}")

        self.__param_names.add(name)

    def visit_lrpc_function_return_end(self) -> None:
        self.__return_names.clear()

    def visit_lrpc_stream(self, stream: LrpcStream) -> None:
        self.__current_stream = stream.name()

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        name = param.name()
        if name in self.__param_names:
            self.__errors.append(f"Duplicate name in {self.__current_service}.{self.__current_stream}: {name}")

        self.__param_names.add(name)

    def visit_lrpc_stream_param_end(self) -> None:
        self.__param_names.clear()

    def visit_lrpc_stream_return(self, ret: LrpcVar) -> None:
        name = ret.name()
        if name in self.__return_names:
            self.__errors.append(f"Duplicate name in {self.__current_service}.{self.__current_stream}: {name}")

        self.__return_names.add(name)

    def visit_lrpc_stream_return_end(self) -> None:
        self.__return_names.clear()
