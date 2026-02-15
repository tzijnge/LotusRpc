from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcEnum
from lrpc.visitors import LrpcVisitor


class EnumFileVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._descriptor: LrpcEnum
        self._file: CppFile
        self._namespace: str | None
        self._output = output

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self._descriptor = enum
        self._file = CppFile(f"{self._output}/{self._descriptor.name()}.hpp")

        write_file_banner(self._file)
        self._write_include_guard()

        if self._descriptor.is_external():
            self._write_external_enum_include()
            self._file.newline()
            self._write_external_alias_if_needed()
            self._write_external_enum_checks()
        else:
            self._file.newline()
            optionally_in_namespace(self._file, self._write_enum, self._namespace)

    def _write_external_alias_if_needed(self) -> None:
        if self._namespace or self._descriptor.external_namespace():
            optionally_in_namespace(self._file, self._write_external_alias, self._namespace)
            self._file.newline()

    def _write_external_alias(self) -> None:
        name = self._qualified_name()
        ext_ns = self._descriptor.external_namespace()
        ext_full_name = f"{ext_ns}::{name}" if ext_ns else f"::{name}"
        self._file.write(f"using {name} = {ext_full_name};")

    def _write_include_guard(self) -> None:
        self._file.write("#pragma once")

    def _write_external_enum_include(self) -> None:
        self._file.write(f'#include "{self._descriptor.external_file()}"')

    def _write_external_enum_checks(self) -> None:
        with self._file.block("namespace lrpc_private"):
            for f in self._descriptor.fields():
                ns = self._namespace
                enum_name = self._descriptor.name()
                field_name = f.name()
                field_id = f.id()
                if ns:
                    self._file.write(
                        f"static_assert(static_cast<uint8_t>({ns}::{enum_name}::{field_name}) == {field_id}, "
                        f'"External enum value {field_name} is not as specified in LRPC");',
                    )
                else:
                    self._file.write(
                        f"static_assert(static_cast<uint8_t>({enum_name}::{field_name}) == {field_id}, "
                        f'"External enum value {field_name} is not as specified in LRPC");',
                    )

            self._file.newline()

            self._file.write("// With the right compiler settings this function generates a compiler warning")
            self._file.write("// if the external enum declaration has fields that are not known to LRPC")
            self._file.write(
                "// This function does not serve any purpose and is optimized out "
                "with the right compiler/linker settings",
            )

            with (
                self._file.block(f"constexpr void CheckEnum(const {self._name()} v)"),
                self._file.block("switch (v)"),
            ):
                for f in self._descriptor.fields():
                    self._file.write(f"case {self._name()}::{f.name()}: break;")

    def _write_enum(self) -> None:
        n = self._descriptor.name()
        with self._file.block(f"enum class {n}", ";"):
            for f in self._descriptor.fields():
                self._file.write(f"{f.name()} = {f.id()},")

    def _name(self) -> str:
        ns = self._namespace
        qn = self._qualified_name()
        return f"{ns}::{qn}" if ns else qn

    def _qualified_name(self) -> str:
        return self._descriptor.name()
