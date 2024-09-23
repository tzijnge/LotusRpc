from importlib import resources
from typing import List, Optional, TypedDict
from typing_extensions import NotRequired

import jsonschema
import yaml
from lrpc import LrpcVisitor
from lrpc import schema as lrpc_schema
from lrpc.core import LrpcConstant, LrpcEnum, LrpcService, LrpcStruct, LrpcVarDict
from lrpc.core import LrpcStructDict, LrpcServiceDict, LrpcConstantDict, LrpcEnumDict


class LrpcDefDict(TypedDict):
    name: str
    services: List[LrpcServiceDict]
    namespace: NotRequired[str]
    rx_buffer_size: NotRequired[int]
    tx_buffer_size: NotRequired[int]
    structs: NotRequired[List[LrpcStructDict]]
    enums: NotRequired[List[LrpcEnumDict]]
    constants: NotRequired[List[LrpcConstantDict]]


class LrpcDef:

    def __init__(self, raw: LrpcDefDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "services" in raw and isinstance(raw["services"], List)

        struct_names = []
        if "structs" in raw:
            struct_names.extend([s["name"] for s in raw["structs"]])

        enum_names = []
        if "enums" in raw:
            enum_names.extend([e["name"] for e in raw["enums"]])

        self.__init_base_types(raw, struct_names, enum_names)
        self.__init_service_ids(raw)

        self.__name = raw["name"]
        self.__services = [LrpcService(s) for s in raw["services"]]
        self.__namespace = raw.get("namespace", None)
        self.__rx_buffer_size = raw.get("rx_buffer_size", 256)
        self.__tx_buffer_size = raw.get("tx_buffer_size", 256)

        self.__structs = []
        if "structs" in raw:
            self.__structs.extend([LrpcStruct(s) for s in raw["structs"]])

        self.__enums = []
        if "enums" in raw:
            self.__enums.extend([LrpcEnum(s) for s in raw["enums"]])

        self.__constants = []
        if "constants" in raw:
            self.__constants.extend([LrpcConstant(c) for c in raw["constants"]])

    def __init_base_types(self, raw: LrpcDefDict, struct_names: List[str], enum_names: List[str]) -> None:
        for service in raw["services"]:
            for function in service["functions"]:
                for p in function.get("params", []):
                    p["base_type_is_struct"] = self.__base_type_is_struct(p, struct_names)
                    p["base_type_is_enum"] = self.__base_type_is_enum(p, enum_names)
                for r in function.get("returns", []):
                    r["base_type_is_struct"] = self.__base_type_is_struct(r, struct_names)
                    r["base_type_is_enum"] = self.__base_type_is_enum(r, enum_names)

        for struct in raw.get("structs", []):
            for field in struct["fields"]:
                field["base_type_is_struct"] = self.__base_type_is_struct(field, struct_names)
                field["base_type_is_enum"] = self.__base_type_is_enum(field, enum_names)

    def __init_service_ids(self, raw: LrpcDefDict) -> None:
        last_service_id = -1

        for s in raw["services"]:
            if "id" in s:
                last_service_id = s["id"]
            else:
                last_service_id = last_service_id + 1
                s["id"] = last_service_id

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_def(self)

        if len(self.constants()) != 0:
            visitor.visit_lrpc_constants()
            for c in self.constants():
                c.accept(visitor)
            visitor.visit_lrpc_constants_end()

        for e in self.enums():
            e.accept(visitor)

        for struct in self.structs():
            struct.accept(visitor)

        for service in self.services():
            service.accept(visitor)

        visitor.visit_lrpc_def_end()

    def name(self) -> str:
        return self.__name

    def namespace(self) -> Optional[str]:
        return self.__namespace

    def rx_buffer_size(self) -> int:
        return self.__rx_buffer_size

    def tx_buffer_size(self) -> int:
        return self.__tx_buffer_size

    def services(self) -> List[LrpcService]:
        return self.__services

    def service_by_name(self, name: str) -> Optional[LrpcService]:
        for s in self.services():
            if s.name() == name:
                return s

        return None

    def service_by_id(self, identifier: int) -> Optional[LrpcService]:
        for s in self.services():
            if s.id() == identifier:
                return s

        return None

    def max_service_id(self) -> int:
        service_ids = [s.id() for s in self.services()]
        return max(service_ids)

    def structs(self) -> List[LrpcStruct]:
        return self.__structs

    def struct(self, name: str) -> Optional[LrpcStruct]:
        for s in self.structs():
            if s.name() == name:
                return s

        return None

    def enums(self) -> List[LrpcEnum]:
        return self.__enums

    def enum(self, name: str) -> Optional[LrpcEnum]:
        for s in self.enums():
            if s.name() == name:
                return s

        return None

    def constants(self) -> List[LrpcConstant]:
        return self.__constants

    def __struct_names(self) -> List[str]:
        return [s.name() for s in self.structs()]

    def __enum_names(self) -> List[str]:
        return [e.name() for e in self.enums()]

    @classmethod
    def __base_type_is_struct(cls, var: LrpcVarDict, struct_names: List[str]) -> bool:
        return var["type"].strip("@") in struct_names

    @classmethod
    def __base_type_is_enum(cls, var: LrpcVarDict, enum_names: List[str]) -> bool:
        return var["type"].strip("@") in enum_names

    @staticmethod
    def load(definition_url: str) -> "LrpcDef":
        from lrpc.validation import SemanticAnalyzer

        schema_url = resources.files(lrpc_schema).joinpath("lotusrpc-schema.json")

        with open(definition_url, mode="rt", encoding="utf-8") as rpc_def:
            definition = yaml.safe_load(rpc_def)
            schema = yaml.safe_load(schema_url.read_text())
            jsonschema.validate(definition, schema)

            lrpc_def = LrpcDef(definition)
            sa = SemanticAnalyzer(lrpc_def)
            sa.analyze()

            assert len(sa.errors) == 0
            assert len(sa.warnings) == 0

            return lrpc_def
