from lrpc.core import LrpcVar
from lrpc import LrpcVisitor

class LrpcStruct(object):
    def __init__(self, raw) -> None:
        self.raw = raw

    def accept(self, visitor: LrpcVisitor):
        visitor.visit_lrpc_struct(self)

        for f in self.fields():
            visitor.visit_lrpc_struct_field(f)

        visitor.visit_lrpc_struct_end()

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
