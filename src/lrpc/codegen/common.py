from importlib.metadata import version
from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..core import LrpcVar


def lrpc_var_includes(var: LrpcVar) -> set[str]:
    includes = set()
    if var.base_type_is_integral():
        includes.add("<stdint.h>")

    if var.base_type_is_custom():
        includes.add(f'"{var.base_type()}.hpp"')

    if var.base_type_is_string():
        includes.add("<etl/string.h>")
        includes.add("<etl/string_view.h>")

    if var.is_array():
        includes.add("<etl/span.h>")

    if var.is_optional():
        includes.add("<etl/optional.h>")

    return includes


def write_file_banner(file: CppFile) -> None:
    v = version("lotusrpc")
    file.write(f"// This file has been generated with LRPC version {v}")
    file.newline()
