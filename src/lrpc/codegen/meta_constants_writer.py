from importlib.metadata import version

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.utils import optionally_in_namespace


# pylint: disable = too-few-public-methods
class MetaConstantsWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file
        self._definition_version: str | None = None
        self._definition_hash: str | None = None
        self._compressed_definition = b""
        self._definition_stream_chunk_size: int = 0

    # pylint: disable = too-many-arguments
    # pylint: disable = too-many-positional-arguments
    def write_constants(
        self,
        definition_version: str | None,
        definition_hash: str | None,
        compressed_definition: bytes,
        definition_stream_chunk_size: int,
        namespace: str | None = None,
    ) -> None:
        self._definition_version = definition_version
        self._definition_hash = definition_hash
        self._compressed_definition = compressed_definition
        self._definition_stream_chunk_size = definition_stream_chunk_size

        self._file.write("#pragma once")
        self._file.write("#include <stdint.h>")
        self._file.write("#include <etl/array.h>")
        self._file.write("#include <etl/string_view.h>")

        self._file.newline()
        optionally_in_namespace(self._file, self._write_constants, namespace)

    def _write_constants(self) -> None:
        with self._file.block("namespace lrpc_meta"):
            self._write_version_constants()
            self._file.newline()
            self._write_definition_constants()

    def _write_version_constants(self) -> None:
        lrpc_version = version("lotusrpc")
        def_version_str = f'"{self._definition_version}"' if self._definition_version else ""
        def_version_hash_str = f'"{self._definition_hash}"' if self._definition_hash else ""
        lrpc_version_str = f'"{lrpc_version}"'

        self._file.write(f"static constexpr etl::string_view DefinitionVersion {{{def_version_str}}};")
        self._file.write(f"static constexpr etl::string_view DefinitionHash {{{def_version_hash_str}}};")
        self._file.write(f"static constexpr etl::string_view LrpcVersion {{{lrpc_version_str}}};")

    def _write_definition_constants(self) -> None:
        chunk_size = self._definition_stream_chunk_size
        comp_def = self._compressed_definition
        comp_def_size = len(comp_def)

        self._file.write(f"static constexpr size_t DefinitionStreamChunkSize {{{chunk_size}}};")
        self._file.newline()

        with self._file.block(
            f"static constexpr etl::array<uint8_t, {comp_def_size}> CompressedDefinition =",
            ";",
        ):
            if comp_def_size == 0:
                self._file.write(
                    "// Use the 'embed_definition' setting in the definition file "
                    "to embed the definition in the generated server code",
                )
                return

            bytes_per_line = 16
            for i in range(0, comp_def_size, bytes_per_line):
                sub = comp_def[i : i + bytes_per_line]
                hex_values = [f"0x{b:02x}" for b in sub]
                self._file.write(", ".join(hex_values) + ",")
