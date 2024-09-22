from typing import List, TypedDict

from lrpc import LrpcVisitor
from lrpc.core import LrpcFun, LrpcFunDict


class LrpcServiceDict(TypedDict):
    name: str
    id: int
    functions: List[LrpcFunDict]


class LrpcService:
    def __init__(self, raw: LrpcServiceDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "id" in raw and isinstance(raw["id"], int)
        assert "functions" in raw and isinstance(raw["functions"], List)

        self.__init_functions_ids(raw["functions"])

        self.__name = raw["name"]
        self.__id = raw["id"]
        self.__functions = [LrpcFun(f) for f in raw["functions"]]

    def __init_functions_ids(self, functions: List[LrpcFunDict]) -> None:
        last_function_id = -1

        for f in functions:
            if "id" in f:
                last_function_id = f["id"]
            else:
                last_function_id = last_function_id + 1
                f["id"] = last_function_id

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_service(self)
        for f in self.functions():
            f.accept(visitor)
        visitor.visit_lrpc_service_end()

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def functions(self) -> List[LrpcFun]:
        return self.__functions

    def function_by_name(self, name: str) -> LrpcFun | None:
        for f in self.functions():
            if f.name() == name:
                return f

        return None

    def function_by_id(self, function_id: int) -> LrpcFun | None:
        for f in self.functions():
            if f.id() == function_id:
                return f

        return None
