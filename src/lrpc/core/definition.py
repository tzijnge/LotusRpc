from typing import Optional, TypedDict
from typing_extensions import NotRequired

from .constant import LrpcConstant, LrpcConstantDict
from .enum import LrpcEnum, LrpcEnumDict
from .function import LrpcFun
from .stream import LrpcStream
from .service import LrpcService, LrpcServiceDict
from .struct import LrpcStruct, LrpcStructDict
from .var import LrpcVarDict
from ..visitors import LrpcVisitor


class LrpcDefDict(TypedDict):
    name: str
    version: NotRequired[str]
    services: list[LrpcServiceDict]
    namespace: NotRequired[str]
    rx_buffer_size: NotRequired[int]
    tx_buffer_size: NotRequired[int]
    structs: NotRequired[list[LrpcStructDict]]
    enums: NotRequired[list[LrpcEnumDict]]
    constants: NotRequired[list[LrpcConstantDict]]


# pylint: disable = too-many-instance-attributes
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

        self.__init_all_vars(raw, struct_names, enum_names)
        self.__init_service_ids(raw)

        self.__name = raw["name"]
        self.__version = raw.get("version", None)
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
                # id field must be present in LrpcServiceDict to construct LrpcService
                # but it is optional when constructing LrpcDef. This method
                # makes sure that service IDs are initialized properly
                last_service_id = last_service_id + 1  # type: ignore[unreachable]
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

    def version(self) -> Optional[str]:
        return self.__version

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

    def function(self, service_name: str, function_name: str) -> Optional[LrpcFun]:
        service = self.service_by_name(service_name)
        if service is None:
            return None

        return service.function_by_name(function_name)

    def stream(self, service_name: str, stream_name: str) -> Optional[LrpcStream]:
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
