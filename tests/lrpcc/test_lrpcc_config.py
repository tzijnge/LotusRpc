import os
import re
import tempfile
from collections.abc import Generator
from pathlib import Path

import pydantic
import pytest

from lrpc.tools.lrpcc import LrpccConfig, LrpccConfigDict


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    os.chdir(request.fspath.dirname)  # type: ignore[attr-defined]
    yield
    os.chdir(request.config.invocation_params.dir)


def test_minimal_config() -> None:
    config_dict: LrpccConfigDict = {"transport_type": "my_transport"}

    with pytest.raises(
        ValueError,
        match=re.escape("'definition_url' must be specified when 'definition_from_server' is never (default)"),
    ):
        LrpccConfig(config_dict)


def test_minimal_config_non_existing_definition_url() -> None:
    config_dict: LrpccConfigDict = {
        "transport_type": "my_transport",
        "definition_url": "bad_definition.lrpc.yaml",
    }

    resolved_url = Path("bad_definition.lrpc.yaml").resolve()
    with pytest.raises(
        FileNotFoundError,
        match=re.escape(f"{resolved_url} must exist when 'definition_from_server' is never (default)"),
    ):
        LrpccConfig(config_dict)


def test_minimal_config_valid_definition_url() -> None:
    config_dict: LrpccConfigDict = {
        "transport_type": "my_transport",
        "definition_url": "../testdata/TestServer1.lrpc.yaml",
    }

    config = LrpccConfig(config_dict)
    assert config.transport_type() == "my_transport"
    assert config.transport_params() == {}
    assert config.definition_url() == Path("../testdata/TestServer1.lrpc.yaml").resolve()
    assert config.check_server_version() is True
    assert config.definition_from_server() == "never"
    assert config.log_level() == "INFO"


def test_minimal_config_definition_from_server() -> None:
    config_dict: LrpccConfigDict = {
        "transport_type": "my_transport",
        "definition_from_server": "always",
    }

    config = LrpccConfig(config_dict)
    assert config.transport_type() == "my_transport"
    assert config.transport_params() == {}
    with pytest.raises(AssertionError, match="Function should not be called when definition_from_server is 'always'"):
        config.definition_url()
    assert config.check_server_version() is True
    assert config.definition_from_server() == "always"
    assert config.log_level() == "INFO"


def test_full_config() -> None:
    config_dict: LrpccConfigDict = {
        "transport_type": "my_fancy_transport",
        "transport_params": {
            "p1": True,
            "p2": "yes",
            "p3": 77,
            "p4": 33.44,
        },
        "definition_url": "tests/testdata/TestServer1.lrpc.yaml",
        "check_server_version": False,
        "definition_from_server": "always",
        "log_level": "ERROR",
    }

    config = LrpccConfig(config_dict)
    assert config.transport_type() == "my_fancy_transport"
    assert config.transport_params() == {
        "p1": True,
        "p2": "yes",
        "p3": 77,
        "p4": 33.44,
    }
    assert config.definition_url() == Path("tests/testdata/TestServer1.lrpc.yaml").resolve()
    assert config.check_server_version() is False
    assert config.definition_from_server() == "always"
    assert config.log_level() == "ERROR"


def test_definition_url_not_specified_when_definition_from_server_is_once() -> None:
    config_dict: LrpccConfigDict = {
        "transport_type": "my_transport",
        "definition_from_server": "once",
    }

    with pytest.raises(
        ValueError,
        match=re.escape("'definition_url' must be specified when 'definition_from_server' is once"),
    ):
        LrpccConfig(config_dict)


def test_create_and_load() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir).joinpath("lrpcc.config.yaml")

        LrpccConfig.create(config_path, "test.lrpc.yaml", "my_transport")

        config = LrpccConfig.load(config_path)
        assert config.transport_type() == "my_transport"
        assert config.transport_params() == {}
        assert config.definition_url() == Path("test.lrpc.yaml").resolve()
        assert config.check_server_version() is True
        assert config.definition_from_server() == "once"
        assert config.log_level() == "INFO"


def test_create_and_load_serial() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir).joinpath("lrpcc.config.yaml")

        LrpccConfig.create(config_path, "test.lrpc.yaml", "serial")

        config = LrpccConfig.load(config_path)
        assert config.transport_type() == "serial"
        assert config.transport_params() == {
            "port": "<PORT>",
            "baudrate": "<BAUDRATE>",
        }
        assert config.definition_url() == Path("test.lrpc.yaml").resolve()
        assert config.check_server_version() is True
        assert config.definition_from_server() == "once"
        assert config.log_level() == "INFO"


def test_load_empty() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir).joinpath("test.lrpc.yaml")
        config_path.touch()
        with pytest.raises(ValueError, match=re.escape(f"Configuration file {config_path} is empty")):
            LrpccConfig.load(config_path)


def test_bad_config_additional_entry() -> None:
    with pytest.raises(pydantic.ValidationError, match="Extra inputs are not permitted"):
        LrpccConfig.load(Path("bad_configs/additional_entry.config.yaml"))


def test_bad_config_invalid_log_level() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="Input should be 'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG' or 'NOTSET'",
    ):
        LrpccConfig.load(Path("bad_configs/invalid_log_level.config.yaml"))


def test_bad_config_invalid_transport_params() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="Input should be a valid string",
    ):
        LrpccConfig.load(Path("bad_configs/invalid_transport_params.config.yaml"))


def test_bad_config_invalid_type() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="Input should be a valid string",
    ):
        LrpccConfig.load(Path("bad_configs/invalid_type.config.yaml"))


def test_bad_config_missing_def_url() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape("'definition_url' must be specified when 'definition_from_server' is never (default)"),
    ):
        LrpccConfig.load(Path("bad_configs/missing_def_url.config.yaml"))


def test_bad_config_missing_transport_type() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="validation error for LrpccConfigDict\ntransport_type\n  Field required",
    ):
        LrpccConfig.load(Path("bad_configs/missing_transport_type.config.yaml"))


def test_load_config() -> None:
    config = LrpccConfig.load(Path("lrpcc.config.yaml"))
    assert config.definition_url() == Path("../testdata/TestServer1.lrpc.yaml").resolve()
    assert config.definition_from_server() == "never"
    assert config.transport_type() == "file"
    assert config.transport_params() == {"file_url": "server.yaml"}
    assert config.log_level() == "INFO"
    assert config.check_server_version() is False
