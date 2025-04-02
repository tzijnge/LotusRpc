import os
from typing import Optional
from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..visitors import LrpcVisitor
from ..core import LrpcDef
from ..core import LrpcEnum
from ..codegen.utils import optionally_in_namespace
from ..codegen.common import write_file_banner


class EnumFileVisitor(LrpcVisitor):

    def __init__(self, output: os.PathLike[str]) -> None:
        self.__descriptor: LrpcEnum
        self.__file: CppFile
        self.__namespace: Optional[str]
        self.__output = output

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__namespace = lrpc_def.namespace()

    def visit_lrpc_enum(self, enum: LrpcEnum) -> None:
        self.__descriptor = enum
        self.__file = CppFile(f"{self.__output}/{self.__descriptor.name()}.hpp")

        write_file_banner(self.__file)
        self.__write_include_guard()

        if self.__descriptor.is_external():
            self.__write_external_enum_include()
            self.__file.newline()
            self.__write_external_alias_if_needed()
            self.__write_external_enum_checks()
        else:
            self.__file.newline()
            optionally_in_namespace(self.__file, self.__write_enum, self.__namespace)

    def __write_external_alias_if_needed(self) -> None:
        if self.__namespace or self.__descriptor.external_namespace():
            optionally_in_namespace(self.__file, self.__write_external_alias, self.__namespace)
            self.__file.newline()

    def __write_external_alias(self) -> None:
        name = self.__qualified_name()
        ext_ns = self.__descriptor.external_namespace()
        ext_full_name = f"{ext_ns}::{name}" if ext_ns else f"::{name}"
        self.__file.write(f"using {name} = {ext_full_name};")

    def __write_include_guard(self) -> None:
        self.__file.write("#pragma once")

    def __write_external_enum_include(self) -> None:
        self.__file.write(f'#include "{self.__descriptor.external_file()}"')

    def __write_external_enum_checks(self) -> None:
        with self.__file.block("namespace lrpc_private"):
            for f in self.__descriptor.fields():
                ns = self.__namespace
                enum_name = self.__descriptor.name()
                field_name = f.name()
                field_id = f.id()
                if ns:
                    self.__file.write(
                        f'static_assert(static_cast<uint8_t>({ns}::{enum_name}::{field_name}) == {field_id}, "External enum value {field_name} is not as specified in LRPC");'
                    )
                else:
                    self.__file.write(
                        f'static_assert(static_cast<uint8_t>({enum_name}::{field_name}) == {field_id}, "External enum value {field_name} is not as specified in LRPC");'
                    )

            self.__file.newline()

            self.__file.write("// With the right compiler settings this function generates a compiler warning")
            self.__file.write("// if the external enum declaration has fields that are not known to LRPC")
            self.__file.write(
                "// This function does not serve any purpose and is optimized out with the right compiler/linker settings"
            )

            with self.__file.block(f"constexpr void CheckEnum(const {self.__name()} v)"):
                with self.__file.block("switch (v)"):
                    for f in self.__descriptor.fields():
                        self.__file.write(f"case {self.__name()}::{f.name()}: break;")

    def __write_enum(self) -> None:
        n = self.__descriptor.name()
        with self.__file.block(f"enum class {n}", ";"):
            for f in self.__descriptor.fields():
                self.__file.write(f"{f.name()} = {f.id()},")

    def __name(self) -> str:
        ns = self.__namespace
        qn = self.__qualified_name()
        return f"{ns}::{qn}" if ns else qn

    def __qualified_name(self) -> str:
        return self.__descriptor.name()
