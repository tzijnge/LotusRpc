from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import lrpc_var_includes, write_file_banner
from lrpc.codegen.struct_codec_writer import StructCodecWriter
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcStruct, LrpcVar
from lrpc.visitors import LrpcVisitor


class StructFileVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._output = output
        self._namespace: str | None
        self._file: CppFile
        self._descriptor: LrpcStruct
        self._alias: str = ""
        self._includes: set[str] = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self._descriptor = struct
        self._file = CppFile(f"{self._output}/{self._qualified_name()}.hpp")
        self._init_alias()

    def visit_lrpc_struct_end(self) -> None:
        write_file_banner(self._file)
        self._file.write("#pragma once")
        self._write_includes()
        self._file.newline()

        if self._descriptor.is_external():
            self._write_external_alias_if_needed()
        else:
            optionally_in_namespace(self._file, self._write_struct, self._namespace)

        self._file.newline()
        self._write_codec()
        self._file.newline()

        if self._descriptor.is_external():
            self._write_external_struct_checks()

    def visit_lrpc_struct_field(self, _struct: LrpcStruct, field: LrpcVar) -> None:
        if self._descriptor.is_external():
            return

        self._includes.update(lrpc_var_includes(field))

    def _init_alias(self) -> None:
        ns = self._namespace
        ext_ns = self._descriptor.external_namespace()
        name = self._descriptor.name()

        if (not ns) and (not ext_ns):
            self._alias = ""
        elif (not ns) and ext_ns:
            self._alias = name
        elif ns and (not ext_ns):
            self._alias = f"{ns}::{name}"
        else:
            self._alias = f"{ns}::{name}"

    def _write_external_alias_if_needed(self) -> None:
        if len(self._alias) > 0:
            optionally_in_namespace(self._file, self._write_external_alias, self._namespace)
            self._file.newline()

    def _write_external_struct_checks(self) -> None:
        with (
            self._file.block("namespace lrpc_private"),
            self._file.block("namespace dummy"),
        ):
            with self._file.block(f"struct {self._qualified_name()}", ";"):
                for f in self._descriptor.fields():
                    self._write_struct_field(f)

            self._file.newline()
            self._file.write(
                f"static_assert(sizeof(dummy::{self._qualified_name()}) == sizeof({self._name()}), "
                '"External struct size not as expected. It may have missing or additional fields '
                'or different packing.");',
            )
            self._file.newline()
            for f in self._descriptor.fields():
                self._file.write(
                    f"static_assert(std::is_same<decltype(dummy::{self._qualified_name()}::{f.name()}), "
                    f'decltype({self._name()}::{f.name()})>::value, "Type of field {f.name()} '
                    'is not as specified in LRPC");',
                )

    def _write_external_alias(self) -> None:
        ext_ns = self._descriptor.external_namespace()
        name = self._descriptor.name()
        ext_full_name = f"{ext_ns}::{name}" if ext_ns else f"::{name}"
        self._file.write(f"using {name} = {ext_full_name};")

    def _write_includes(self) -> None:
        self._includes.add("<etl/byte_stream.h>")
        self._includes.add('"lrpccore/EtlRwExtensions.hpp"')
        if self._descriptor.is_external():
            self._includes.add(f'"{self._descriptor.external_file()}"')
        for i in sorted(self._includes):
            self._file(f"#include {i}")

    def _write_struct(self) -> None:
        with self._file.block(f"struct {self._qualified_name()}", ";"):
            for f in self._descriptor.fields():
                self._write_struct_field(f)

            self._file.newline()

            with self._file.block(f"bool operator==(const {self._qualified_name()}& other) const"):
                field_names = [f.name() for f in self._descriptor.fields()]
                fields_equal = [f"(this->{n} == other.{n})" for n in field_names]
                all_fields_equal = " && ".join(fields_equal)
                self._file(f"return {all_fields_equal};")

            with self._file.block(f"bool operator!=(const {self._qualified_name()}& other) const"):
                self._file("return !(*this == other);")

    def _write_codec(self) -> None:
        codec_writer = StructCodecWriter(self._file, self._descriptor, self._namespace)
        with self._file.block("namespace lrpc"):
            codec_writer.write_decoder()
            self._file.newline()
            codec_writer.write_encoder()

    def _write_struct_field(self, f: LrpcVar) -> None:
        self._file(f"{f.field_type()} {f.name()};")

    def _name(self) -> str:
        ns = self._namespace
        qn = self._qualified_name()
        return f"{ns}::{qn}" if ns else qn

    def _qualified_name(self) -> str:
        return self._descriptor.name()
