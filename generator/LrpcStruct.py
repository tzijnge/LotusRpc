from LrpcVar import LrpcVar

class LrpcStruct(object):
    def __init__(self, raw) -> None:
        self.raw = raw

    def name(self):
        return self.raw['name']

    def fields(self):
        return [LrpcVar(f) for f in self.raw['fields']]
