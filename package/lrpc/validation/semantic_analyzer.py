import logging

from .validator import LrpcValidator
from .service import ServiceValidator
from .function import FunctionValidator
from .enum import EnumValidator
from .names import NamesValidator
from .custom_types import CustomTypesValidator
from ..core import LrpcVar, LrpcDef


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

    def __check_multiple_auto_strings_in_param_list_or_return_list(self) -> None:
        offenders = []
        for s in self.__services:
            for f in s.functions():
                auto_string_params = [(f.name(), p.name()) for p in f.params() if p.is_auto_string()]
                if len(auto_string_params) > 1:
                    offenders.extend(auto_string_params)

        if len(offenders) > 0:
            self.__errors.append(
                f"More than one auto string per parameter list or return value list is not allowed: {offenders}"
            )

    @staticmethod
    def __is_auto_string_array(p: LrpcVar) -> bool:
        if not p.is_auto_string():
            return False

        if p.is_optional():
            return False

        return p.array_size() > 1

    def __check_array_of_auto_strings(self) -> None:
        offenders = []
        for s in self.__services:
            for f in s.functions():
                auto_string_arrays = [(f.name(), p.name()) for p in f.params() if self.__is_auto_string_array(p)]
                offenders.extend(auto_string_arrays)

        if len(offenders) > 0:
            self.__errors.append(f"Array of auto strings is not allowed: {offenders}")

    def __check_return_auto_string(self) -> None:
        offenders = []
        for s in self.__services:
            for f in s.functions():
                auto_string_returns = [(s.name(), f.name(), r.name()) for r in f.returns() if r.is_auto_string()]
                offenders.extend(auto_string_returns)

        if len(offenders) > 0:
            self.__errors.append(f"A function cannot return an auto string: {offenders}")

    def analyze(self, warnings_as_errors: bool) -> None:
        for validator in self.validators:
            self.definition.accept(validator)
            self.__errors.extend(validator.errors())
            self.__warnings.extend(validator.warnings())

        self.__check_duplicate_struct_field_names()
        self.__check_auto_string_in_struct()
        self.__check_multiple_auto_strings_in_param_list_or_return_list()
        self.__check_array_of_auto_strings()
        self.__check_return_auto_string()

        for w in self.__warnings:
            logging.warning(w)

        for e in self.__errors:
            logging.error(e)

        if len(self.__errors) != 0:
            raise ValueError("Errors detected in LRPC definition")

        if warnings_as_errors and (len(self.__warnings) != 0):
            raise ValueError("Warnings detected in LRPC definition and treated as error")
