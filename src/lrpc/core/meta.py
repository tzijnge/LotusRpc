from pydantic import TypeAdapter
from typing_extensions import TypedDict


class MetaVersionResponseDict(TypedDict):
    definition: str
    definition_hash: str
    lrpc: str


# pylint: disable=invalid-name
MetaVersionResponseValidator = TypeAdapter(MetaVersionResponseDict)
