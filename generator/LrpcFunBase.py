from LrpcVar import LrpcVar
from abc import ABC, abstractmethod


class LrpcFunBase(ABC):
    @abstractmethod
    def params(self) -> list[LrpcVar]:
        pass

    @abstractmethod
    def returns(self) -> list[LrpcVar]:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def id(self) -> int:
        pass

    @abstractmethod
    def number_returns(self) -> int:
        pass

    @abstractmethod
    def param_names(self) -> list[str]:
        pass

    @abstractmethod
    def required_includes(self) -> list[str]:
        pass