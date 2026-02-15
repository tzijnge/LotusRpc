from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict

from lrpc.visitors import LrpcVisitor

from .var import LrpcVar, LrpcVarDict


class LrpcFunDict(TypedDict):
    name: str
    id: int
    params: NotRequired[list[LrpcVarDict]]
    returns: NotRequired[list[LrpcVarDict]]


class LrpcFunOptionalIdDict(TypedDict):
    name: str
    id: NotRequired[int]
    params: NotRequired[list[LrpcVarDict]]
    returns: NotRequired[list[LrpcVarDict]]


# pylint: disable=invalid-name
LrpcFunValidator = TypeAdapter(LrpcFunDict)


class LrpcFun:
    def __init__(self, raw: LrpcFunDict) -> None:
        LrpcFunValidator.validate_python(raw, strict=True, extra="forbid")

        self._params = []
        self._returns = []

        if "params" in raw:
            self._params.extend([LrpcVar(p) for p in raw["params"]])

        if "returns" in raw:
            self._returns.extend([LrpcVar(p) for p in raw["returns"]])

        self._name = raw["name"]
        self._id = raw["id"]

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
        return self._params

    def param(self, name: str) -> LrpcVar:
        for p in self.params():
            if p.name() == name:
                return p

        raise ValueError(f"No parameter {name} in function {self.name()}")

    def returns(self) -> list[LrpcVar]:
        return self._returns

    def ret(self, name: str) -> LrpcVar:
        for r in self.returns():
            if r.name() == name:
                return r

        raise ValueError(f"No return value {name} in function {self.name()}")

    def name(self) -> str:
        return self._name

    def id(self) -> int:
        return self._id

    def number_returns(self) -> int:
        return len(self.returns())

    def param_names(self) -> list[str]:
        return [p.name() for p in self.params()]
