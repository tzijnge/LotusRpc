from importlib.metadata import version
from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.utils import optionally_in_namespace
from lrpc.core import LrpcDef
from lrpc.visitors import LrpcVisitor


class MetaServiceVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._namespace: str | None
        self._output = output
        self._file: CppFile
        self._file2: CppFile
        self._processing_meta_service = False
        self._lines: list[str] = []
        self._definition_version: str | None = None
        self._definition_hash: str | None
        self._embed_definition: bool = False

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()
        self._file = CppFile(f"{self._output}/LrpcMeta_service.hpp")
        self._definition_version = lrpc_def.version()
        self._definition_hash = lrpc_def.definition_hash()
        self._embed_definition = lrpc_def.embed_definition()

        write_file_banner(self._file)
        self._file.write("#pragma once")
        self._file.write('#include "LrpcMeta_shim.hpp"')
        if lrpc_def.embed_definition():
            self._file.write('#include "LrpcMeta_definition.hpp"')

        self._file.newline()
        optionally_in_namespace(self._file, self._write_service_class, self._namespace)

        if lrpc_def.embed_definition():
            self._write_definition(lrpc_def.compressed_definition())

    def _write_service_class(self) -> None:
        with self._file.block("namespace lrpc_meta_version"):
            lrpc_version = version("lotusrpc")
            def_version_str = f'"{self._definition_version}"' if self._definition_version else ""
            def_version_hash_str = f'"{self._definition_hash}"' if self._definition_hash else ""
            lrpc_version_str = f'"{lrpc_version}"'

            self._file.write(f"static constexpr etl::string_view DefinitionVersion {{{def_version_str}}};")
            self._file.write(f"static constexpr etl::string_view DefinitionHash {{{def_version_hash_str}}};")
            self._file.write(f"static constexpr etl::string_view LrpcVersion {{{lrpc_version_str}}};")

        self._file.newline()

        with self._file.block("class LrpcMeta_service : public LrpcMeta_shim", ";"):
            self._file.label("public")
            self._file.write("void error() override {}")
            self._file.write("void error_stop() override {}")

            self._file.newline()

            if self._embed_definition:
                with self._file.block("void definition() override"):
                    self._file.write(
                        "etl::span<const LRPC_BYTE_TYPE> data {reinterpret_cast<const LRPC_BYTE_TYPE *>(compressed.begin()), reinterpret_cast<const LRPC_BYTE_TYPE *>(compressed.end())};",
                    )
                    self._file.write("const size_t chunkSize{200};")
                    self._file.write("bool final {false};")

                    with self._file.block("while (!final)"):
                        self._file.write("const auto transmitSize = etl::min<size_t>(data.size(), chunkSize);")
                        self._file.write("final = transmitSize != chunkSize;")
                        self._file.newline()
                        self._file.write("definition_response(data.first(transmitSize), final);")
                        self._file.write("data.advance(transmitSize);")
            else:
                with self._file.block("void definition() override"):
                    self._file.write("definition_response({}, true);")

            self._file.write("void definition_stop() override {}")

            self._file.newline()

            with (
                self._file.block(
                    "std::tuple<etl::string_view, etl::string_view, etl::string_view> version() override",
                ),
                self._file.block("return ", ";"),
            ):
                self._file.write("lrpc_meta_version::DefinitionVersion,")
                self._file.write("lrpc_meta_version::DefinitionHash,")
                self._file.write("lrpc_meta_version::LrpcVersion")

    def _write_definition(self, definition: bytes) -> None:
        self._file2 = CppFile(f"{self._output}/LrpcMeta_definition.hpp")
        self._file2.write("#pragma once")
        self._file2.write("#include <stdint.h>")
        self._file2.write("#include <etl/array.h>")

        self._file2.newline()

        with self._file2.block("namespace lrpc"):
            self._file2.write(f"constexpr size_t compressedSize {{{len(definition)}}};")

            self._file2.newline()

            with self._file2.block("constexpr etl::array<uint8_t, compressedSize> compressed = ", ";"):
                for i in range(0, len(definition), 16):
                    sub = definition[i : i + 16]
                    decls = [f"0x{b:02x}" for b in sub]
                    self._file2.write(", ".join(decls) + ",")
