import hashlib
import lzma
from pathlib import Path
from typing import cast

import yaml
from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict

from lrpc.visitors import LrpcVisitor

from .constant import LrpcConstant, LrpcConstantDict
from .enum import LrpcEnum, LrpcEnumDict
from .function import LrpcFun
from .service import LrpcService, LrpcServiceDict, LrpcServiceOptionalIdDict
from .stream import LrpcStream
from .struct import LrpcStruct, LrpcStructDict
from .var import LrpcVarDict


class LrpcDefDict(TypedDict):
    name: str
    version: NotRequired[str]
    definition_hash_length: NotRequired[int]
    embed_definition: NotRequired[bool]
    services: list[LrpcServiceOptionalIdDict]
    namespace: NotRequired[str]
    rx_buffer_size: NotRequired[int]
    tx_buffer_size: NotRequired[int]
    structs: NotRequired[list[LrpcStructDict]]
    enums: NotRequired[list[LrpcEnumDict]]
    constants: NotRequired[list[LrpcConstantDict]]


# pylint: disable=invalid-name
LrpcDefValidator = TypeAdapter(LrpcDefDict)


# pylint: disable = too-many-instance-attributes
# pylint: disable = too-many-public-methods
class LrpcDef:
    META_SERVICE_ID = 255

    @staticmethod
    def _decompressed(compressed: bytes) -> str:
        return lzma.decompress(compressed).decode("utf-8")

    @staticmethod
    def decompress(compressed: bytes) -> "LrpcDef":
        definition_yaml = LrpcDef._decompressed(compressed)
        return LrpcDef(yaml.safe_load(definition_yaml))

    @staticmethod
    def save_to(compressed: bytes, destination: Path) -> None:
        with destination.open("wt+") as dest:
            dest.write(LrpcDef._decompressed(compressed))

    def __init__(self, raw: LrpcDefDict) -> None:
        LrpcDefValidator.validate_python(raw, strict=True, extra="allow")
        self._definition_yaml = yaml.dump(raw, sort_keys=False)

        struct_names = []
        if "structs" in raw:
            struct_names.extend([s["name"] for s in raw["structs"]])

        enum_names = []
        if "enums" in raw:
            enum_names.extend([e["name"] for e in raw["enums"]])

        self.__init_all_vars(raw, struct_names, enum_names)
        self.__init_meta_service(raw)
        self.__init_service_ids(raw)
        self.__init_definition_hash(raw)

        self.__name = raw["name"]
        self.__version = raw.get("version", None)
        self.__embed_definition = raw.get("embed_definition", False)

        self.__services = [LrpcService(cast(LrpcServiceDict, s)) for s in raw["services"]]
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

    def __init_all_vars(self, raw: LrpcDefDict, struct_names: list[str], enum_names: list[str]) -> None:
        for service in raw["services"]:
            for function in service.get("functions", []):
                self.__init_vars(function.get("params", []), struct_names, enum_names)
                self.__init_vars(function.get("returns", []), struct_names, enum_names)

            for stream in service.get("streams", []):
                self.__init_vars(stream.get("params", []), struct_names, enum_names)

        for struct in raw.get("structs", []):
            self.__init_vars(struct.get("fields", []), struct_names, enum_names)

    def __init_vars(self, lrpc_vars: list[LrpcVarDict], struct_names: list[str], enum_names: list[str]) -> None:
        for var in lrpc_vars:
            self.__init_structs_and_enums(var, struct_names, enum_names)

    def __init_meta_service(self, raw: LrpcDefDict) -> None:
        meta_service_found = False
        for s in raw["services"]:
            if s["name"] == "LrpcMeta":
                s["id"] = self.META_SERVICE_ID
                self.__meta_service = LrpcService(cast(LrpcServiceDict, s))
                raw["services"].remove(s)
                meta_service_found = True

        if not meta_service_found:
            raise ValueError("No meta service found in definition")

    @classmethod
    def __init_structs_and_enums(cls, var: LrpcVarDict, struct_names: list[str], enum_names: list[str]) -> None:
        if var["type"].strip("@") in struct_names:
            var["type"] = "struct" + var["type"]

        if var["type"].strip("@") in enum_names:
            var["type"] = "enum" + var["type"]

    @staticmethod
    def __init_service_ids(raw: LrpcDefDict) -> None:
        last_service_id = -1

        for s in raw["services"]:
            if "id" in s:
                last_service_id = s["id"]
            else:
                last_service_id = last_service_id + 1
                s["id"] = last_service_id

    def __init_definition_hash(self, raw: LrpcDefDict) -> None:
        definition_hash = hashlib.sha3_256(self._definition_yaml.encode(encoding="utf-8")).hexdigest()
        definition_hash_length = raw.get("definition_hash_length", len(definition_hash))
        self.__definition_hash = None if definition_hash_length == 0 else definition_hash[:definition_hash_length]

    def accept(self, visitor: LrpcVisitor, *, visit_meta_service: bool = True) -> None:
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

        if visit_meta_service:
            self.__meta_service.accept(visitor)

        visitor.visit_lrpc_def_end()

    def name(self) -> str:
        return self.__name

    def version(self) -> str | None:
        return self.__version

    def definition_hash(self) -> str | None:
        return self.__definition_hash

    def embed_definition(self) -> bool:
        return self.__embed_definition

    def compressed_definition(self) -> bytes:
        return lzma.compress(self._definition_yaml.encode(encoding="utf-8"))

    def namespace(self) -> str | None:
        return self.__namespace

    def rx_buffer_size(self) -> int:
        return self.__rx_buffer_size

    def tx_buffer_size(self) -> int:
        return self.__tx_buffer_size

    def services(self) -> list[LrpcService]:
        return self.__services

    def service_by_name(self, name: str) -> LrpcService | None:
        if name == "LrpcMeta":
            return self.__meta_service

        for s in self.services():
            if s.name() == name:
                return s

        return None

    def service_by_id(self, identifier: int) -> LrpcService | None:
        if identifier == self.META_SERVICE_ID:
            return self.__meta_service

        for s in self.services():
            if s.id() == identifier:
                return s

        return None

    def meta_service(self) -> LrpcService:
        return self.__meta_service

    def max_service_id(self) -> int:
        service_ids = [s.id() for s in self.services()]
        return max(service_ids)

    def function(self, service_name: str, function_name: str) -> LrpcFun | None:
        service = self.service_by_name(service_name)
        if service is None:
            return None

        return service.function_by_name(function_name)

    def stream(self, service_name: str, stream_name: str) -> LrpcStream | None:
        service = self.service_by_name(service_name)
        if service is None:
            return None

        return service.stream_by_name(stream_name)

    def structs(self) -> list[LrpcStruct]:
        return self.__structs

    def struct(self, name: str) -> LrpcStruct:
        for s in self.structs():
            if s.name() == name:
                return s

        raise ValueError(f"No struct {name} in LRPC definition {self.name()}")

    def enums(self) -> list[LrpcEnum]:
        return self.__enums

    def enum(self, name: str) -> LrpcEnum:
        for s in self.enums():
            if s.name() == name:
                return s

        raise ValueError(f"No enum {name} in LRPC definition {self.name()}")

    def constants(self) -> list[LrpcConstant]:
        return self.__constants
