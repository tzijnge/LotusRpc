from LrpcVar import LrpcVar
from LrpcVisitor import LrpcVisitor
from abc import ABC
from typing import Optional

from LrpcStructBase import LrpcStructBase

class LrpcStruct(LrpcStructBase):
    def __init__(self, raw) -> None:
        self.raw = raw

    def accept(self, visitor: LrpcVisitor):
        visitor.visit_lrpc_struct(self)
        for f in self.fields():
            visitor.visit_lrpc_struct_field(f)
        visitor.visit_lrpc_struct_field_end()

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
