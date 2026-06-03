import re
from pathlib import Path

import pytest

from lrpc.tools.lrpcc.lrpcc import LRPCC_CONFIG_ENV_VAR, find_config


def test_find_config_in_cwd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "lrpcc.config.yaml").touch()
    config_path = find_config()
    assert config_path.name == "lrpcc.config.yaml"


def test_find_config_in_cwd_subdir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    subdir = tmp_path / "d1" / "d2" / "d3"
    subdir.mkdir(parents=True)
    (subdir / "lrpcc.config.yaml").touch()
    config_path = find_config()
    assert {"d1", "d2", "d3", "lrpcc.config.yaml"}.issubset(config_path.parts)


def test_find_first_config_in_cwd_subdir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "d1" / "d2" / "d3").mkdir(parents=True)
    (tmp_path / "d1" / "d2" / "d3" / "lrpcc.config.yaml").touch()
    (tmp_path / "d1" / "d2" / "lrpcc.config.yaml").touch()
    config_path = find_config()
    assert "d3" not in config_path.parts
    assert {"d1", "d2", "lrpcc.config.yaml"}.issubset(config_path.parts)


def test_find_config_in_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    config_file = tmp_path / "env_dir" / "d2" / "lrpcc.config.yaml"
    config_file.parent.mkdir(parents=True)
    config_file.touch()
    monkeypatch.setenv(LRPCC_CONFIG_ENV_VAR, str(config_file))
    config_path = find_config()
    assert {"d2", "lrpcc.config.yaml"}.issubset(config_path.parts)


def test_find_config_in_env_var_with_non_standard_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    config_file = tmp_path / "env_dir" / "d2" / "config_123.txt"
    config_file.parent.mkdir(parents=True)
    config_file.touch()
    monkeypatch.setenv(LRPCC_CONFIG_ENV_VAR, str(config_file))
    config_path = find_config()
    assert {"d2", "config_123.txt"}.issubset(config_path.parts)


def test_find_config_in_env_var_file_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    (tmp_path / "env_dir" / "d2").mkdir(parents=True)
    (tmp_path / "env_dir" / "d2" / "lrpcc.config.yaml").touch()
    nonexistent = tmp_path / "env_dir" / "d2" / "no_such_file.yaml"
    monkeypatch.setenv(LRPCC_CONFIG_ENV_VAR, str(nonexistent))
    with pytest.raises(FileNotFoundError, match="No configuration file found in location"):
        find_config()


def test_find_config_in_cwd_file_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    not_found_message = re.escape("No lrpcc configuration (lrpcc.config.yaml) in current working directory")
    with pytest.raises(FileNotFoundError, match=not_found_message):
        find_config()
