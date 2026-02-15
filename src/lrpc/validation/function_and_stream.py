from lrpc.core import LrpcDef, LrpcFun, LrpcService, LrpcStream

from .validator import LrpcValidator


class FunctionAndStreamIdValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self._ids: set[int] = set()
        self._current_service: str = ""

    def visit_lrpc_def(self, _lrpc_def: LrpcDef) -> None:
        self.reset()
        self._ids.clear()
        self._current_service = ""

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        function_id = function.id()

        if function_id in self._ids:
            self.add_error(f"Duplicate function id in service {self._current_service}: {function_id}")

        self._ids.add(function_id)

    def visit_lrpc_stream(self, stream: LrpcStream) -> None:
        stream_id = stream.id()

        if stream_id in self._ids:
            self.add_error(f"Duplicate stream id in service {self._current_service}: {stream_id}")

        self._ids.add(stream_id)

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self._current_service = service.name()
        self._ids.clear()


class FunctionAndStreamNameValidator(LrpcValidator):
    def __init__(self) -> None:
        super().__init__()
        self._function_names: set[str] = set()
        self._current_service: str = ""
        self._param_names: set[str] = set()
        self._return_names: set[str] = set()

    def visit_lrpc_def(self, _lrpc_def: LrpcDef) -> None:
        self.reset()
        self._function_names.clear()
        self._current_service = ""
        self._param_names.clear()
        self._return_names.clear()

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        name = function.name()

        if name in self._function_names:
            self.add_error(f"Duplicate function name in service {self._current_service}: {name}")

        if name == (self._current_service + "_shim"):
            self.add_error(
                f"Invalid function name: {name}. This name is incompatible with the generated code "
                "for the containing service",
            )

        self._function_names.add(name)

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self._current_service = service.name()
        self._function_names.clear()
