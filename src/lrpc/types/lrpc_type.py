"""LrpcType can hold any Python type that is understood by LotusRPC"""

from typing import Union, Iterable

LrpcBasicType = Union[bool, int, float, str]
LrpcType = Union[LrpcBasicType, Iterable["LrpcType"], dict[str, "LrpcType"], None]
