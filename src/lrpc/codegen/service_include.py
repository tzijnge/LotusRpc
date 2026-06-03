from pathlib import Path

from lrpc.codegen.common import lrpc_var_includes, write_file_banner
from lrpc.codegen.cppfile import CppFile
from lrpc.core import LrpcFun, LrpcService, LrpcVar
from lrpc.visitors import LrpcVisitor


class ServiceIncludeVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._output = output
        self._file: CppFile
        self._includes: set[tuple[str, bool]] = set()

    def _create_service_include(self, output: Path, service_name: str) -> None:
        self._includes = set()

        self._file = CppFile(f"{output}/{service_name}_includes.hpp")
        write_file_banner(self._file)
        self._file.pragma_once()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self._create_service_include(self._output, service.name())

    def visit_lrpc_service_end(self) -> None:
        for path, iwyu_export in sorted(self._includes):
            self._file.include(path, iwyu_export=iwyu_export)

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        if function.number_returns() > 1:
            self._includes.add(("<tuple>", True))

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self._includes.update(lrpc_var_includes(ret))

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self._includes.update(lrpc_var_includes(param))

    def visit_lrpc_stream_return(self, ret: LrpcVar) -> None:
        self._includes.update(lrpc_var_includes(ret))

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self._includes.update(lrpc_var_includes(param))
