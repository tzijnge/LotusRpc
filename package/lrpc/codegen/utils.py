from typing import Callable, Optional


def optionally_in_namespace(func: Callable) -> Callable:
    """Decorator to generate code in a namespace or not"""

    def wrapper(self, namespace: Optional[str]) -> None:
        if namespace:
            with self.file.block(f"namespace {namespace}"):
                func(self)
        else:
            func(self)

    return wrapper
