from typing import Optional
from code_generation.code_generator import CppFile
from lrpc import LrpcVisitor
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcConstant, LrpcDef


class ConstantsFileVisitor(LrpcVisitor):
    def __init__(self, output: str):
        self.output = output
        self.namespace: Optional[str] = None
        self.file: CppFile
        self.includes: set[str] = set()
        self.constant_definitions: list[str] = []

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.file = CppFile(f"{self.output}/{lrpc_def.name()}_Constants.hpp")
        self.namespace = lrpc_def.namespace()
        self.constant_definitions = []
        self.includes = set()

    def visit_lrpc_constant(self, constant: LrpcConstant) -> None:
        if "int" in constant.cpp_type():
            self.includes.add("stdint.h")
        if constant.cpp_type() == "string":
            self.includes.add("etl/string_view.h")

        self.constant_definitions.append(self.__constant_definition(constant))

    def visit_lrpc_constants_end(self) -> None:
        self.__write_include_guard()
        self.__write_includes()
        self.file.newline()
        self.__write_constant_definitions(self.namespace)

    def __write_include_guard(self) -> None:
        self.file("#pragma once")

    def __write_includes(self) -> None:
        for i in self.includes:
            self.file.write(f"#include <{i}>")

    @optionally_in_namespace
    def __write_constant_definitions(self) -> None:
        for cd in self.constant_definitions:
            self.file.write(cd)

    def __constant_definition(self, constant: LrpcConstant) -> str:
        n = constant.name()

        if constant.cpp_type() == "string":
            t = "etl::string_view"
            v = f'"{constant.value()}"'
        else:
            t = constant.cpp_type()
            v = str(constant.value()).lower()

        return f"constexpr {t} {n} {{{v}}};"
