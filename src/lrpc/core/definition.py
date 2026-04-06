import hashlib
import lzma

# pylint: disable = unused-import
from collections.abc import Iterable  # noqa: TC003
from copy import deepcopy
from pathlib import Path
from typing import cast

import yaml
from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypeAliasType, TypedDict

from lrpc.visitors import LrpcVisitor

from .constant import LrpcConstant, LrpcConstantDict, LrpcConstantType
from .enum import LrpcEnum, LrpcEnumDict
from .function import LrpcFun
from .service import LrpcService, LrpcServiceDict, LrpcServiceOptionalIdDict
from .settings import RpcSettings, RpcSettingsDict
from .stream import LrpcStream
from .struct import LrpcStruct, LrpcStructDict
from .var import LrpcVarDict

LrpcUserSetting = bool | int | float | str | None
LrpcUserSettings = TypeAliasType(
    "LrpcUserSettings",
    "LrpcUserSetting | Iterable[LrpcUserSettings] | dict[str, LrpcUserSettings] | None",
)


class LrpcDefDict(TypedDict):
    name: str
    services: list[LrpcServiceOptionalIdDict]
    structs: NotRequired[list[LrpcStructDict]]
    enums: NotRequired[list[LrpcEnumDict]]
    constants: NotRequired[list[LrpcConstantDict]]
    settings: NotRequired[RpcSettingsDict]
    user_settings: NotRequired[LrpcUserSettings]


# pylint: disable=invalid-name
LrpcDefValidator = TypeAdapter(LrpcDefDict)


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

    def __init__(self, raw_: LrpcDefDict) -> None:
        raw = deepcopy(raw_)
        LrpcDefValidator.validate_python(raw, strict=True, extra="allow")
        self._definition_yaml = yaml.dump(raw, sort_keys=False)

        self._name = raw["name"]
        self._settings = RpcSettings(raw.get("settings", {}))

        struct_names = []
        if "structs" in raw:
            struct_names.extend([s["name"] for s in raw["structs"]])

        enum_names = []
        if "enums" in raw:
            enum_names.extend([e["name"] for e in raw["enums"]])

        self._init_all_vars(raw, struct_names, enum_names)
        self._init_meta_service(raw)
        self._init_service_ids(raw)
        self._init_definition_hash()

        self._services = [LrpcService(cast(LrpcServiceDict, s)) for s in raw["services"]]

        self._structs = []
        if "structs" in raw:
            self._structs.extend([LrpcStruct(s) for s in raw["structs"]])

        self._enums = []
        if "enums" in raw:
            self._enums.extend([LrpcEnum(s) for s in raw["enums"]])

        self._constants = []
        if "constants" in raw:
            self._constants.extend([LrpcConstant(c) for c in raw["constants"]])

        self._user_settings = raw.get("user_settings", None)

    def _init_all_vars(self, raw: LrpcDefDict, struct_names: list[str], enum_names: list[str]) -> None:
        for service in raw["services"]:
            for function in service.get("functions", []):
                self._init_vars(function.get("params", []), struct_names, enum_names)
                self._init_vars(function.get("returns", []), struct_names, enum_names)

            for stream in service.get("streams", []):
                self._init_vars(stream.get("params", []), struct_names, enum_names)

        for struct in raw.get("structs", []):
            self._init_vars(struct.get("fields", []), struct_names, enum_names)

    def _init_vars(self, lrpc_vars: list[LrpcVarDict], struct_names: list[str], enum_names: list[str]) -> None:
        for var in lrpc_vars:
            self._init_structs_and_enums(var, struct_names, enum_names)

    def _init_meta_service(self, raw: LrpcDefDict) -> None:
        meta_service_found = False
        for s in raw["services"]:
            if s["name"] == "LrpcMeta":
                s["id"] = self.META_SERVICE_ID
                self._meta_service = LrpcService(cast(LrpcServiceDict, s))
                raw["services"].remove(s)
                meta_service_found = True

        if not meta_service_found:
            raise ValueError("No meta service found in definition")

    @classmethod
    def _init_structs_and_enums(cls, var: LrpcVarDict, struct_names: list[str], enum_names: list[str]) -> None:
        if var["type"].strip("@") in struct_names:
            var["type"] = "struct" + var["type"]

        if var["type"].strip("@") in enum_names:
            var["type"] = "enum" + var["type"]

    @staticmethod
    def _init_service_ids(raw: LrpcDefDict) -> None:
        last_service_id = -1

        for s in raw["services"]:
            if "id" in s:
                last_service_id = s["id"]
            else:
                last_service_id = last_service_id + 1
                s["id"] = last_service_id

    def _init_definition_hash(self) -> None:
        definition_hash = hashlib.sha3_256(self._definition_yaml.encode(encoding="utf-8")).hexdigest()
        definition_hash_length = self._settings.definition_hash_length()
        definition_hash_length = min(definition_hash_length, len(definition_hash))
        self._definition_hash = None if definition_hash_length == 0 else definition_hash[:definition_hash_length]

    def accept(self, visitor: LrpcVisitor, *, visit_meta_service: bool = True) -> None:
        visitor.visit_lrpc_def(self)

        visitor.visit_rpc_settings(self._settings)

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
            self._meta_service.accept(visitor)

        visitor.visit_lrpc_user_settings(self.user_settings())

        visitor.visit_lrpc_def_end()

    def name(self) -> str:
        return self._name

    def settings(self) -> RpcSettings:
        return self._settings

    def definition_hash(self) -> str | None:
        return self._definition_hash

    def compressed_definition(self) -> bytes:
        return lzma.compress(self._definition_yaml.encode(encoding="utf-8"))

    def services(self) -> list[LrpcService]:
        return self._services

    def service_by_name(self, name: str) -> LrpcService | None:
        if name == "LrpcMeta":
            return self._meta_service

        for s in self.services():
            if s.name() == name:
                return s

        return None

    def service_by_id(self, identifier: int) -> LrpcService | None:
        if identifier == self.META_SERVICE_ID:
            return self._meta_service

        for s in self.services():
            if s.id() == identifier:
                return s

        return None

    def meta_service(self) -> LrpcService:
        return self._meta_service

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
        return self._structs

    def struct(self, name: str) -> LrpcStruct:
        for s in self.structs():
            if s.name() == name:
                return s

        raise ValueError(f"No struct {name} in LRPC definition {self.name()}")

    def enums(self) -> list[LrpcEnum]:
        return self._enums

    def enum(self, name: str) -> LrpcEnum:
        for s in self.enums():
            if s.name() == name:
                return s

        raise ValueError(f"No enum {name} in LRPC definition {self.name()}")

    def constants(self) -> list[LrpcConstant]:
        return self._constants

    def constant(self, name: str) -> LrpcConstantType:
        for c in self.constants():
            if c.name() == name:
                return c.value()

        raise ValueError(f"No constant {name} in LRPC definition {self.name()}")

    def user_settings(self) -> LrpcUserSettings:
        return self._user_settings
