from typing import Callable


def optionally_in_namespace(func: Callable) -> Callable:
    """Decorator to generate code in a namespace or not"""

    def wrapper(self, namespace: str | None) -> None:
        if namespace:
            with self.file.block(f"namespace {namespace}"):
                func(self)
        else:
            func(self)

    return wrapper
