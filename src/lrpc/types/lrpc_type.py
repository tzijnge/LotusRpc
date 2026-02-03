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

LrpcResponseBasicType = bool | int | float | str | bytes
LrpcResponseType = LrpcResponseBasicType | Iterable["LrpcResponseType"] | dict[str, "LrpcResponseType"] | None

# pylint: disable=invalid-name
LrpcResponseBasicTypeValidator: TypeAdapter[LrpcResponseBasicType] = TypeAdapter(
    LrpcResponseBasicType,
    config={"arbitrary_types_allowed": True},
)
