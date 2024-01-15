class LrpcEnumField(object):
    def __init__(self, raw, index) -> None:
        self.raw = raw

        if isinstance(self.raw, str):
            self.raw = {'name': raw, 'id': index}

    def name(self):
        return self.raw['name']
    
    def id(self):
        return self.raw['id']

class LrpcEnum(object):
    def __init__(self, raw) -> None:
        self.raw = raw

    def name(self):
        return self.raw['name']

    def fields(self):
        all_fields = list()
        for (index, field) in enumerate(self.raw['fields']):
            all_fields.append(LrpcEnumField(field, index))
        
        return all_fields

    def is_external(self):
        return 'external' in self.raw

    def external_file(self):
        return self.raw.get('external', None)

    def external_namespace(self):
        return self.raw.get('external_namespace', None)
