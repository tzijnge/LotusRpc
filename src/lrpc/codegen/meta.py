import os
from importlib.metadata import version
from typing import Optional

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..codegen.common import write_file_banner
from ..codegen.utils import optionally_in_namespace
from ..core import LrpcDef
from ..visitors import LrpcVisitor


class MetaFileVisitor(LrpcVisitor):

    def __init__(self, output: os.PathLike[str]) -> None:
        self.__output = output
        self.__file: CppFile
        self.__namespace: Optional[str] = None
        self.__version: Optional[str] = None

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__file = CppFile(f"{self.__output}/{lrpc_def.name()}_Meta.hpp")
        self.__namespace = lrpc_def.namespace()
        self.__version = lrpc_def.version()

        write_file_banner(self.__file)
        self.__write_includes()
        optionally_in_namespace(self.__file, self.__write_attributes, self.__namespace)

    def __write_includes(self) -> None:
        self.__file.write("#include <etl/string_view.h>")
        self.__file.newline()

    def __write_attributes(self) -> None:
        with self.__file.block("namespace meta"):
            lrpc_version = version("lotusrpc")
            lrpc_version_string = f'"{lrpc_version}"'

            self.__file.write(f"constexpr etl::string_view LrpcVersion {{{lrpc_version_string}}};")

            self.__file.newline()

            if self.__version:
                definition_version = f'"{self.__version}"'
                self.__file.write(f"constexpr etl::string_view DefinitionVersion {{{definition_version}}};")
            else:
                self.__file.write(
                    "// Define a version in the definition file to generate a DefinitionVersion constant here"
                )
