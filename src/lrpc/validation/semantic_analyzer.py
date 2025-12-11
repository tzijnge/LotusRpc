import logging
from typing import TYPE_CHECKING

from ..core import LrpcDef
from .custom_types import CustomTypesValidator
from .enum import EnumValidator
from .function_and_stream import FunctionAndStreamIdValidator, FunctionAndStreamNameValidator
from .names import NamesValidator
from .param_and_return import ParamAndReturnValidator
from .service import ServiceValidator
from .struct import StructValidator

if TYPE_CHECKING:
    from .validator import LrpcValidator


# pylint: disable = too-few-public-methods
class SemanticAnalyzer:
    def __init__(self, definition: LrpcDef) -> None:
        self._errors: list[str] = []
        self._warnings: list[str] = []
        self._definition = definition
        self._validators: list[LrpcValidator] = [
            ServiceValidator(),
            ParamAndReturnValidator(),
            FunctionAndStreamIdValidator(),
            FunctionAndStreamNameValidator(),
            EnumValidator(),
            StructValidator(),
            NamesValidator(),
            CustomTypesValidator(),
        ]

        self._log = logging.getLogger(self.__class__.__name__)

    def analyze(self, *, warnings_as_errors: bool) -> None:
        for validator in self._validators:
            self._definition.accept(validator)
            self._errors.extend(validator.errors())
            self._warnings.extend(validator.warnings())

        for w in self._warnings:
            self._log.warning(w)

        for e in self._errors:
            self._log.error(e)

        if len(self._errors) != 0:
            raise ValueError("Errors detected in LRPC definition")

        if warnings_as_errors and (len(self._warnings) != 0):
            raise ValueError("Warnings detected in LRPC definition and treated as error")
