import typing
from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcConstant, LrpcDef
from lrpc.visitors import LrpcVisitor


class ConstantsFileVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._output = output
        self._namespace: str | None = None
        self._file: CppFile
        self._includes: set[str] = set()
        self._constant_definitions: list[str] = []
        self._def_name: str

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()
        self._def_name = lrpc_def.name()

    def visit_lrpc_constant(self, constant: LrpcConstant) -> None:
        if "int" in constant.cpp_type():
            self._includes.add("stdint.h")
        if constant.cpp_type() == "string":
            self._includes.add("etl/string_view.h")
        if constant.cpp_type() == "bytearray":
            self._includes.update({"etl/array.h", "stdint.h"})

        self._constant_definitions.append(self._constant_definition(constant))

    def visit_lrpc_constants_end(self) -> None:
        self._file = CppFile(f"{self._output}/{self._def_name}_Constants.hpp")
        write_file_banner(self._file)
        self._write_include_guard()
        self._write_includes()
        self._file.newline()
        optionally_in_namespace(self._file, self._write_constant_definitions, self._namespace)

    def _write_include_guard(self) -> None:
        self._file("#pragma once")

    def _write_includes(self) -> None:
        for i in self._includes:
            self._file.write(f"#include <{i}>")

    def _write_constant_definitions(self) -> None:
        for cd in self._constant_definitions:
            self._file.write(cd)

    def _constant_definition(self, constant: LrpcConstant) -> str:
        n = constant.name()
        literal = "f" if constant.cpp_type() == "float" else ""

        if constant.cpp_type() == "string":
            str_value = typing.cast(str, constant.value())
            t = "etl::string_view"
            v = f'"{str_value}"'
        elif constant.cpp_type() == "bytearray":
            ba_value = typing.cast(bytes, constant.value())
            t = f"etl::array<uint8_t, {len(ba_value)}>"
            v = ", ".join(hex(b) for b in ba_value)
        else:
            t = constant.cpp_type()
            v = str(constant.value()).lower()

        return f"constexpr {t} {n} {{{v}{literal}}};"
