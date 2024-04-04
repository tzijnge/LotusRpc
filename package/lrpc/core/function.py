from lrpc.core import LrpcVar
from lrpc import LrpcVisitor

class LrpcFun(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        self.__init_params()
        self.__init_returns()

    def __init_returns(self):
        if 'returns' not in self.raw:
            self.raw['returns'] = list()

    def __init_params(self):
        if 'params' not in self.raw:
            self.raw['params'] = list()

    def accept(self, visitor: LrpcVisitor):
        visitor.visit_lrpc_function(self)
        
        for r in self.returns():
            visitor.visit_lrpc_function_return(r)
        visitor.visit_lrpc_function_return_end()

        for p in self.params():
            visitor.visit_lrpc_function_param(p)
        visitor.visit_lrpc_function_param_end()

        visitor.visit_lrpc_function_end()

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
