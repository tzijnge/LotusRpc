from lrpc.core import LrpcFun
from lrpc import LrpcVisitor

class LrpcService(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        self.__init_functions_ids()

    def __init_functions_ids(self):
        last_function_id = -1

        for f in self.raw['functions']:
            if 'id' in f:
                last_function_id = f['id']
            else:
                last_function_id = last_function_id + 1
                f['id'] = last_function_id

    def accept(self, visitor: LrpcVisitor):
        visitor.visit_lrpc_service(self)
        for f in self.functions():
            f.accept(visitor)
        visitor.visit_lrpc_service_end()

    def name(self):
        return self.raw['name']

    def id(self):
        return self.raw['id']

    def functions(self):
        return [LrpcFun(f) for f in self.raw['functions']]
