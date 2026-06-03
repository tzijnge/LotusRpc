from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from typing import Self, TextIO


class CppFile:
    IWYU_EXPORT = " // IWYU pragma: export"

    def __init__(self, filename: str, *, _writer: Callable[[str], int] | None = None, indent: int = 4) -> None:
        if indent < 0:
            raise ValueError(f"indent must be non-negative, got {indent}")
        self._indent = " " * indent
        self._level = 0
        if _writer is None:
            self._file: TextIO | None = Path(filename).open("w", encoding="utf-8")  # noqa: SIM115  # pylint: disable=consider-using-with
            self._writer: Callable[[str], int] = self._file.write
        else:
            self._file = None
            self._writer = _writer

    @classmethod
    def from_writer(cls, writer: Callable[[str], int], indent: int = 4) -> Self:
        return cls("", _writer=writer, indent=indent)

    def write(self, text: str) -> None:
        prefix = self._indent * self._level if text else ""
        self._writer(prefix + text + "\n")

    def __call__(self, text: str) -> None:
        self.write(text)

    def newline(self) -> None:
        self._writer("\n")

    def pragma_once(self) -> None:
        self.write("#pragma once")

    def include(self, path: str, *, iwyu_export: bool = False) -> None:
        suffix = self.IWYU_EXPORT if iwyu_export else ""
        self.write(f"#include {path}{suffix}")

    def label(self, text: str) -> None:
        self._writer(self._indent * (self._level - 1) + text + ":\n")

    @contextmanager
    def block(self, text: str, postfix: str = "", *, trailing_newline: bool = False) -> Generator[None, None, None]:
        self.write(text)
        self._writer(self._indent * self._level + "{\n")
        self._level += 1
        try:
            yield
        finally:
            self._level -= 1
            self._writer(self._indent * self._level + "}" + postfix + "\n")
            if trailing_newline:
                self._writer("\n")

    def __enter__(self) -> Self:
        return self

    def close(self) -> None:
        self.__exit__(None, None, None)

    def __exit__(self, *_: object) -> None:
        if self._file is not None:
            self._file.close()
