import pytest
from pydantic import ValidationError

from lrpc.core.settings import RpcSettings, RpcSettingsDict


def test_empty() -> None:
    s: RpcSettingsDict = {}
    settings = RpcSettings(s)

    assert settings.version() is None
    assert settings.definition_hash_length() == 64
    assert settings.embed_definition() is False
    assert settings.namespace() is None
    assert settings.rx_buffer_size() == 256
    assert settings.tx_buffer_size() == 256
    assert settings.byte_type() == "uint8_t"


def test_all_settings() -> None:
    s: RpcSettingsDict = {
        "version": "1.2.3",
        "definition_hash_length": 32,
        "embed_definition": True,
        "namespace": "my_app",
        "rx_buffer_size": 512,
        "tx_buffer_size": 1024,
        "byte_type": "char8_t",
    }
    settings = RpcSettings(s)

    assert settings.version() == "1.2.3"
    assert settings.definition_hash_length() == 32
    assert settings.embed_definition() is True
    assert settings.namespace() == "my_app"
    assert settings.rx_buffer_size() == 512
    assert settings.tx_buffer_size() == 1024
    assert settings.byte_type() == "char8_t"


def test_version_only() -> None:
    s: RpcSettingsDict = {"version": "2.0.0"}
    settings = RpcSettings(s)

    assert settings.version() == "2.0.0"
    assert settings.definition_hash_length() == 64
    assert settings.embed_definition() is False
    assert settings.namespace() is None
    assert settings.rx_buffer_size() == 256
    assert settings.tx_buffer_size() == 256
    assert settings.byte_type() == "uint8_t"


def test_definition_hash_length_only() -> None:
    s: RpcSettingsDict = {"definition_hash_length": 20}
    settings = RpcSettings(s)

    assert settings.version() is None
    assert settings.definition_hash_length() == 20
    assert settings.embed_definition() is False
    assert settings.namespace() is None
    assert settings.rx_buffer_size() == 256
    assert settings.tx_buffer_size() == 256
    assert settings.byte_type() == "uint8_t"


def test_embed_definition_only() -> None:
    s: RpcSettingsDict = {"embed_definition": True}
    settings = RpcSettings(s)

    assert settings.version() is None
    assert settings.definition_hash_length() == 64
    assert settings.embed_definition() is True
    assert settings.namespace() is None
    assert settings.rx_buffer_size() == 256
    assert settings.tx_buffer_size() == 256
    assert settings.byte_type() == "uint8_t"


def test_namespace_only() -> None:
    s: RpcSettingsDict = {"namespace": "my::namespace"}
    settings = RpcSettings(s)

    assert settings.version() is None
    assert settings.definition_hash_length() == 64
    assert settings.embed_definition() is False
    assert settings.namespace() == "my::namespace"
    assert settings.rx_buffer_size() == 256
    assert settings.tx_buffer_size() == 256
    assert settings.byte_type() == "uint8_t"


def test_buffer_sizes_only() -> None:
    s: RpcSettingsDict = {"rx_buffer_size": 512, "tx_buffer_size": 1024}
    settings = RpcSettings(s)

    assert settings.version() is None
    assert settings.definition_hash_length() == 64
    assert settings.embed_definition() is False
    assert settings.namespace() is None
    assert settings.rx_buffer_size() == 512
    assert settings.tx_buffer_size() == 1024
    assert settings.byte_type() == "uint8_t"


def test_byte_type_only() -> None:
    s: RpcSettingsDict = {"byte_type": "etl::byte"}
    settings = RpcSettings(s)

    assert settings.version() is None
    assert settings.definition_hash_length() == 64
    assert settings.embed_definition() is False
    assert settings.namespace() is None
    assert settings.rx_buffer_size() == 256
    assert settings.tx_buffer_size() == 256
    assert settings.byte_type() == "etl::byte"


def test_validation_extra_fields() -> None:
    s = {
        "version": "1.0.0",
        "extra_field": "not allowed",
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]


def test_validation_wrong_type_version() -> None:
    s = {
        "version": 123,
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]


def test_validation_wrong_type_definition_hash_length() -> None:
    s = {
        "definition_hash_length": "not an int",
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]


def test_validation_wrong_type_embed_definition() -> None:
    s = {
        "embed_definition": "true",
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]


def test_validation_wrong_type_namespace() -> None:
    s = {
        "namespace": 123,
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]


def test_validation_wrong_type_rx_buffer_size() -> None:
    s = {
        "rx_buffer_size": "512",
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]


def test_validation_wrong_type_tx_buffer_size() -> None:
    s = {
        "tx_buffer_size": "1024",
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]


def test_validation_wrong_byte_type() -> None:
    s = {
        "byte_type": "int",
    }

    with pytest.raises(ValidationError):
        RpcSettings(s)  # type: ignore[arg-type]
