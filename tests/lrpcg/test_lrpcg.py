import json
import re
from importlib.metadata import version
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from lrpc.tools.lrpcg.lrpcg import run_cli

TESTDATA = Path(__file__).parent.parent / "testdata"
SERVER1 = str(TESTDATA / "TestServer1.lrpc.yaml")

MINIMAL_DEF = """\
name: MinimalTest
services:
  - name: srv0
    functions:
      - name: f0
"""

DEF_WITH_UNUSED_TYPE = """\
name: WithWarning
services:
  - name: srv0
    functions:
      - name: f0
enums:
  - name: UnusedEnum
    fields: [V0]
"""


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_version(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == version("lotusrpc")


def test_help(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["--help"])
    assert result.exit_code == 0
    commands_section = result.output.split("Commands:\n")[1]
    assert set(re.findall(r"^ {2}(\w+)", commands_section, re.MULTILINE)) == {
        "cpp", "cppcore", "merge", "schema", "puml",
    }


# --- cpp ---


def test_cpp_missing_definition_file(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["cpp"])
    assert result.exit_code == 2
    assert "--definition_file" in result.output


def test_cpp_nonexistent_definition_file(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["cpp", "-d", "no_such_file.yaml"])
    assert result.exit_code == 2


def test_cpp_happy_path(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        Path("test.lrpc.yaml").write_text(MINIMAL_DEF, encoding="utf-8")
        result = runner.invoke(run_cli, ["cpp", "-d", "test.lrpc.yaml", "-o", "output"])
        assert result.exit_code == 0
        out = Path("output")
        assert (out / "srv0_shim.hpp").exists()
        assert (out / "srv0_includes.hpp").exists()
        assert (out / "MinimalTest.hpp").exists()
        assert (out / "lrpccore").is_dir()


def test_cpp_no_core(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        Path("test.lrpc.yaml").write_text(MINIMAL_DEF, encoding="utf-8")
        result = runner.invoke(run_cli, ["cpp", "-d", "test.lrpc.yaml", "-o", "output", "--no-core"])
        assert result.exit_code == 0
        out = Path("output")
        assert (out / "srv0_shim.hpp").exists()
        assert (out / "srv0_includes.hpp").exists()
        assert (out / "MinimalTest.hpp").exists()
        assert not (out / "lrpccore").exists()


def test_cpp_with_overlay(runner: CliRunner) -> None:
    overlay = "merge_strategy: add\nconstants:\n  - name: MY_CONST\n    value: 42\n"
    with runner.isolated_filesystem():
        Path("test.lrpc.yaml").write_text(MINIMAL_DEF, encoding="utf-8")
        Path("overlay.yaml").write_text(overlay, encoding="utf-8")
        result = runner.invoke(
            run_cli, ["cpp", "-d", "test.lrpc.yaml", "-ov", "overlay.yaml", "-o", "output"],
        )
        assert result.exit_code == 0
        out = Path("output")
        assert (out / "srv0_shim.hpp").exists()
        assert (out / "MinimalTest_Constants.hpp").exists()


def test_cpp_warnings_not_errors_by_default(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        Path("test.lrpc.yaml").write_text(DEF_WITH_UNUSED_TYPE, encoding="utf-8")
        result = runner.invoke(run_cli, ["cpp", "-d", "test.lrpc.yaml", "-o", "output"])
        assert result.exit_code == 0
        assert Path("output/srv0_shim.hpp").exists()


def test_cpp_warnings_as_errors(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        Path("test.lrpc.yaml").write_text(DEF_WITH_UNUSED_TYPE, encoding="utf-8")
        result = runner.invoke(run_cli, ["cpp", "-d", "test.lrpc.yaml", "-o", "output", "-w"])
        assert result.exit_code == 1
        assert not Path("output").exists()


def test_cpp_existing_testdata(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(run_cli, ["cpp", "-d", SERVER1, "-o", "output"])
        assert result.exit_code == 0
        assert Path("output/srv0_shim.hpp").exists()


# --- cppcore ---


def test_cppcore_happy_path(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(run_cli, ["cppcore", "-o", "output"])
        assert result.exit_code == 0
        core_dir = Path("output/lrpccore")
        assert core_dir.is_dir()
        assert any(core_dir.iterdir())


def test_cppcore_byte_type_char(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(run_cli, ["cppcore", "-o", "output", "-b", "char"])
        assert result.exit_code == 0
        core_dir = Path("output/lrpccore")
        assert core_dir.is_dir()
        byte_types_file = core_dir / "LrpcByteTypes.hpp"
        assert byte_types_file.exists()
        assert "char" in byte_types_file.read_text(encoding="utf-8")


def test_cppcore_invalid_byte_type(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["cppcore", "-b", "not_a_byte_type"])
    assert result.exit_code == 2


# --- merge ---


def test_merge_missing_definition_file(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["merge"])
    assert result.exit_code == 2


def test_merge_missing_overlay(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        Path("base.yaml").write_text(MINIMAL_DEF, encoding="utf-8")
        result = runner.invoke(run_cli, ["merge", "-d", "base.yaml", "-o", "merged.yaml"])
        assert result.exit_code == 2


def test_merge_invalid_overlay(runner: CliRunner) -> None:
    # An overlay without merge_strategy gets "unspecified" strategy, which raises
    # ValueError for any non-None value, hitting the except block in merge command.
    bad_overlay = "unknown_field: some_value\n"
    with runner.isolated_filesystem():
        Path("base.yaml").write_text(MINIMAL_DEF, encoding="utf-8")
        Path("bad_overlay.yaml").write_text(bad_overlay, encoding="utf-8")
        result = runner.invoke(
            run_cli, ["merge", "-d", "base.yaml", "-ov", "bad_overlay.yaml", "-o", "merged.yaml"],
        )
        assert result.exit_code == 1
        assert not Path("merged.yaml").exists()


def test_merge_happy_path(runner: CliRunner) -> None:
    overlay = "merge_strategy: add\nconstants:\n  - name: MY_CONST\n    value: 42\n"
    with runner.isolated_filesystem():
        Path("base.yaml").write_text(MINIMAL_DEF, encoding="utf-8")
        Path("overlay.yaml").write_text(overlay, encoding="utf-8")
        result = runner.invoke(
            run_cli, ["merge", "-d", "base.yaml", "-ov", "overlay.yaml", "-o", "merged.yaml"],
        )
        assert result.exit_code == 0
        assert Path("merged.yaml").exists()
        merged = yaml.safe_load(Path("merged.yaml").read_text(encoding="utf-8"))
        assert merged["name"] == "MinimalTest"
        assert any(c["name"] == "MY_CONST" for c in merged["constants"])


# --- schema ---


def test_schema_happy_path(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(run_cli, ["schema", "-o", "output"])
        assert result.exit_code == 0
        schema_file = Path("output/lotusrpc-schema.json")
        assert schema_file.exists()
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        assert "$schema" in schema


# --- puml ---


def test_puml_missing_definition_file(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["puml"])
    assert result.exit_code == 2


def test_puml_nonexistent_definition_file(runner: CliRunner) -> None:
    result = runner.invoke(run_cli, ["puml", "-d", "no_such_file.yaml"])
    assert result.exit_code == 2


def test_puml_happy_path(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        Path("test.lrpc.yaml").write_text(MINIMAL_DEF, encoding="utf-8")
        result = runner.invoke(run_cli, ["puml", "-d", "test.lrpc.yaml", "-o", "output"])
        assert result.exit_code == 0
        puml_file = Path("output/MinimalTest.puml")
        assert puml_file.exists()
        content = puml_file.read_text(encoding="utf-8")
        assert "@startmindmap" in content
        assert "@endmindmap" in content


def test_puml_warnings_as_errors(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        Path("test.lrpc.yaml").write_text(DEF_WITH_UNUSED_TYPE, encoding="utf-8")
        result = runner.invoke(run_cli, ["puml", "-d", "test.lrpc.yaml", "-o", "output", "-w"])
        assert result.exit_code == 1
        assert result.exception is not None
        assert not Path("output/WithWarning.puml").exists()
