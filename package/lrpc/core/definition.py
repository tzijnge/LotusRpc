from typing import Optional

from lrpc import LrpcVisitor
from lrpc.core import LrpcConstant, LrpcEnum, LrpcService, LrpcStruct
from lrpc import schema as lrpc_schema
import jsonschema
from importlib import resources
import yaml

class LrpcDef(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        self.__init_structs()
        self.__init_enums()
        self.__init_buffer_sizes()
        self.__init_namespace()
        self.__init_service_ids()
        self.__init_base_types()
        self.__init_constants()

    def __init_base_types(self):
        for s in self.raw['services']:
            for f in s['functions']:
                for p in f.get('params', list()):
                    p['base_type_is_struct'] = self.__base_type_is_struct(p)
                    p['base_type_is_enum'] = self.__base_type_is_enum(p)
                for r in f.get('returns', list()):
                    r['base_type_is_struct'] = self.__base_type_is_struct(r)
                    r['base_type_is_enum'] = self.__base_type_is_enum(r)

        for s in self.raw['structs']:
            for f in s['fields']:
                f['base_type_is_struct'] = self.__base_type_is_struct(f)
                f['base_type_is_enum'] = self.__base_type_is_enum(f)

    def __init_service_ids(self):
        last_service_id = -1

        for s in self.raw['services']:
            if 'id' in s:
                last_service_id = s['id']
            else:
                last_service_id = last_service_id + 1
                s['id'] = last_service_id

    def __init_namespace(self):
        if 'namespace' not in self.raw:
            self.raw['namespace'] = None

    def __init_buffer_sizes(self):
        if 'tx_buffer_size' not in self.raw:
            self.raw['tx_buffer_size'] = 256
        if 'rx_buffer_size' not in self.raw:
            self.raw['rx_buffer_size'] = 256

    def __init_structs(self):
        if 'structs' not in self.raw:
            self.raw['structs'] = list()

    def __init_enums(self):
        if 'enums' not in self.raw:
            self.raw['enums'] = list()

    def __init_constants(self):
        if 'constants' not in self.raw:
            self.raw['constants'] = list()

    def accept(self, visitor: LrpcVisitor):
        visitor.visit_lrpc_def(self)

        if len(self.constants()) != 0:
            visitor.visit_lrpc_constants()
            for c in self.constants():
                c.accept(visitor)
            visitor.visit_lrpc_constants_end()

        for e in self.enums():
            e.accept(visitor)

        for s in self.structs():
            s.accept(visitor)

        for s in self.services():
            s.accept(visitor)

        visitor.visit_lrpc_def_end()

    def name(self):
        return self.raw['name']

    def namespace(self):
        return self.raw['namespace']

    def rx_buffer_size(self):
        return self.raw['rx_buffer_size']

    def tx_buffer_size(self):
        return self.raw['tx_buffer_size']

    def services(self):
        return [LrpcService(s) for s in self.raw['services']]

    def service_by_name(self, name: str) -> Optional[LrpcService]:
        for s in self.services():
            if s.name() == name:
                return s

        return None

    def service_by_id(self, id: int) -> Optional[LrpcService]:
        for s in self.services():
            if s.id() == id:
                return s

        return None

    def max_service_id(self):
        service_ids = [s.id() for s in self.services()]
        return max(service_ids)

    def structs(self):
        return [LrpcStruct(s) for s in self.raw['structs']]

    def struct(self, name: str) -> Optional[LrpcStruct]:
        for s in self.structs():
            if s.name() == name:
                return s

        return None

    def enums(self):
        return [LrpcEnum(s) for s in self.raw['enums']]

    def enum(self, name: str) -> Optional[LrpcEnum]:
        for s in self.enums():
            if s.name() == name:
                return s

        return None

    def constants(self):
        return [LrpcConstant(c) for c in self.raw['constants']]

    def __struct_names(self):
        return [s['name'] for s in self.raw['structs']]

    def __enum_names(self):
        return [e['name'] for e in self.raw['enums']]

    def __base_type_is_struct(self, var):
        return var['type'].strip('@') in self.__struct_names()

    def __base_type_is_enum(self, var):
        return var['type'].strip('@') in self.__enum_names()
    
    def load(definition_url: str) -> 'LrpcDef':
        from lrpc.validation import SemanticAnalyzer

        schema_url = resources.files(lrpc_schema).joinpath('lotusrpc-schema.json')

        with open(definition_url, 'rt') as rpc_def:
            definition = yaml.safe_load(rpc_def)
            schema = yaml.safe_load(schema_url.read_text())
            jsonschema.validate(definition, schema)

            lrpc_def = LrpcDef(definition)
            sa = SemanticAnalyzer(lrpc_def)
            sa.analyze()

            assert len(sa.errors) == 0
            assert len(sa.warnings) == 0

            return lrpc_def

