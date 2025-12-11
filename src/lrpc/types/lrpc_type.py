"""LrpcType can hold any Python type that is understood by LotusRPC"""

from collections.abc import Iterable

LrpcBasicType = bool | int | float | str
LrpcType = LrpcBasicType | Iterable["LrpcType"] | dict[str, "LrpcType"] | None
