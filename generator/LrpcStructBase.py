from LrpcVar import LrpcVar
from abc import abstractmethod
from typing import Optional


class LrpcStructBase(object):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fields(self) -> LrpcVar:
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