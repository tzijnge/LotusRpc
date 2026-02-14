import contextlib
import os
import re
from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from lrpc.tools.lrpcc.lrpcc import LRPCC_CONFIG_ENV_VAR, find_config


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
