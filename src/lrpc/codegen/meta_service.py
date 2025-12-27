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
        self._processing_meta_service = False
        self._lines: list[str] = []
        self._definition_version: str | None = None
        self._definition_hash: str | None

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()
        self._file = CppFile(f"{self._output}/LrpcMeta_service.hpp")
        self._definition_version = lrpc_def.version()
        self._definition_hash = lrpc_def.definition_hash()

        write_file_banner(self._file)
        self._file.write("#pragma once")
        self._file.write('#include "LrpcMeta_shim.hpp"')
        self._file.newline()
        optionally_in_namespace(self._file, self._write_service_class, self._namespace)

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

            with (
                self._file.block(
                    "std::tuple<etl::string_view, etl::string_view, etl::string_view> version() override",
                ),
                self._file.block("return ", ";"),
            ):
                self._file.write("lrpc_meta_version::DefinitionVersion,")
                self._file.write("lrpc_meta_version::DefinitionHash,")
                self._file.write("lrpc_meta_version::LrpcVersion")
