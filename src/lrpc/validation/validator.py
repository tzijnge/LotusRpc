from ..visitors import LrpcVisitor


class LrpcValidator(LrpcVisitor):
    def __init__(self) -> None:
        self._errors: set[str] = set()
        self._warnings: set[str] = set()

    def reset(self) -> None:
        self._errors.clear()
        self._warnings.clear()

    def errors(self) -> set[str]:
        return self._errors

    def add_error(self, error: str) -> None:
        self._errors.add(error)

    def warnings(self) -> set[str]:
        return self._warnings

    def add_warning(self, warning: str) -> None:
        self._warnings.add(warning)
