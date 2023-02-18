from LrpcService import LrpcService

class LrpcDef(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        if 'structs' not in self.raw:
            self.raw['structs'] = list()
        if 'enums' not in self.raw:
            self.raw['enums'] = list()
        
        for s in self.raw['services']:
            for f in s['functions']:
                for p in f.get('params', list()):
                    p['base_type_is_struct'] = self.__base_type_is_struct(p)
                    p['base_type_is_enum'] = self.__base_type_is_enum(p)
                for r in f.get('returns', list()):
                    r['base_type_is_struct'] = self.__base_type_is_struct(r)
                    r['base_type_is_enum'] = self.__base_type_is_enum(r)

        for s in self.raw['structs']:
            for f in s['fields']:
                f['base_type_is_struct'] = self.__base_type_is_struct(f)
                f['base_type_is_enum'] = self.__base_type_is_enum(f)

    def name(self):
        return self.raw['name']
    
    def namespace(self):
        return self.raw['namespace']

    def services(self):
        return [LrpcService(s) for s in self.raw['services']]

    def structs(self):
        return self.raw['structs']

    def enums(self):
        return self.raw['enums']

    def __struct_names(self):
        return [s['name'] for s in self.raw['structs']]

    def __enum_names(self):
        return [e['name'] for e in self.raw['enums']]

    def __base_type_is_struct(self, var):
        return var['type'].strip('@') in self.__struct_names()

    def __base_type_is_enum(self, var):
        return var['type'].strip('@') in self.__enum_names()
