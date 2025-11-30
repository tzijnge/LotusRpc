import os

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]
from ..visitors import LrpcVisitor
from ..codegen.common import lrpc_var_includes, write_file_banner
from ..core import LrpcFun, LrpcService, LrpcVar


class ServiceIncludeVisitor(LrpcVisitor):
    def __init__(self, output: os.PathLike[str]) -> None:
        self.__output = output
        self.__file: CppFile
        self.__includes: set[str] = set()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__includes = set()

        # TODO: file name should be service_includes.hpp
        self.__file = CppFile(f"{self.__output}/{service.name()}.hpp")
        write_file_banner(self.__file)
        self.__file.write("#pragma once")

    def visit_lrpc_service_end(self) -> None:
        for i in sorted(self.__includes):
            self.__file.write(f"#include {i}")

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        if function.number_returns() > 1:
            self.__includes.add("<tuple>")

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.__includes.update(lrpc_var_includes(ret))

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.__includes.update(lrpc_var_includes(param))

    def visit_lrpc_stream_return(self, ret: LrpcVar) -> None:
        self.__includes.update(lrpc_var_includes(ret))

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self.__includes.update(lrpc_var_includes(param))


class MetaServiceIncludeVisitor(ServiceIncludeVisitor):
    def __init__(self, output: os.PathLike[str]) -> None:
        super().__init__(os.path.join(output, "lrpccore", "meta"))
        self._active = False

    def visit_lrpc_service(self, service: LrpcService) -> None:
        if service.id() == 255:
            super().visit_lrpc_service(service)
            self._active = True

    def visit_lrpc_service_end(self) -> None:
        if self._active:
            super().visit_lrpc_service_end()
            self._active = False
