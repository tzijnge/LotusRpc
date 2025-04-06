import logging

from .validator import LrpcValidator
from .service import ServiceValidator
from .function import FunctionValidator
from .enum import EnumValidator
from .names import NamesValidator
from .custom_types import CustomTypesValidator
from ..core import LrpcDef


# pylint: disable = too-few-public-methods
class SemanticAnalyzer:
    def __init__(self, definition: LrpcDef) -> None:
        self.__errors: list[str] = []
        self.__warnings: list[str] = []
        self.definition = definition
        self.__services = definition.services()
        self.validators: list[LrpcValidator] = [
            ServiceValidator(),
            FunctionValidator(),
            EnumValidator(),
            NamesValidator(),
            CustomTypesValidator(),
        ]

    @staticmethod
    def __duplicates(input_list: list[tuple[str, str]]) -> list[tuple[str, str]]:
        unique: list[tuple[str, str]] = []
        duplicates: list[tuple[str, str]] = []

        for n in input_list:
            if n in unique:
                duplicates.append(n)
            else:
                unique.append(n)

        return duplicates

    def __check_duplicate_struct_field_names(self) -> None:
        duplicate_names = []
        for s in self.definition.structs():
            names = [(s.name(), field.name()) for field in s.fields()]
            duplicate_names.extend(self.__duplicates(names))

        if len(duplicate_names) > 0:
            self.__errors.append(f"Duplicate struct field name(s): {duplicate_names}")

    def __check_auto_string_in_struct(self) -> None:
        offenders = []
        for s in self.definition.structs():
            auto_strings = [(s.name(), f.name()) for f in s.fields() if f.is_auto_string()]
            offenders.extend(auto_strings)

        if len(offenders) > 0:
            self.__errors.append(f"Auto string not allowed in struct: {offenders}")


    def analyze(self, warnings_as_errors: bool) -> None:
        for validator in self.validators:
            self.definition.accept(validator)
            self.__errors.extend(validator.errors())
            self.__warnings.extend(validator.warnings())

        self.__check_duplicate_struct_field_names()
        self.__check_auto_string_in_struct()

        for w in self.__warnings:
            logging.warning(w)

        for e in self.__errors:
            logging.error(e)

        if len(self.__errors) != 0:
            raise ValueError("Errors detected in LRPC definition")

        if warnings_as_errors and (len(self.__warnings) != 0):
            raise ValueError("Warnings detected in LRPC definition and treated as error")
