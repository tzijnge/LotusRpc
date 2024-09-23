from typing import List, Optional, TypedDict
from typing_extensions import NotRequired

from lrpc import LrpcVisitor
from lrpc.core import LrpcVar, LrpcVarDict


class LrpcFunDict(TypedDict):
    name: str
    id: int
    params: NotRequired[List[LrpcVarDict]]
    returns: NotRequired[List[LrpcVarDict]]


class LrpcFun:

    def __init__(self, raw: LrpcFunDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "id" in raw and isinstance(raw["id"], int)

        self.__params = []
        self.__returns = []

        if "params" in raw:
            self.__params.extend([LrpcVar(p) for p in raw["params"]])

        if "returns" in raw:
            self.__returns.extend([LrpcVar(p) for p in raw["returns"]])

        self.__name = raw["name"]
        self.__id = raw["id"]

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_function(self)

        for r in self.returns():
            visitor.visit_lrpc_function_return(r)
        visitor.visit_lrpc_function_return_end()

        for p in self.params():
            visitor.visit_lrpc_function_param(p)
        visitor.visit_lrpc_function_param_end()

        visitor.visit_lrpc_function_end()

    def params(self) -> List[LrpcVar]:
        return self.__params

    def param(self, name: str) -> Optional[LrpcVar]:
        for p in self.params():
            if p.name() == name:
                return p

        return None

    def returns(self) -> List[LrpcVar]:
        return self.__returns

    def ret(self, name: str) -> Optional[LrpcVar]:
        for r in self.returns():
            if r.name() == name:
                return r

        return None

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def number_returns(self) -> int:
        return len(self.returns())

    def param_names(self) -> List[str]:
        return [p.name() for p in self.params()]
