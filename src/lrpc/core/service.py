from typing import Optional, TypedDict
from typing_extensions import NotRequired

from ..visitors import LrpcVisitor
from .function import LrpcFun, LrpcFunDict
from .stream import LrpcStream, LrpcStreamDict


class LrpcServiceDict(TypedDict):
    name: str
    id: int
    functions: NotRequired[list[LrpcFunDict]]
    streams: NotRequired[list[LrpcStreamDict]]


class LrpcService:
    def __init__(self, raw: LrpcServiceDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "id" in raw and isinstance(raw["id"], int)

        functions = raw.get("functions", [])
        streams = raw.get("streams", [])

        assert (len(functions) != 0) or (len(streams) != 0)

        if "functions" in raw:
            assert isinstance(raw["functions"], list)

        if "streams" in raw:
            assert isinstance(raw["streams"], list)

        self.__init_functions_ids(functions)

        self.__name = raw["name"]
        self.__id = raw["id"]
        self.__functions = [LrpcFun(f) for f in functions]
        self.__streams = [LrpcStream(s) for s in streams]

    @staticmethod
    def __init_functions_ids(functions: list[LrpcFunDict]) -> None:
        last_function_id = -1

        for f in functions:
            if "id" in f:
                last_function_id = f["id"]
            else:
                # id field must be present in LrpcFunDict to construct LrpcFun
                # but it is optional when constructing LrpcService. This method
                # makes sure that function IDs are initialized properly
                last_function_id = last_function_id + 1  # type: ignore[unreachable]
                f["id"] = last_function_id

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_service(self)
        for f in self.functions():
            f.accept(visitor)
        for s in self.streams():
            s.accept(visitor)
        visitor.visit_lrpc_service_end()

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def functions(self) -> list[LrpcFun]:
        return self.__functions

    def function_by_name(self, name: str) -> Optional[LrpcFun]:
        for f in self.functions():
            if f.name() == name:
                return f

        return None

    def function_by_id(self, function_id: int) -> Optional[LrpcFun]:
        for f in self.functions():
            if f.id() == function_id:
                return f

        return None

    def streams(self) -> list[LrpcStream]:
        return self.__streams
