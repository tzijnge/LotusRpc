from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict

from lrpc.visitors import LrpcVisitor

from .var import LrpcVar, LrpcVarDict


class LrpcStructDict(TypedDict):
    name: str
    fields: list[LrpcVarDict]
    external: NotRequired[str]
    external_namespace: NotRequired[str]


# pylint: disable=invalid-name
LrpcStructValidator = TypeAdapter(LrpcStructDict)


class LrpcStruct:
    def __init__(self, raw: LrpcStructDict) -> None:
        LrpcStructValidator.validate_python(raw, strict=True, extra="forbid")

        self._name = raw["name"]
        self._fields = [LrpcVar(f) for f in raw["fields"]]
        self._external = raw.get("external", None)
        self._external_namespace = raw.get("external_namespace", None)

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_struct(self)

        for f in self.fields():
            visitor.visit_lrpc_struct_field(self, f)

        visitor.visit_lrpc_struct_end()

    def name(self) -> str:
        return self._name

    def fields(self) -> list[LrpcVar]:
        return self._fields

    def is_external(self) -> bool:
        return self._external is not None

    def external_file(self) -> str | None:
        return self._external

    def external_namespace(self) -> str | None:
        return self._external_namespace
