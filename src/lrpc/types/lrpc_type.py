"""LrpcType can hold any Python type that is understood by LotusRPC"""

import sys
from collections.abc import Iterable

from pydantic import TypeAdapter

if sys.version_info >= (3, 12):
    from collections.abc import Buffer

    LrpcBuffer = Buffer
else:
    LrpcBuffer = bytes | bytearray | memoryview

LrpcBasicType = bool | int | float | str | LrpcBuffer
LrpcType = LrpcBasicType | Iterable["LrpcType"] | dict[str, "LrpcType"] | None

# pylint: disable=invalid-name
LrpcBasicTypeValidator: TypeAdapter[LrpcBasicType] = TypeAdapter(
    LrpcBasicType,
    config={"arbitrary_types_allowed": True},
)
