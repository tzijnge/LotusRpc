from typing import List, TypedDict, NotRequired

from lrpc import LrpcVisitor


class LrpcEnumFieldDict(TypedDict):
    name: str
    id: int


class LrpcEnumField:
    def __init__(self, raw: LrpcEnumFieldDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "id" in raw and isinstance(raw["id"], int)

        self.__name = raw["name"]
        self.__id = raw["id"]

    @classmethod
    def from_name_and_index(cls, name: str, index: int) -> "LrpcEnumField":
        return cls({"name": name, "id": index})

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id


class LrpcEnumDict(TypedDict):
    name: str
    fields: List[LrpcEnumFieldDict | str]
    external: NotRequired[str]
    external_namespace: NotRequired[str]


class LrpcEnum:

    def __init__(self, raw: LrpcEnumDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "fields" in raw and isinstance(raw["fields"], List)

        self.__name = raw["name"]
        self.__fields = raw["fields"]
        self.__external = raw.get("external", None)
        self.__external_namespace = raw.get("external_namespace", None)

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_enum(self)

        for f in self.fields():
            visitor.visit_lrpc_enum_field(self, f)

        visitor.visit_lrpc_enum_end(self)

    def name(self) -> str:
        return self.__name

    def fields(self) -> List[LrpcEnumField]:
        all_fields = []
        index = 0
        for field in self.__fields:
            if isinstance(field, str):
                all_fields.append(LrpcEnumField.from_name_and_index(field, index))
            elif "id" not in field:
                all_fields.append(LrpcEnumField.from_name_and_index(field["name"], index))
            else:
                all_fields.append(LrpcEnumField(field))

            index = all_fields[-1].id() + 1

        return all_fields

    def field_id(self, name: str) -> int | None:
        for f in self.fields():
            if f.name() == name:
                return f.id()

        return None

    def is_external(self) -> bool:
        return self.__external is not None

    def external_file(self) -> str | None:
        return self.__external

    def external_namespace(self) -> str | None:
        return self.__external_namespace
