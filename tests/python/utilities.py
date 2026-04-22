import json
import re
from pathlib import Path

from lrpc.core import LrpcFun, LrpcService, LrpcStream, LrpcVar
from lrpc.core.definition import LrpcDef, LrpcUserSettings
from lrpc.utils import load_lrpc_def
from lrpc.visitors import LrpcVisitor


def number_out_of_range_pattern(low: int, high: int) -> str:
    variants = [
        "argument out of range",
        f"{low} <= number <= {high}",
    ]
    if low == 0 and high == 65535:
        variants += [
            re.escape("0 <= number <= (32767 *2 +1)"),
            "0 <= number <= 0xffff",
            re.escape("0 <= number <= (0x7fff * 2 + 1)"),
        ]
    elif low == -32768 and high == 32767:
        variants += [
            re.escape("(-32767 -1) <= number <= 32767"),
            re.escape("(-32768) <= number <= 32767"),
            re.escape("(-0x7fff - 1) <= number <= 0x7fff"),
        ]
    return "|".join(variants)


def load_test_definition(definition_file_name: str) -> LrpcDef:
    def_url = Path(__file__).parent.parent.joinpath("testdata").joinpath(definition_file_name)
    return load_lrpc_def(def_url)


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

    def visit_lrpc_user_settings(self, user_settings: LrpcUserSettings) -> None:
        if user_settings is None:
            return

        self._insert_separator()
        self.result += f"user_settings: {json.dumps(user_settings)}"

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
