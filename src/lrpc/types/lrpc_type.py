"""LrpcType can hold any Python type that is understood by LotusRPC"""

import sys

if sys.version_info >= (3, 12):
    from collections.abc import Buffer

    LrpcBuffer = Buffer
else:
    LrpcBuffer = bytes | bytearray | memoryview

from collections.abc import Iterable

from pydantic import TypeAdapter

LrpcBasicType = bool | int | float | str | LrpcBuffer
LrpcType = LrpcBasicType | Iterable["LrpcType"] | dict[str, "LrpcType"] | None

LrpcBasicTypeValidator: TypeAdapter[LrpcBasicType] = TypeAdapter(
    LrpcBasicType,
    config={"arbitrary_types_allowed": True},
)
