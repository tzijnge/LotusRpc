import os
from typing import Optional
from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..visitors import LrpcVisitor
from ..codegen.common import write_file_banner
from ..codegen.utils import optionally_in_namespace
from ..core import LrpcConstant, LrpcDef


class ConstantsFileVisitor(LrpcVisitor):

    def __init__(self, output: os.PathLike[str]) -> None:
        self.__output = output
        self.__namespace: Optional[str] = None
        self.__file: CppFile
        self.__includes: set[str] = set()
        self.__constant_definitions: list[str] = []
        self.__def_name: str

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__namespace = lrpc_def.namespace()
        self.__def_name = lrpc_def.name()

    def visit_lrpc_constant(self, constant: LrpcConstant) -> None:
        if "int" in constant.cpp_type():
            self.__includes.add("stdint.h")
        if constant.cpp_type() == "string":
            self.__includes.add("etl/string_view.h")

        self.__constant_definitions.append(self.__constant_definition(constant))

    def visit_lrpc_constants_end(self) -> None:
        self.__file = CppFile(f"{self.__output}/{self.__def_name}_Constants.hpp")
        write_file_banner(self.__file)
        self.__write_include_guard()
        self.__write_includes()
        self.__file.newline()
        optionally_in_namespace(self.__file, self.__write_constant_definitions, self.__namespace)

    def __write_include_guard(self) -> None:
        self.__file("#pragma once")

    def __write_includes(self) -> None:
        for i in self.__includes:
            self.__file.write(f"#include <{i}>")

    def __write_constant_definitions(self) -> None:
        for cd in self.__constant_definitions:
            self.__file.write(cd)

    def __constant_definition(self, constant: LrpcConstant) -> str:
        n = constant.name()
        literal = "f" if constant.cpp_type() == "float" else ""

        if constant.cpp_type() == "string":
            t = "etl::string_view"
            v = f'"{constant.value()}"'
        else:
            t = constant.cpp_type()
            v = str(constant.value()).lower()

        return f"constexpr {t} {n} {{{v}{literal}}};"
