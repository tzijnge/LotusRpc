from collections.abc import Callable

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]


def optionally_in_namespace(file: CppFile, fun: Callable[..., None], namespace: str | None) -> None:
    if namespace:
        with file.block(f"namespace {namespace}"):
            fun()
    else:
        fun()
