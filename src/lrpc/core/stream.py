from enum import Enum
from typing import TypedDict

from typing_extensions import NotRequired

from ..visitors import LrpcVisitor
from .var import LrpcVar, LrpcVarDict


class LrpcStreamDict(TypedDict):
    name: str
    id: int
    origin: str
    finite: NotRequired[bool]
    params: NotRequired[list[LrpcVarDict]]


class LrpcStream:
    class Origin(str, Enum):
        CLIENT = "client"
        SERVER = "server"

    def __init__(self, raw: LrpcStreamDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "id" in raw and isinstance(raw["id"], int)
        assert "origin" in raw and isinstance(raw["origin"], str)

        self.__name = raw["name"]
        self.__id = raw["id"]
        self.__origin = LrpcStream.Origin(raw["origin"])
        self.__is_finite = raw.get("finite", False)
        self.__params = []
        self.__returns = []

        params = []
        if "params" in raw:
            params.extend([LrpcVar(p) for p in raw["params"]])

        if self.is_finite():
            params.append(LrpcVar({"name": "final", "type": "bool"}))

        if self.origin() == LrpcStream.Origin.CLIENT:
            self.__params = params
        else:
            self.__params.append(LrpcVar({"name": "start", "type": "bool"}))
            self.__returns = params

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_stream(self)

        for p in self.params():
            visitor.visit_lrpc_stream_param(p)
        visitor.visit_lrpc_stream_param_end()

        for r in self.returns():
            visitor.visit_lrpc_stream_return(r)
        visitor.visit_lrpc_stream_return_end()

        visitor.visit_lrpc_stream_end()

    def params(self) -> list[LrpcVar]:
        return self.__params

    def returns(self) -> list[LrpcVar]:
        return self.__returns

    def param(self, name: str) -> LrpcVar:
        for p in self.params():
            if p.name() == name:
                return p

        raise ValueError(f"No parameter {name} in function {self.name()}")

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def origin(self) -> Origin:
        return self.__origin

    def number_params(self) -> int:
        return len(self.params())

    def number_returns(self) -> int:
        return len(self.returns())

    def param_names(self) -> list[str]:
        return [p.name() for p in self.params()]

    def is_finite(self) -> bool:
        return self.__is_finite
