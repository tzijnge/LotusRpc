from typing import TypedDict
from typing_extensions import NotRequired

from ..visitors import LrpcVisitor
from .var import LrpcVar, LrpcVarDict


class LrpcFunDict(TypedDict):
    name: str
    id: int
    params: NotRequired[list[LrpcVarDict]]
    returns: NotRequired[list[LrpcVarDict]]


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

    def params(self) -> list[LrpcVar]:
        return self.__params

    def param(self, name: str) -> LrpcVar:
        for p in self.params():
            if p.name() == name:
                return p

        raise ValueError(f"No parameter {name} in function {self.name()}")

    def returns(self) -> list[LrpcVar]:
        return self.__returns

    def ret(self, name: str) -> LrpcVar:
        for r in self.returns():
            if r.name() == name:
                return r

        raise ValueError(f"No return value {name} in function {self.name()}")

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def number_returns(self) -> int:
        return len(self.returns())

    def param_names(self) -> list[str]:
        return [p.name() for p in self.params()]
