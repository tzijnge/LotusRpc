from enum import Enum
from typing import TypedDict

from typing_extensions import NotRequired

from ..visitors import LrpcVisitor
from .var import LrpcVar, LrpcVarDict


class LrpcStreamDict(TypedDict):
    name: str
    id: int
    origin: str
    params: NotRequired[list[LrpcVarDict]]
    returns: NotRequired[list[LrpcVarDict]]

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

        if self.__origin == LrpcStream.Origin.SERVER:
            assert "returns" not in raw

        self.__params = []
        self.__returns = []

        if "params" in raw:
            self.__params.extend([LrpcVar(p) for p in raw["params"]])

        if "returns" in raw:
            self.__returns.extend([LrpcVar(p) for p in raw["returns"]])


    # def accept(self, visitor: LrpcVisitor) -> None:
        # visitor.visit_lrpc_function(self)

        # for r in self.returns():
        #     visitor.visit_lrpc_function_return(r)
        # visitor.visit_lrpc_function_return_end()

        # for p in self.params():
        #     visitor.visit_lrpc_function_param(p)
        # visitor.visit_lrpc_function_param_end()

        # visitor.visit_lrpc_function_end()

    def params(self) -> list[LrpcVar]:
        return self.__params

    # def param(self, name: str) -> LrpcVar:
        # for p in self.params():
        #     if p.name() == name:
        #         return p

        # raise ValueError(f"No parameter {name} in function {self.name()}")

    def returns(self) -> list[LrpcVar]:
        return self.__returns

    # def ret(self, name: str) -> LrpcVar:
        # for r in self.returns():
        #     if r.name() == name:
        #         return r

        # raise ValueError(f"No return value {name} in function {self.name()}")

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
