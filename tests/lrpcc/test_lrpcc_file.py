import os
import subprocess
from collections.abc import Generator
from importlib.metadata import version
from pathlib import Path

import pytest
import yaml

with Path("tests/lrpcc/server.yaml").open(encoding="utf-8") as server:
    server_config = yaml.safe_load(server)
    test_params = [(config["cli"], config["response"]) for config in server_config]


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    os.chdir(request.fspath.dirname)  # type: ignore[attr-defined]
    yield
    os.chdir(request.config.invocation_params.dir)


@pytest.mark.parametrize(("cli", "response"), test_params)
def test_lrpcc(cli: str, response: str) -> None:
    result = subprocess.run(cli, shell=True, capture_output=True, check=False)  # noqa: S602

    assert result.returncode == 0
    assert result.stderr.decode().strip() == ""
    assert result.stdout.decode().strip() == response.replace("\r\n", os.linesep)


def test_lrpcc_version() -> None:
    cli = "lrpcc --version"
    expected_response = f"{version('lotusrpc')}"
    result = subprocess.run(cli, shell=True, capture_output=True, check=False)  # noqa: S602

    assert result.returncode == 0
    assert result.stderr.decode().strip() == ""
    actual_response = result.stdout.decode().strip()
    assert actual_response == expected_response


def test_lrpcc_help() -> None:
    cli = "lrpcc --help"
    expected_response = """Usage: lrpcc [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show version and exit.
  --help     Show this message and exit.

Commands:
  s0
"""
    result = subprocess.run(cli, shell=True, capture_output=True, check=False)  # noqa: S602

    assert result.returncode == 0
    assert result.stderr.decode().strip() == ""
    actual_response = result.stdout.decode().replace("\r\n", "\n")
    assert actual_response == expected_response


def test_lrpcc_no_args() -> None:
    cli = "lrpcc"
    expected_response = """Usage: lrpcc [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show version and exit.
  --help     Show this message and exit.

Commands:
  s0
"""
    result = subprocess.run(cli, shell=True, capture_output=True, check=False)  # noqa: S602

    assert result.returncode == 2
    assert result.stdout.decode().strip() == ""
    actual_response = result.stderr.decode().replace("\r\n", "\n")
    assert actual_response == expected_response
