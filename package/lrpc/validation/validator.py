import abc
from ..visitors import LrpcVisitor


class LrpcValidator(LrpcVisitor):
    @abc.abstractmethod
    def errors(self) -> list[str]:
        """Errors found by the validator"""

    @abc.abstractmethod
    def warnings(self) -> list[str]:
        """Warnings found by the validator"""
