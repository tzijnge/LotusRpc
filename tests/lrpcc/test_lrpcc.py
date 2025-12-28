import contextlib
import os
import re
from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

import pydantic
import pytest

from lrpc.lrpcc import LRPCC_CONFIG_ENV_VAR, find_config, load_config


@contextlib.contextmanager
def working_directory(path: Path) -> Generator[None, None, None]:
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


@contextlib.contextmanager
def lrpcc_config_env_var(config_path: Path) -> Generator[None, None, None]:
    old_environ = dict(os.environ)
    os.environ.update({LRPCC_CONFIG_ENV_VAR: str(config_path)})
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    os.chdir(request.fspath.dirname)  # type: ignore[attr-defined]
    yield
    os.chdir(request.config.invocation_params.dir)


def test_find_config_in_cwd() -> None:
    with TemporaryDirectory() as td, working_directory(Path(td)):
        Path(td).joinpath("lrpcc.config.yaml").touch()
        config_path = find_config()
        assert config_path.name == "lrpcc.config.yaml"


def test_find_config_in_cwd_subdir() -> None:
    with TemporaryDirectory() as td, working_directory(Path(td)):
        Path(td).joinpath("d1/d2/d3/").mkdir(parents=True, exist_ok=False)
        Path(td).joinpath("d1/d2/d3/lrpcc.config.yaml").touch()
        config_path = find_config()
        assert {"d1", "d2", "d3", "lrpcc.config.yaml"}.issubset(config_path.parts)


def test_find_first_config_in_cwd_subdir() -> None:
    with TemporaryDirectory() as td, working_directory(Path(td)):
        Path(td).joinpath("d1/d2/d3/").mkdir(parents=True, exist_ok=False)
        Path(td).joinpath("d1/d2/d3/lrpcc.config.yaml").touch()
        Path(td).joinpath("d1/d2/lrpcc.config.yaml").touch()
        config_path = find_config()
        assert "d3" not in config_path.parts
        assert {"d1", "d2", "lrpcc.config.yaml"}.issubset(config_path.parts)


def test_find_config_in_env_var() -> None:
    with (
        TemporaryDirectory() as td,
        working_directory(Path(td)),
        TemporaryDirectory() as td2,
        lrpcc_config_env_var(Path(td2).joinpath("d2/lrpcc.config.yaml")),
    ):
        Path(td2).joinpath("d2").mkdir(parents=True, exist_ok=False)
        Path(td2).joinpath("d2/lrpcc.config.yaml").touch()
        config_path = find_config()
        assert {"d2", "lrpcc.config.yaml"}.issubset(config_path.parts)


def test_find_config_in_env_var_with_non_standard_name() -> None:
    with (
        TemporaryDirectory() as td,
        working_directory(Path(td)),
        TemporaryDirectory() as td2,
        lrpcc_config_env_var(Path(td2).joinpath("d2/config_123.txt")),
    ):
        Path(td2).joinpath("d2").mkdir(parents=True, exist_ok=False)
        Path(td2).joinpath("d2/config_123.txt").touch()
        config_path = find_config()
        assert {"d2", "config_123.txt"}.issubset(config_path.parts)


def test_find_config_in_env_var_file_not_found() -> None:
    with (
        TemporaryDirectory() as td,
        working_directory(Path(td)),
        TemporaryDirectory() as td2,
        lrpcc_config_env_var(Path(td2).joinpath("d2/no_such_file.yaml")),
    ):
        Path(td2).joinpath("d2").mkdir(parents=True, exist_ok=False)
        Path(td2).joinpath("d2/lrpcc.config.yaml").touch()
        with pytest.raises(FileNotFoundError, match="No configuration file found in location"):
            find_config()


def test_find_config_in_cwd_file_not_found() -> None:
    not_found_in_cwd_message = re.escape("No lrpcc configuration (lrpcc.config.yaml) in current working directory")
    with (
        TemporaryDirectory() as td,
        working_directory(Path(td)),
        pytest.raises(FileNotFoundError, match=not_found_in_cwd_message),
    ):
        find_config()


def test_bad_config_additional_entry() -> None:
    with pytest.raises(pydantic.ValidationError, match="Extra inputs are not permitted"):
        load_config(Path("bad_configs/additional_entry.config.yaml"))


def test_bad_config_invalid_log_level() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="Input should be 'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG' or 'NOTSET'",
    ):
        load_config(Path("bad_configs/invalid_log_level.config.yaml"))


def test_bad_config_invalid_transport_params() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="Input should be a valid string",
    ):
        load_config(Path("bad_configs/invalid_transport_params.config.yaml"))


def test_bad_config_invalid_type() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="Input should be a valid string",
    ):
        load_config(Path("bad_configs/invalid_type.config.yaml"))


def test_bad_config_missing_def_url() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="validation error for LrpccConfigDict\ndefinition_url\n  Field required",
    ):
        load_config(Path("bad_configs/missing_def_url.config.yaml"))


def test_bad_config_missing_transport_type() -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="validation error for LrpccConfigDict\ntransport_type\n  Field required",
    ):
        load_config(Path("bad_configs/missing_transport_type.config.yaml"))


def test_load_config() -> None:
    config = load_config(Path("lrpcc.config.yaml"))
    assert config["definition_url"] == "../testdata/TestServer1.lrpc.yaml"
    assert config["transport_type"] == "file"
    assert "transport_params" in config
    assert config["transport_params"] == {"file_url": "server.yaml"}
    assert "log_level" in config
    assert config["log_level"] == "INFO"
    assert "check_server_version" in config
    assert config["check_server_version"] is False
