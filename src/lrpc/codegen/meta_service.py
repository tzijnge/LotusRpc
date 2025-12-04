from pathlib import Path
from typing import Optional

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]
from ..visitors import LrpcVisitor
from ..codegen.common import write_file_banner
from ..codegen.utils import optionally_in_namespace
from ..core import LrpcDef, LrpcService, LrpcStream


class MetaServiceVisitor(LrpcVisitor):
    def __init__(self, output: Path) -> None:
        self._namespace: Optional[str]
        self._output = output
        self._file: CppFile
        self._processing_meta_service = False
        self._lines: list[str] = []

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self._namespace = lrpc_def.namespace()
        self._file = CppFile(f"{self._output}/LrpcMeta_service.hpp")

        write_file_banner(self._file)
        self._file.write("#pragma once")
        self._file.write('#include "LrpcMeta_shim.hpp"')
        self._file.newline()
        optionally_in_namespace(self._file, self._write_service_class, self._namespace)

    def _write_service_class(self) -> None:
        with self._file.block("class LrpcMeta_service : public LrpcMeta_shim", ";"):
            self._file.write("void error() override {};")
            self._file.write("void error_stop() override {};")
