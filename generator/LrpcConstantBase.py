
from abc import ABC, abstractmethod
from typing import Union

class LrpcConstantBase(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def value(self) -> Union[str, int, float, bool]:
        pass

    @abstractmethod
    def cpp_type(self) -> str:
        pass