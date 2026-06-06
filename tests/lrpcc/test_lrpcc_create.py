import re
from importlib.metadata import version
from pathlib import Path

import yaml
from click.testing import CliRunner

from lrpc.tools.lrpcc.lrpcc import run_lrpcc_config_creator

EXPECTED_CONFIG_KEYS = {
    "definition_url", "definition_from_server", "transport_type",
    "transport_params", "log_level", "check_server_version",
}


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(run_lrpcc_config_creator, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == version("lotusrpc")


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(run_lrpcc_config_creator, ["--help"])
    assert result.exit_code == 0
    commands_section = result.output.split("Commands:\n")[1]
    assert set(re.findall(r"^ {2}(\w+)", commands_section, re.MULTILINE)) == {"create"}


def test_no_subcommand_shows_help() -> None:
    runner = CliRunner()
    result = runner.invoke(run_lrpcc_config_creator, [])
    assert result.exit_code in (0, 2)
    assert "create" in result.output


def test_create_serial() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(run_lrpcc_config_creator, ["create", "-d", "my.lrpc.yaml", "-t", "serial"])
        assert result.exit_code == 0
        config_path = Path("lrpcc.config.yaml")
        assert config_path.exists()
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert set(config.keys()) == EXPECTED_CONFIG_KEYS
        assert config["transport_type"] == "serial"
        assert config["definition_url"] == "my.lrpc.yaml"
        assert config["definition_from_server"] == "once"
        assert config["log_level"] == "INFO"
        assert config["check_server_version"] is True
        assert config["transport_params"]["port"] == "<PORT>"
        assert config["transport_params"]["baudrate"] == "<BAUDRATE>"


def test_create_no_args() -> None:
    runner = CliRunner()
    result = runner.invoke(run_lrpcc_config_creator, ["create"])
    assert result.exit_code == 2


def test_create_missing_transport() -> None:
    runner = CliRunner()
    result = runner.invoke(run_lrpcc_config_creator, ["create", "-d", "my.lrpc.yaml"])
    assert result.exit_code == 2


def test_create_invalid_transport_type() -> None:
    runner = CliRunner()
    result = runner.invoke(run_lrpcc_config_creator, ["create", "-d", "my.lrpc.yaml", "-t", "generic"])
    assert result.exit_code == 2
