import os
import subprocess

import pytest
import yaml

with open("tests/lrpcc/server.yaml", mode="rt", encoding="utf-8") as server:
    server_config = yaml.safe_load(server)
    test_params = [(config["cli"], config["response"]) for config in server_config]


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest):  # type: ignore[no-untyped-def]
    os.chdir(request.fspath.dirname)  # type: ignore[attr-defined]
    yield
    os.chdir(request.config.invocation_params.dir)


@pytest.mark.parametrize("cli, response", test_params)
def test_lrpcc(cli: str, response: str) -> None:
    result = subprocess.run(cli, shell=True, capture_output=True, check=False)

    assert result.returncode == 0
    assert result.stderr.decode().strip() == ""
    assert result.stdout.decode().strip() == response.replace("\r\n", os.linesep)
