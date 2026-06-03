from collections.abc import Callable

from lrpc.codegen.cppfile import CppFile


def optionally_in_namespace(file: CppFile, fun: Callable[..., None], namespace: str | None) -> None:
    if namespace:
        with file.block(f"namespace {namespace}"):
            fun()
    else:
        fun()
