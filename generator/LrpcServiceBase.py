from abc import ABC, abstractmethod


class LrpcServiceBase(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def id(self) -> int:
        pass

    @abstractmethod
    def functions(self):
        pass

    @abstractmethod
    def required_includes(self) -> set[str]:
        pass