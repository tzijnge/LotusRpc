from typing import List
from LrpcDef import LrpcDef
class SemanticAnalyzer(object):
    errors : List[str]
    warnings : List[str]

    def __init__(self) -> None:
        self.errors = list()
        self.warnings = list()
        self.__services = list()
        self.__enums = list()
        self.__structs = list()

    def __duplicates(self, input):
        unique = list()
        duplicates = list()

        for n in input:
          if n in unique:
            duplicates.append(n)
          else:
            unique.append(n)

        return duplicates

    def __check_duplicate_service_ids(self):
        ids = [s.id() for s in self.__services]
        duplicate_ids = self.__duplicates(ids)
        if len(duplicate_ids) > 0:
            self.errors.append(f'Duplicate service id(s): {duplicate_ids}')

    def __check_duplicate_function_ids(self):
        duplicate_ids = list()
        for s in self.__services:
            ids = [(s.name(), f.id()) for f in s.functions()]
            duplicate_ids.extend(self.__duplicates(ids))

        if len(duplicate_ids) > 0:
            self.errors.append(f'Duplicate function id(s): {duplicate_ids}')

    def __check_duplicate_enum_field_ids(self):
        duplicate_ids = list()
        for e in self.__enums:
            ids = [(e['name'], field['id']) for field in e['fields']]
            duplicate_ids.extend(self.__duplicates(ids))
            
        if len(duplicate_ids) > 0:
            self.errors.append(f'Duplicate enum field id(s): {duplicate_ids}')

    def __check_duplicate_service_names(self):
        names = [s.name() for s in self.__services]
        duplicate_names = self.__duplicates(names)
        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate service name(s): {duplicate_names}')

    def __check_duplicate_function_names(self):
        duplicate_names = list()
        for s in self.__services:
            names = [(s.name(), f.name()) for f in s.functions()]
            duplicate_names.extend(self.__duplicates(names))

        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate function name(s): {duplicate_names}')

    def __check_duplicate_struct_enum_names(self):
        custom_types = self.__enums + self.__structs
        names = [ct['name'] for ct in custom_types]
        duplicate_names = self.__duplicates(names)

        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate struct/enum name(s): {duplicate_names}')

    def __check_duplicate_enum_field_names(self):
        duplicate_names = list()
        for e in self.__enums:
            names = [(e['name'], field['name']) for field in e['fields']]
            duplicate_names.extend(self.__duplicates(names))
            
        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate enum field name(s): {duplicate_names}')

    def __check_duplicate_struct_field_names(self):
        duplicate_names = list()
        for s in self.__structs:
            names = [(s['name'], field['name']) for field in s['fields']]
            duplicate_names.extend(self.__duplicates(names))
            
        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate struct field name(s): {duplicate_names}')

    def __check_undeclared_custom_types(self):
        custom_types = self.__custom_types()
        used_custom_types = self.__used_custom_types()

        all_undeclared_types = [t for t in used_custom_types if t not in custom_types]

        if len(all_undeclared_types) > 0:
            self.errors.append(f'Undeclared custom type(s): {sorted(set(all_undeclared_types))}')

    def __custom_types(self):
        all_declared_structs = [s['name'] for s in self.__structs]
        all_declared_enums = [e['name'] for e in self.__enums]
        return all_declared_structs + all_declared_enums

    def __used_custom_types(self):
        used_custom_types = list()
        for s in self.__services:
            for f in s.functions():
                used_custom_types.extend([p.base_type() for p in f.params() if p.base_type_is_custom()])
                used_custom_types.extend([r.base_type() for r in f.returns() if r.base_type_is_custom()])

        for s in self.__structs:
            used_custom_types.extend([f['type'].strip('@') for f in s['fields'] if ('@' in f['type'])])

        return used_custom_types

    def __check_auto_string_in_struct(self):
        offenders = list()
        for s in self.__structs:
            auto_strings = [(s['name'], f['name']) for f in s['fields'] if f['type'] == 'string_auto']
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

    def __check_custom_types_not_used(self):
        custom_types = self.__custom_types()
        used_custom_types = self.__used_custom_types()
        unused_custom_types = [t for t in custom_types if t not in used_custom_types]

        if len(unused_custom_types) > 0:
            self.warnings.append(f'Unused custom type(s): {unused_custom_types}')

    def __check_return_auto_string(self):
        offenders = list()
        for s in self.__services:
            for f in s.functions():
                auto_string_returns = [(s.name(), f.name(), r.name()) for r in f.returns() if r.is_auto_string()]
                offenders.extend(auto_string_returns)

        if len(offenders) > 0:
            self.errors.append(f'A function cannot return an auto string: {offenders}')

    def analyze(self, definition) -> None:
        self.__services = LrpcDef(definition).services()
        if 'enums' in definition:
            self.__enums = definition['enums']
        if 'structs' in definition:
            self.__structs = definition['structs']

        self.__check_duplicate_service_ids()
        self.__check_duplicate_function_ids()
        self.__check_duplicate_enum_field_ids()
        self.__check_duplicate_service_names()
        self.__check_duplicate_function_names()
        self.__check_duplicate_struct_enum_names()
        self.__check_duplicate_enum_field_names()
        self.__check_duplicate_struct_field_names()
        self.__check_undeclared_custom_types()
        self.__check_auto_string_in_struct()
        self.__check_multiple_auto_strings_in_param_list_or_return_list()
        self.__check_array_of_auto_strings()
        self.__check_custom_types_not_used()
        self.__check_return_auto_string()
