class LrpcEnumField(object):
    def __init__(self, raw) -> None:
        self.raw = raw

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
        return [LrpcEnumField(f) for f in self.raw['fields']]
