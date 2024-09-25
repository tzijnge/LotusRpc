from typing import Optional, TypedDict
from typing_extensions import NotRequired

import jsonschema
import yaml
from lrpc import LrpcVisitor
from lrpc.schema import load_lrpc_schema
from lrpc.core import LrpcConstant, LrpcEnum, LrpcService, LrpcStruct, LrpcVarDict
from lrpc.core import LrpcStructDict, LrpcServiceDict, LrpcConstantDict, LrpcEnumDict


class LrpcDefDict(TypedDict):
    name: str
    services: list[LrpcServiceDict]
    namespace: NotRequired[str]
    rx_buffer_size: NotRequired[int]
    tx_buffer_size: NotRequired[int]
    structs: NotRequired[list[LrpcStructDict]]
    enums: NotRequired[list[LrpcEnumDict]]
    constants: NotRequired[list[LrpcConstantDict]]


class LrpcDef:

    def __init__(self, raw: LrpcDefDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "services" in raw and isinstance(raw["services"], list)

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

    def __init_base_types(self, raw: LrpcDefDict, struct_names: list[str], enum_names: list[str]) -> None:
        for service in raw["services"]:
            for function in service["functions"]:
                for p in function.get("params", []):
                    self.__update_type(p, struct_names, enum_names)
                for r in function.get("returns", []):
                    self.__update_type(r, struct_names, enum_names)

        for struct in raw.get("structs", []):
            for field in struct["fields"]:
                self.__update_type(field, struct_names, enum_names)

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

    def services(self) -> list[LrpcService]:
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

    def structs(self) -> list[LrpcStruct]:
        return self.__structs

    def struct(self, name: str) -> Optional[LrpcStruct]:
        for s in self.structs():
            if s.name() == name:
                return s

        return None

    def enums(self) -> list[LrpcEnum]:
        return self.__enums

    def enum(self, name: str) -> Optional[LrpcEnum]:
        for s in self.enums():
            if s.name() == name:
                return s

        return None

    def constants(self) -> list[LrpcConstant]:
        return self.__constants

    @classmethod
    def __update_type(cls, var: LrpcVarDict, struct_names: list[str], enum_names: list[str]) -> None:
        if var["type"].strip("@") in struct_names:
            var["type"] = "struct" + var["type"]

        if var["type"].strip("@") in enum_names:
            var["type"] = "enum" + var["type"]

    @staticmethod
    def load(definition_url: str) -> "LrpcDef":
        from lrpc.validation import SemanticAnalyzer

        with open(definition_url, mode="rt", encoding="utf-8") as rpc_def:
            definition = yaml.safe_load(rpc_def)
            jsonschema.validate(definition, load_lrpc_schema())

            lrpc_def = LrpcDef(definition)
            sa = SemanticAnalyzer(lrpc_def)
            sa.analyze()

            assert len(sa.errors) == 0
            assert len(sa.warnings) == 0

            return lrpc_def
