from typing import Optional

from abc import ABC, abstractmethod

class LrpcEnumFieldBase(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def id(self) -> str:
        pass

class LrpcEnumBase(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fields(self):
        pass

    @abstractmethod
    def is_external(self) -> bool:
        pass

    @abstractmethod
    def external_file(self) -> Optional[str]:
        pass

    @abstractmethod
    def external_namespace(self) -> Optional[str]:
        pass