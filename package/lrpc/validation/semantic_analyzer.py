from typing import List
from lrpc.core import LrpcDef
from lrpc.validation import ServiceChecker, FunctionChecker, EnumChecker, NamesChecker, CustomTypesChecker

class SemanticAnalyzer(object):
    errors : List[str]
    warnings : List[str]

    def __init__(self, definition: LrpcDef) -> None:
        self.errors = list()
        self.warnings = list()
        self.definition = definition
        self.__services = definition.services()
        self.checkers = [
            ServiceChecker(),
            FunctionChecker(),
            EnumChecker(),
            NamesChecker(),
            CustomTypesChecker()
        ]

    def __duplicates(self, input):
        unique = list()
        duplicates = list()

        for n in input:
            if n in unique:
                duplicates.append(n)
            else:
                unique.append(n)

        return duplicates

    def __check_duplicate_struct_field_names(self):
        duplicate_names = list()
        for s in self.definition.structs():
            names = [(s.name(), field.name()) for field in s.fields()]
            duplicate_names.extend(self.__duplicates(names))
            
        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate struct field name(s): {duplicate_names}')

    def __check_auto_string_in_struct(self):
        offenders = list()
        for s in self.definition.structs():
            auto_strings = [(s.name(), f.name()) for f in s.fields() if f.is_auto_string()]
            offenders.extend(auto_strings)

        if len(offenders) > 0:
            self.errors.append(f'Auto string not allowed in struct: {offenders}')

    def __check_multiple_auto_strings_in_param_list_or_return_list(self):
        offenders = list()
        for s in self.__services:
            for f in s.functions():
                auto_string_params = [(f.name(), p.name()) for p in f.params() if p.is_auto_string()]
                if len(auto_string_params) > 1:
                    offenders.extend(auto_string_params)

        if len(offenders) > 0:
            self.errors.append(f'More than one auto string per parameter list or return value list is not allowed: {offenders}')

    def __is_auto_string_array(self, p):
        if not p.is_auto_string():
            return False

        if p.is_optional():
            return False

        return p.array_size() > 1

    def __check_array_of_auto_strings(self):
        offenders = list()
        for s in self.__services:
            for f in s.functions():
                auto_string_arrays = [(f.name(), p.name()) for p in f.params() if self.__is_auto_string_array(p)]
                offenders.extend(auto_string_arrays)

        if len(offenders) > 0:
            self.errors.append(f'Array of auto strings is not allowed: {offenders}')

    def __check_return_auto_string(self):
        offenders = list()
        for s in self.__services:
            for f in s.functions():
                auto_string_returns = [(s.name(), f.name(), r.name()) for r in f.returns() if r.is_auto_string()]
                offenders.extend(auto_string_returns)

        if len(offenders) > 0:
            self.errors.append(f'A function cannot return an auto string: {offenders}')

    def analyze(self) -> None:
        for checker in self.checkers:
            self.definition.accept(checker)
            self.errors.extend(checker.errors)
            self.warnings.extend(checker.warnings)

        self.__check_duplicate_struct_field_names()
        self.__check_auto_string_in_struct()
        self.__check_multiple_auto_strings_in_param_list_or_return_list()
        self.__check_array_of_auto_strings()
        self.__check_return_auto_string()
