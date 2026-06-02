from pathlib import Path

from lrpc.codegen.common import write_file_banner
from lrpc.codegen.cppfile import CppFile
from lrpc.core.settings import LrpcByteType


def write_byte_types_file(output: Path, byte_type: LrpcByteType) -> None:
    with CppFile(f"{output}/LrpcByteTypes.hpp") as file:
        write_file_banner(file)
        ByteTypesFileWriter(file, byte_type).write()


class ByteTypesFileWriter:
    def __init__(self, file: CppFile, byte_type: LrpcByteType) -> None:
        self._file = file
        self._byte_type = byte_type

    def write(self) -> None:
        self._file.pragma_once()

        byte_header = self._byte_header()
        if byte_header is not None:
            self._file.newline()
            self._file.include(byte_header)

        self._file.newline()
        self._file.include('"LrpcTypes.hpp"')
        self._file.newline()

        with self._file.block("namespace lrpc"):
            self._file.write(f"using byte = {self._byte_type};")
            self._file.write('static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");')
            self._file.newline()
            self._file.write("using bytearray = etl::span<const byte>;")

    def _byte_header(self) -> str | None:
        if self._byte_type in ("uint8_t", "int8_t"):
            return "<cstdint>"
        if self._byte_type == "etl::byte":
            return "<etl/byte.h>"
        if self._byte_type == "std::byte":
            return "<cstddef>"
        return None
