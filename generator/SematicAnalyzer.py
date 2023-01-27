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
        duplicate_ids = list()
        for i in self.__interfaces:
            ids = [(i['name'], f['id']) for f in i['functions']]
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

    def __check_duplicate_interface_names(self):
        names = [i['name'] for i in self.__interfaces]
        duplicate_names = self.__duplicates(names)
        if len(duplicate_names) > 0:
            self.errors.append(f'Duplicate interface name(s): {duplicate_names}')

    def __check_duplicate_function_names(self):
        duplicate_names = list()
        for i in self.__interfaces:
            names = [(i['name'], f['name']) for f in i['functions']]
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
        all_declared_structs = [s['name'] for s in self.__structs]
        all_declared_enums = [e['name'] for e in self.__enums]
        all_declared_types = all_declared_structs + all_declared_enums
        
        all_used_types = list()
        for i in self.__interfaces:
            for f in i['functions']:
                all_used_types.extend([p['type'] for p in f.get('params', list())])
                all_used_types.extend([r['type'] for r in f.get('returns', list())])

        for s in self.__structs:
            all_used_types.extend([f['type'] for f in s['fields']])

        used_custom_types = [t.strip('@') for t in all_used_types if t.startswith('@')]

        all_undeclared_types = [t for t in used_custom_types if t not in all_declared_types]

        if len(all_undeclared_types) > 0:
            self.errors.append(f'Undeclared custom type(s): {sorted(set(all_undeclared_types))}')


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
        self.__check_duplicate_struct_enum_names()
        self.__check_duplicate_enum_field_names()
        self.__check_duplicate_struct_field_names()
        self.__check_undeclared_custom_types()
