from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import lrpc_var_includes, write_file_banner
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef, LrpcStruct, LrpcVar
from lrpc.visitors import LrpcVisitor


class StructCodecWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_encoder_body(self, descriptor: LrpcStruct, namespace: str | None) -> None:
        for f in descriptor.fields():
            t = f.rw_type(namespace)
            p = StructCodecWriter._write_params(f)
            self._file.write(f"lrpc::write_unchecked<{t}>({p});")

    def write_decoder_body(self, descriptor: LrpcStruct, name: str, namespace: str | None) -> None:
        self._file(f"{name} obj;")

        for f in descriptor.fields():
            assignment = StructCodecWriter._read_assignment(f)
            t = f.rw_type(namespace)
            p = StructCodecWriter._read_params(f)
            self._file.write(f"{assignment}lrpc::read_unchecked<{t}>({p});")

        self._file("return obj;")

    @staticmethod
    def _write_params(var: LrpcVar) -> str:
        params = ["writer", f"obj.{var.name()}"]
        if var.is_array():
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)

    @staticmethod
    def _read_params(var: LrpcVar) -> str:
        params = ["reader"]
        if var.is_array():
            params.append(f"obj.{var.name()}")
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)

    @staticmethod
    def _read_assignment(var: LrpcVar) -> str:
        return "" if var.is_array() else f"obj.{var.name()} = "


class StructFileVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self.__output = output
        self.__namespace: str | None
        self.__file: CppFile
        self.__descriptor: LrpcStruct
        self.__alias: str = ""
        self.__includes: set[str] = set()

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__namespace = lrpc_def.namespace()

    def visit_lrpc_struct(self, struct: LrpcStruct) -> None:
        self.__descriptor = struct
        self.__file = CppFile(f"{self.__output}/{self.__qualified_name()}.hpp")
        self.__init_alias()

    def visit_lrpc_struct_end(self) -> None:
        write_file_banner(self.__file)
        self.__file.write("#pragma once")
        self.__write_includes()
        self.__file.newline()

        if self.__descriptor.is_external():
            self.__write_external_alias_if_needed()
        else:
            optionally_in_namespace(self.__file, self.__write_struct, self.__namespace)

        self.__file.newline()
        self.__write_codec()
        self.__file.newline()

        if self.__descriptor.is_external():
            self.__write_external_struct_checks()

    def visit_lrpc_struct_field(self, _struct: LrpcStruct, field: LrpcVar) -> None:
        if self.__descriptor.is_external():
            return

        self.__includes.update(lrpc_var_includes(field))

    def __init_alias(self) -> None:
        ns = self.__namespace
        ext_ns = self.__descriptor.external_namespace()
        name = self.__descriptor.name()

        if (not ns) and (not ext_ns):
            self.__alias = ""
        elif (not ns) and ext_ns:
            self.__alias = name
        elif ns and (not ext_ns):
            self.__alias = f"{ns}::{name}"
        else:
            self.__alias = f"{ns}::{name}"

    def __write_external_alias_if_needed(self) -> None:
        if len(self.__alias) > 0:
            optionally_in_namespace(self.__file, self.__write_external_alias, self.__namespace)
            self.__file.newline()

    def __write_external_struct_checks(self) -> None:
        with (
            self.__file.block("namespace lrpc_private"),
            self.__file.block("namespace dummy"),
        ):
            with self.__file.block(f"struct {self.__qualified_name()}", ";"):
                for f in self.__descriptor.fields():
                    self.__write_struct_field(f)

            self.__file.newline()
            self.__file.write(
                f"static_assert(sizeof(dummy::{self.__qualified_name()}) == sizeof({self.__name()}), "
                '"External struct size not as expected. It may have missing or additional fields '
                'or different packing.");',
            )
            self.__file.newline()
            for f in self.__descriptor.fields():
                self.__file.write(
                    f"static_assert(std::is_same<decltype(dummy::{self.__qualified_name()}::{f.name()}), "
                    f'decltype({self.__name()}::{f.name()})>::value, "Type of field {f.name()} '
                    'is not as specified in LRPC");',
                )

    def __write_external_alias(self) -> None:
        ext_ns = self.__descriptor.external_namespace()
        name = self.__descriptor.name()
        ext_full_name = f"{ext_ns}::{name}" if ext_ns else f"::{name}"
        self.__file.write(f"using {name} = {ext_full_name};")

    def __write_includes(self) -> None:
        self.__includes.add("<etl/byte_stream.h>")
        self.__includes.add('"lrpccore/EtlRwExtensions.hpp"')
        if self.__descriptor.is_external():
            self.__includes.add(f'"{self.__descriptor.external_file()}"')
        for i in sorted(self.__includes):
            self.__file(f"#include {i}")

    def __write_struct(self) -> None:
        with self.__file.block(f"struct {self.__qualified_name()}", ";"):
            for f in self.__descriptor.fields():
                self.__write_struct_field(f)

            self.__file.newline()

            with self.__file.block(f"bool operator==(const {self.__qualified_name()}& other) const"):
                field_names = [f.name() for f in self.__descriptor.fields()]
                fields_equal = [f"(this->{n} == other.{n})" for n in field_names]
                all_fields_equal = " && ".join(fields_equal)
                self.__file(f"return {all_fields_equal};")

            with self.__file.block(f"bool operator!=(const {self.__qualified_name()}& other) const"):
                self.__file("return !(*this == other);")

    def __write_codec(self) -> None:
        codec_writer = StructCodecWriter(self.__file)
        with self.__file.block("namespace lrpc"):
            name = self.__name()
            self.__file("template<>")
            with self.__file.block(f"inline {name} read_unchecked<{name}>(etl::byte_stream_reader& reader)"):
                codec_writer.write_decoder_body(self.__descriptor, name, self.__namespace)

            self.__file.newline()

            self.__file("template<>")
            with self.__file.block(
                f"inline void write_unchecked<{name}>(etl::byte_stream_writer& writer, const {name}& obj)",
            ):
                codec_writer.write_encoder_body(self.__descriptor, self.__namespace)

    def __write_struct_field(self, f: LrpcVar) -> None:
        self.__file(f"{f.field_type()} {f.name()};")

    def __name(self) -> str:
        ns = self.__namespace
        qn = self.__qualified_name()
        return f"{ns}::{qn}" if ns else qn

    def __qualified_name(self) -> str:
        return self.__descriptor.name()
