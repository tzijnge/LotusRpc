from pathlib import Path

from lrpc.codegen.common import lrpc_var_includes, write_file_banner
from lrpc.codegen.cppfile import CppFile
from lrpc.codegen.struct_codec_writer import StructCodecWriter
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcStruct, LrpcVar, RpcSettings
from lrpc.visitors import LrpcVisitor


class StructFileVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._output = output
        self._namespace: str | None
        self._file: CppFile
        self._descriptor: LrpcStruct
        self._alias: str = ""
        self._includes: set[tuple[str, bool]] = set()

    def visit_rpc_settings(self, settings: RpcSettings) -> None:
        self._namespace = settings.namespace()

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self._descriptor = struct
        self._file = CppFile(f"{self._output}/{self._qualified_name()}.hpp")
        self._init_alias()

    def visit_lrpc_struct_end(self) -> None:
        write_file_banner(self._file)
        self._file.pragma_once()
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
            with self._file.block(f"struct {self._qualified_name()}", ";", trailing_newline=True):
                for f in self._descriptor.fields():
                    self._write_struct_field(f)
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
        self._includes.add(("<etl/byte_stream.h>", False))
        self._includes.add(('"lrpccore/EtlRwExtensions.hpp"', False))
        if self._descriptor.is_external():
            self._includes.add((f'"{self._descriptor.external_file()}"', False))
        for path, _ in sorted(self._includes):
            self._file.include(path)

    def _write_struct(self) -> None:
        with self._file.block(f"struct {self._qualified_name()}", ";", trailing_newline=True):
            for f in self._descriptor.fields():
                self._write_struct_field(f)

        with self._file.block(
            f"inline bool operator==(const {self._qualified_name()}& first, const {self._qualified_name()}& second)",
        ):
            field_names = [f.name() for f in self._descriptor.fields()]
            fields_equal = [f"(first.{n} == second.{n})" for n in field_names]
            all_fields_equal = " && ".join(fields_equal)
            self._file(f"return {all_fields_equal};")

        with self._file.block(
            f"inline bool operator!=(const {self._qualified_name()}& first, const {self._qualified_name()}& second)",
        ):
            self._file("return !(first == second);")

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
