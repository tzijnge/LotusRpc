from pydantic import TypeAdapter
from typing_extensions import TypedDict


class MetaVersionResponseDict(TypedDict):
    definition: str
    definition_hash: str
    lrpc: str


class MetaErrorResponseDict(TypedDict):
    type: str
    p1: int
    p2: int
    p3: int
    message: str


# pylint: disable=invalid-name
MetaVersionResponseValidator = TypeAdapter(MetaVersionResponseDict)
