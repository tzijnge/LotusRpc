from LrpcVar import LrpcVar

class LrpcFun(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        if 'params' not in self.raw:
            self.raw['params'] = list()
        if 'returns' not in self.raw:
            self.raw['returns'] = list()

    def params(self):
        return [LrpcVar(p) for p in self.raw['params']]

    def returns(self):
        return [LrpcVar(r) for r in self.raw['returns']]

    def name(self):
        return self.raw['name']

    def id(self):
        return self.raw['id']

    def number_returns(self):
        return len(self.returns())

    def param_names(self):
        return [p.name() for p in self.params()]

    def required_includes(self):
        includes = set()
        for p in self.params() + self.returns():
            includes.update(p.required_includes())

        if len(self.returns()) > 1:
            includes.update({'<tuple>'})

        return includes
