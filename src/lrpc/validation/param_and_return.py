from lrpc.core import LrpcDef, LrpcFun, LrpcService, LrpcStream, LrpcVar

from .validator import LrpcValidator


class ParamAndReturnValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self._current_service: str = ""
        self._current_function: str = ""
        self._current_stream: str = ""
        self._param_return_names: set[str] = set()

    def visit_lrpc_def(self, _: LrpcDef) -> None:
        self.reset()
        self._current_service = ""
        self._current_function = ""
        self._current_stream = ""
        self._param_return_names.clear()

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self._current_function = function.name()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self._current_service = service.name()

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        name = param.name()
        if name in self._param_return_names:
            self.add_error(f"Duplicate name in {self._current_service}.{self._current_function}: {name}")

        self._param_return_names.add(name)

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        name = ret.name()
        if name in self._param_return_names:
            self.add_error(f"Duplicate name in {self._current_service}.{self._current_function}: {name}")

        self._param_return_names.add(name)

    def visit_lrpc_function_end(self) -> None:
        self._param_return_names.clear()

    def visit_lrpc_stream(self, stream: LrpcStream) -> None:
        self._current_stream = stream.name()

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        name = param.name()
        if name in self._param_return_names:
            self.add_error(f"Duplicate name in {self._current_service}.{self._current_stream}: {name}")

        self._param_return_names.add(name)

    def visit_lrpc_stream_param_end(self) -> None:
        self._param_return_names.clear()

    def visit_lrpc_stream_return(self, ret: LrpcVar) -> None:
        name = ret.name()
        if name in self._param_return_names:
            self.add_error(f"Duplicate name in {self._current_service}.{self._current_stream}: {name}")

        self._param_return_names.add(name)

    def visit_lrpc_stream_return_end(self) -> None:
        self._param_return_names.clear()
