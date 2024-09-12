from typing import Optional

from lrpc import LrpcVisitor
from lrpc.core import LrpcFun

class LrpcService(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        self.__init_functions_ids()

    def __init_functions_ids(self) -> None:
        last_function_id = -1

        for f in self.raw['functions']:
            if 'id' in f:
                last_function_id = f['id']
            else:
                last_function_id = last_function_id + 1
                f['id'] = last_function_id

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_service(self)
        for f in self.functions():
            f.accept(visitor)
        visitor.visit_lrpc_service_end()

    def name(self) -> str:
        return self.raw['name']

    def id(self):
        return self.raw['id']

    def functions(self):
        return [LrpcFun(f) for f in self.raw['functions']]

    def function_by_name(self, name: str) -> Optional[LrpcFun]:
        for f in self.functions():
            if f.name() == name:
                return f

        return None

    def function_by_id(self, function_id: int) -> Optional[LrpcFun]:
        for f in self.functions():
            if f.id() == function_id:
                return f

        return None
