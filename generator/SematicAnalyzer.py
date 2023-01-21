from typing import List

class SemanticAnalyzer(object):
    errors : List[str]

    def __init__(self) -> None:
        self.errors = list()
        self.__interfaces = list()
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

    def __check_duplicate_interface_ids(self):
        ids = [i['id'] for i in self.__interfaces]
        duplicate_ids = self.__duplicates(ids)
        if len(duplicate_ids) > 0:
            self.errors.append(f'Duplicate interface id(s): {duplicate_ids}')

    def __check_duplicate_function_ids(self):
        pass

    def __check_duplicate_enum_field_ids(self):
        duplicate_ids = list()
        for e in self.__enums:
            ids = [(e['name'], field['id']) for field in e['fields']]
            duplicate_ids.extend(self.__duplicates(ids))
            
        if len(duplicate_ids) > 0:
            self.errors.append(f'Duplicate enum field id(s): {duplicate_ids}')

    def __check_duplicate_interface_names(self):
        names = [i['name'] for i in self.__interfaces]
        duplicate_names = self.__duplicates(names)
        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate interface name(s): {duplicate_names}')

    def __check_duplicate_function_names(self):
        pass

    def __check_duplicate_enum_names(self):
        duplicate_names = list()
        for e in self.__enums:
            names = [(e['name'], field['name']) for field in e['fields']]
            duplicate_names.extend(self.__duplicates(names))
            
        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate enum name(s): {duplicate_names}')

    def __check_duplicate_enum_field_names(self):
        pass

    def __check_duplicate_struct_names(self):
        pass

    def __check_duplicate_struct_field_names(self):
        pass


    def analyze(self, definition) -> None:
        self.__interfaces = definition['interfaces']
        if 'enums' in definition:
            self.__enums = definition['enums']
        if 'structs' in definition:
            self.__structs = definition['structs']

        self.__check_duplicate_interface_ids()
        self.__check_duplicate_function_ids()
        self.__check_duplicate_enum_field_ids()
        self.__check_duplicate_interface_names()
        self.__check_duplicate_function_names()
        self.__check_duplicate_enum_names()
        self.__check_duplicate_enum_field_names()
        self.__check_duplicate_struct_names()
        self.__check_duplicate_struct_field_names()
