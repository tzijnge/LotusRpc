from LrpcFun import LrpcFun

class LrpcService(object):
    def __init__(self, raw, structs) -> None:
        self.raw = raw
        self.structs = structs

    def name(self):
        return self.raw['name']

    def id(self):
        return self.raw['id']

    def functions(self):
        return [LrpcFun(f, self.structs) for f in self.raw['functions']]

    def required_includes(self):
        includes = set()
        for f in self.functions():
            includes.update(f.required_includes())

        return includes