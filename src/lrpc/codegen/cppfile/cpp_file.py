from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import TextIO


class CppFile:
    IWYU_EXPORT = " // IWYU pragma: export"

    def __init__(self, filename: str, writer: TextIO | None = None, indent: str = "    ") -> None:
        self._indent = indent
        self._level = 0
        self._owns_file = writer is None
        self._file: TextIO = Path(filename).open("w") if writer is None else writer  # noqa: SIM115

    def write(self, text: str) -> None:
        prefix = self._indent * self._level if text else ""
        self._file.write(prefix + text + "\n")

    def __call__(self, text: str) -> None:
        self.write(text)

    def newline(self) -> None:
        self._file.write("\n")

    def pragma_once(self) -> None:
        self.write("#pragma once")

    def include(self, path: str, *, iwyu_export: bool = False) -> None:
        suffix = self.IWYU_EXPORT if iwyu_export else ""
        self.write(f"#include {path}{suffix}")

    def label(self, text: str) -> None:
        self._file.write(self._indent * (self._level - 1) + text + ":\n")

    @contextmanager
    def block(self, text: str, postfix: str = "", *, trailing_newline: bool = False) -> Generator[None, None, None]:
        self.write(text)
        self._file.write(self._indent * self._level + "{\n")
        self._level += 1
        try:
            yield
        finally:
            self._level -= 1
            self._file.write(self._indent * self._level + "}" + postfix + "\n")
            if trailing_newline:
                self._file.write("\n")

    def close(self) -> None:
        if self._owns_file:
            self._file.close()
