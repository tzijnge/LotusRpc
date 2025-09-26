from lrpc.visitors import LrpcVisitor
from lrpc.core import LrpcService, LrpcVar, LrpcFun, LrpcStream


class StringifyVisitor(LrpcVisitor):
    def __init__(self) -> None:
        self.result: str = ""

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self._insert_separator()
        self.result += f"service[{service.name()}]"

    def visit_lrpc_service_end(self) -> None:
        self._insert_separator()
        self.result += "service_end"

    def visit_lrpc_stream(self, stream: LrpcStream) -> None:
        self._insert_separator()
        self.result += f"stream[{stream.name()}+{stream.id()}+{stream.origin().value}]"

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self._add_param(param)

    def visit_lrpc_stream_param_end(self) -> None:
        self._add_param_end()

    def visit_lrpc_stream_return(self, ret: "LrpcVar") -> None:
        self._add_return(ret)

    def visit_lrpc_stream_return_end(self) -> None:
        self._add_return_end()

    def visit_lrpc_stream_end(self) -> None:
        self._insert_separator()
        self.result += "stream_end"

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self._insert_separator()
        self.result += f"function[{function.name()}+{function.id()}]"

    def visit_lrpc_function_end(self) -> None:
        self._insert_separator()
        self.result += "function_end"

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self._add_return(ret)

    def visit_lrpc_function_return_end(self) -> None:
        self._add_return_end()

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self._add_param(param)

    def visit_lrpc_function_param_end(self) -> None:
        self._add_param_end()

    def _insert_separator(self) -> None:
        if len(self.result) != 0:
            self.result += "-"

    def _add_return(self, ret: LrpcVar) -> None:
        self._insert_separator()
        self.result += f"return[{ret.name()}]"

    def _add_return_end(self) -> None:
        self._insert_separator()
        self.result += "return_end"

    def _add_param(self, param: LrpcVar) -> None:
        self._insert_separator()
        self.result += f"param[{param.name()}]"

    def _add_param_end(self) -> None:
        self._insert_separator()
        self.result += "param_end"
