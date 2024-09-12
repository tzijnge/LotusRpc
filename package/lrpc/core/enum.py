from typing import List

from lrpc import LrpcVisitor


class LrpcEnumField(object):
    def __init__(self, raw, index) -> None:
        self.raw = raw

        if isinstance(self.raw, dict) and 'id' not in self.raw:
            self.raw['id'] = index

        if isinstance(self.raw, str):
            self.raw = {'name': raw, 'id': index}

    def name(self):
        return self.raw['name']

    def id(self):
        return self.raw['id']

class LrpcEnum(object):
    def __init__(self, raw) -> None:
        self.raw = raw

    def accept(self, visitor: LrpcVisitor):
        visitor.visit_lrpc_enum(self)

        for f in self.fields():
            visitor.visit_lrpc_enum_field(self, f)

        visitor.visit_lrpc_enum_end(self)

    def name(self):
        return self.raw['name']

    def fields(self) -> List[LrpcEnumField]:
        all_fields = list()
        index = 0
        for field in self.raw['fields']:
            all_fields.append(LrpcEnumField(field, index))
            index = all_fields[-1].id() + 1

        return all_fields

    def field_id(self, name: str):
        for f in self.fields():
            if f.name() == name:
                return f.id()

        return None

    def is_external(self):
        return 'external' in self.raw

    def external_file(self):
        return self.raw.get('external', None)

    def external_namespace(self):
        return self.raw.get('external_namespace', None)
