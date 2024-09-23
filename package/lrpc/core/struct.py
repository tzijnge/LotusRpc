from typing import List, TypedDict
from typing_extensions import NotRequired

from lrpc import LrpcVisitor
from lrpc.core import LrpcVar, LrpcVarDict


class LrpcStructDict(TypedDict):
    name: str
    fields: List[LrpcVarDict]
    external: NotRequired[str]
    external_namespace: NotRequired[str]


class LrpcStruct:
    def __init__(self, raw: LrpcStructDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "fields" in raw and isinstance(raw["fields"], List)

        self.__name = raw["name"]
        self.__fields = [LrpcVar(f) for f in raw["fields"]]
        self.__external = raw.get("external", None)
        self.__external_namespace = raw.get("external_namespace", None)

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_struct(self)

        for f in self.fields():
            visitor.visit_lrpc_struct_field(f)

        visitor.visit_lrpc_struct_end()

    def name(self) -> str:
        return self.__name

    def fields(self) -> List[LrpcVar]:
        return self.__fields

    def is_external(self) -> bool:
        return self.__external is not None

    def external_file(self) -> str | None:
        return self.__external

    def external_namespace(self) -> str | None:
        return self.__external_namespace
