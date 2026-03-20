from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict


class RpcSettingsDict(TypedDict):
    version: NotRequired[str]
    definition_hash_length: NotRequired[int]
    embed_definition: NotRequired[bool]
    namespace: NotRequired[str]
    rx_buffer_size: NotRequired[int]
    tx_buffer_size: NotRequired[int]


# pylint: disable=invalid-name
RpcSettingsValidator = TypeAdapter(RpcSettingsDict)


class RpcSettings:
    def __init__(self, raw: RpcSettingsDict) -> None:
        RpcSettingsValidator.validate_python(raw, strict=True, extra="forbid")

        self._version = raw.get("version", None)
        self._definition_hash_length = raw.get("definition_hash_length", None)
        self._embed_definition = raw.get("embed_definition", False)
        self._namespace = raw.get("namespace", None)
        self._rx_buffer_size = raw.get("rx_buffer_size", 256)
        self._tx_buffer_size = raw.get("tx_buffer_size", 256)

    def version(self) -> str | None:
        return self._version

    def definition_hash_length(self) -> int | None:
        return self._definition_hash_length

    def embed_definition(self) -> bool:
        return self._embed_definition

    def namespace(self) -> str | None:
        return self._namespace

    def rx_buffer_size(self) -> int:
        return self._rx_buffer_size

    def tx_buffer_size(self) -> int:
        return self._tx_buffer_size
