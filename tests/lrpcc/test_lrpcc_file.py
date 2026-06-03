import re
import shlex
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from lrpc.tools.lrpcc import Lrpcc, LrpccConfig

with Path("tests/lrpcc/server.yaml").open(encoding="utf-8") as server:
    server_config = yaml.safe_load(server)
    test_params = [(config["cli"], config["response"]) for config in server_config]


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(request.fspath.dirname)  # type: ignore[attr-defined]


def escape_ansi(line: str) -> str:
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


@pytest.mark.parametrize(("cli", "response"), test_params)
def test_lrpcc(cli: str, response: str) -> None:
    runner = CliRunner()
    lrpcc = Lrpcc(LrpccConfig.load(Path("lrpcc.config.yaml")))
    click_group = lrpcc.make_cli()
    args = shlex.split(cli)[1:]  # strip leading "lrpcc"
    result = runner.invoke(click_group, args)
    assert result.exit_code == 0
    assert escape_ansi(result.output).strip() == response.replace("\r\n", "\n")
