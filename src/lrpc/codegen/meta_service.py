from pathlib import Path

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.meta_constants_writer import MetaConstantsWriter
from lrpc.codegen.meta_service_file_writer import MetaServiceFileWriter
from lrpc.core import LrpcDef
from lrpc.visitors import LrpcVisitor


class MetaServiceVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._namespace: str | None
        self._output = output
        self._service_file: CppFile
        self._constants_file: CppFile
        self._definition_version: str | None = None
        self._definition_hash: str | None
        self._compressed_definition = b""
        self._definition_stream_chunk_size: int

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()
        self._service_file = CppFile(f"{self._output}/LrpcMeta_service.hpp")
        self._constants_file = CppFile(f"{self._output}/LrpcMeta_constants.hpp")
        self._definition_version = lrpc_def.version()
        self._definition_hash = lrpc_def.definition_hash()

        if lrpc_def.embed_definition():
            self._compressed_definition = lrpc_def.compressed_definition()

        # TX buffer size - 5 to account for
        # - Message size field
        # - Service ID field
        # - Stream ID field
        # - Bytearray length field
        # - Stream final parameter
        self._definition_stream_chunk_size = lrpc_def.tx_buffer_size() - 5

        self._write_service_file()
        self._write_constants_file()

    def _write_constants_file(self) -> None:
        write_file_banner(self._constants_file)
        writer = MetaConstantsWriter(self._constants_file)
        writer.write_constants(
            self._definition_version,
            self._definition_hash,
            self._compressed_definition,
            self._definition_stream_chunk_size,
            self._namespace,
        )

    def _write_service_file(self) -> None:
        write_file_banner(self._service_file)
        writer = MetaServiceFileWriter(self._service_file)
        writer.write_service(self._namespace)
