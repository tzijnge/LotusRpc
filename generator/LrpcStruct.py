from LrpcVar import LrpcVar

class LrpcStruct(object):
    def __init__(self, raw) -> None:
        self.raw = raw

    def name(self):
        return self.raw['name']

    def fields(self):
        return [LrpcVar(f) for f in self.raw['fields']]

    def is_external(self):
        return 'external' in self.raw

    def external_file(self):
        return self.raw.get('external', None)

    def external_namespace(self):
        return self.raw.get('external_namespace', None)
