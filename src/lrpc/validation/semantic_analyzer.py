import logging

from .validator import LrpcValidator
from .service import ServiceValidator
from .function_and_stream import FunctionAndStreamIdValidator, FunctionAndStreamNameValidator
from .param_and_return import ParamAndReturnValidator
from .enum import EnumValidator
from .struct import StructValidator
from .names import NamesValidator
from .custom_types import CustomTypesValidator
from ..core import LrpcDef


# pylint: disable = too-few-public-methods
class SemanticAnalyzer:
    def __init__(self, definition: LrpcDef) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.definition = definition
        self.validators: list[LrpcValidator] = [
            ServiceValidator(),
            ParamAndReturnValidator(),
            FunctionAndStreamIdValidator(),
            FunctionAndStreamNameValidator(),
            EnumValidator(),
            StructValidator(),
            NamesValidator(),
            CustomTypesValidator(),
        ]

    def analyze(self, warnings_as_errors: bool) -> None:
        for validator in self.validators:
            self.definition.accept(validator)
            self.__errors.extend(validator.errors())
            self.__warnings.extend(validator.warnings())

        for w in self.__warnings:
            logging.warning(w)

        for e in self.__errors:
            logging.error(e)

        if len(self.__errors) != 0:
            raise ValueError("Errors detected in LRPC definition")

        if warnings_as_errors and (len(self.__warnings) != 0):
            raise ValueError("Warnings detected in LRPC definition and treated as error")
