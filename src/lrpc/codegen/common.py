from importlib.metadata import version

from lrpc.codegen.cppfile import CppFile
from lrpc.core import LrpcVar


def lrpc_var_includes(var: LrpcVar) -> set[tuple[str, bool]]:
    includes: set[tuple[str, bool]] = set()
    if var.base_type_is_integral():
        includes.add(("<cstdint>", True))

    if var.base_type_is_custom():
        includes.add((f'"{var.base_type()}.hpp"', True))

    if var.base_type_is_bytearray():
        includes.add(('"lrpccore/LrpcByteTypes.hpp"', True))
    elif var.base_type_is_string() or var.is_array() or var.is_optional():
        includes.add(('"lrpccore/LrpcTypes.hpp"', True))

    return includes


def write_file_banner(file: CppFile) -> None:
    v = version("lotusrpc")
    file.write(f"// This file has been generated with LRPC version {v}")
    file.newline()
