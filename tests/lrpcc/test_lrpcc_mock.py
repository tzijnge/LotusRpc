import logging
import re
import sys
import tempfile
import types
from pathlib import Path
from typing import Literal
from unittest.mock import patch

import pytest

from lrpc.client import LrpcClient
from lrpc.tools.lrpcc import Lrpcc, LrpccConfig, LrpccConfigDict
from lrpc.tools.lrpcc.lrpcc import run_cli
from tests.embedded_definition import embedded_definition_for_testing

# pylint: disable=protected-access
# ruff: noqa: SLF001


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(request.fspath.dirname)  # type: ignore[attr-defined]


def escape_ansi(line: str) -> str:
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


def make_lrpcc(
    definition_url: str,
    response: str = "",
    *,
    check_server_version: bool = False,
    definition_from_server: Literal["always", "never", "once"] = "never",
) -> Lrpcc:
    # dummy version response with all fields set to empty string
    meta_version_response = "05ff02000000" if check_server_version else ""

    lrpcc_config: LrpccConfigDict = {
        "definition_url": definition_url,
        "transport_type": "mock",
        "transport_params": {"response": meta_version_response + response},
        "check_server_version": check_server_version,
        "definition_from_server": definition_from_server,
    }
    return Lrpcc(LrpccConfig(lrpcc_config))


def test_server1_f13(capsys: pytest.CaptureFixture[str]) -> None:
    response = "04000dcdab"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("srv0", "f13")

    expected_response = """r0: 43981 (0xabcd)
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server1_f13_with_version_check(capsys: pytest.CaptureFixture[str]) -> None:
    response = "04000dcdab"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=True)
    lrpcc._command_handler("srv0", "f13")

    expected_response = """r0: 43981 (0xabcd)
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server1_f29(capsys: pytest.CaptureFixture[str]) -> None:
    response = "06001d03334455"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("srv0", "f29", p0=b"\x77\x88\x99")

    expected_response = """r0: [33 44 55]
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server1_f30(capsys: pytest.CaptureFixture[str]) -> None:
    response = "02001e"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("srv0", "f30", p0=[b"\x33\x44", b"\x55\x66"])

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server1_stream0(capsys: pytest.CaptureFixture[str]) -> None:
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", check_server_version=False)
    lrpcc._command_handler("srv0", "stream0", p0=b"\x77\x88\x99", final=False)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server1_stream0_final(capsys: pytest.CaptureFixture[str]) -> None:
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", check_server_version=False)
    lrpcc._command_handler("srv0", "stream0", p0=b"\x77\x88\x99", final=True)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_client_infinite(capsys: pytest.CaptureFixture[str]) -> None:
    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml")
    lrpcc._command_handler("srv0", "client_infinite", p0=1234, p1=56)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_client_finite(capsys: pytest.CaptureFixture[str]) -> None:
    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml")
    lrpcc._command_handler("srv0", "client_finite", p0=True, p1="Open", final=False)

    assert escape_ansi(capsys.readouterr().out) == ""

    lrpcc._command_handler("srv0", "client_finite", p0=True, p1="Closed", final=True)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server_infinite_start(capsys: pytest.CaptureFixture[str]) -> None:
    response = "054200d20438"
    response += "0542000a1a4d"
    response += "054200e8fd03"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    with pytest.raises(TimeoutError, match="Timeout waiting for response"):
        lrpcc._command_handler("srv1", "server_infinite", start=True)

    expected_response = """[#0]
p0: 1234 (0x4d2)
p1: 56 (0x38)
[#1]
p0: 6666 (0x1a0a)
p1: 77 (0x4d)
[#2]
p0: 65000 (0xfde8)
p1: 3 (0x3)
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server_infinite_stop(capsys: pytest.CaptureFixture[str]) -> None:
    response = "054200d20438"
    response += "0542000a1a4d"
    response += "054200e8fd03"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    lrpcc._command_handler("srv1", "server_infinite", start=False)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server_finite_start(capsys: pytest.CaptureFixture[str]) -> None:
    response = "054221000000"
    response += "054221010100"
    response += "054221000101"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    lrpcc._command_handler("srv1", "server_finite", start=True)

    expected_response = """[#0]
p0: False
p1: Open
[#1]
p0: True
p1: Closed
[#2]
p0: False
p1: Closed
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server_finite_start_no_final_response(capsys: pytest.CaptureFixture[str]) -> None:
    response = "054221000000"
    response += "054221010100"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)

    with pytest.raises(TimeoutError, match="Timeout waiting for response"):
        lrpcc._command_handler("srv1", "server_finite", start=True)

    expected_response = """[#0]
p0: False
p1: Open
[#1]
p0: True
p1: Closed
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server_finite_stop(capsys: pytest.CaptureFixture[str]) -> None:
    response = "054221000000"
    response += "054221010100"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    lrpcc._command_handler("srv1", "server_finite", start=False)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_error_response_unknown_service(capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture) -> None:
    response = "0aff000044550000000000"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("srv0", "f13")

    expected_log = "Server reported error 'UnknownService' for call to srv0.f13"
    expected_print = "Server reported call to unknown service with ID 68. Function or stream ID is 85"

    assert len(caplog.messages) == 1
    assert caplog.messages[0] == expected_log
    assert escape_ansi(capsys.readouterr().out.strip()) == expected_print


def test_error_response_unknown_function_or_stream(
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    response = "0aff000144550000000000"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("srv0", "f13")

    expected_log = "Server reported error 'UnknownFunctionOrStream' for call to srv0.f13"
    expected_print = "Server reported call to unknown function or stream with ID 85 in service with ID 68"

    assert len(caplog.messages) == 1
    assert caplog.messages[0] == expected_log
    assert escape_ansi(capsys.readouterr().out.strip()) == expected_print


def test_definition_from_server_always(capsys: pytest.CaptureFixture[str]) -> None:
    response = embedded_definition_for_testing()
    # actual response to s0.f0
    response += b"\x02\x00\x00"

    lrpcc = make_lrpcc(
        "",
        response.hex(),
        check_server_version=False,
        definition_from_server="always",
    )
    lrpcc._command_handler("srv0", "f0")

    assert escape_ansi(capsys.readouterr().out) == ""


def test_definition_from_server_once(capsys: pytest.CaptureFixture[str]) -> None:
    response = embedded_definition_for_testing()
    # actual response to srv0.f0. Times 2 to make sure srv0.f0 can be called again without retrieving the
    # embedded definition again
    response += b"\x02\x00\x00"
    response += b"\x02\x00\x00"

    with tempfile.TemporaryDirectory() as temp_dir:
        definition_file = Path(temp_dir).joinpath("test_definition_from_server_once.lrpc.yaml")
        assert not definition_file.exists()

        lrpcc = make_lrpcc(
            str(definition_file),
            response.hex(),
            check_server_version=False,
            definition_from_server="once",
        )
        lrpcc._command_handler("srv0", "f0")
        assert definition_file.exists()

        lrpcc._command_handler("srv0", "f0")

        assert escape_ansi(capsys.readouterr().out) == ""


def test_definition_from_server_when_server_has_no_embedded_definition() -> None:
    with pytest.raises(ValueError, match="No embedded definition found on server"):
        make_lrpcc("", "04ff010001", check_server_version=False, definition_from_server="always")


def test_definition_from_server_once_existing_file(capsys: pytest.CaptureFixture[str]) -> None:
    # Step 1: "once" with no file — server provides the embedded definition and saves it
    setup_response = (embedded_definition_for_testing() + b"\x02\x00\x00").hex()
    with tempfile.TemporaryDirectory() as temp_dir:
        definition_file = Path(temp_dir) / "saved.lrpc.yaml"
        make_lrpcc(str(definition_file), setup_response, check_server_version=False, definition_from_server="once")
        assert definition_file.exists()

        # Step 2: "once" with the now-existing file — loads from disk (hits line 123)
        lrpcc = make_lrpcc(
            str(definition_file),
            b"\x02\x00\x00".hex(),
            check_server_version=False,
            definition_from_server="once",
        )
        lrpcc._command_handler("srv0", "f0")
        assert escape_ansi(capsys.readouterr().out) == ""


def test_invalid_log_level(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="lrpc.tools.lrpcc.lrpcc")
    Lrpcc._set_log_level("NOT_A_LEVEL")
    assert "Invalid log level: NOT_A_LEVEL" in caplog.text


def test_error_response_unknown_type(capsys: pytest.CaptureFixture[str]) -> None:
    # The decoder enforces the LrpcMetaError enum, so only the two known types
    # can arrive via the normal protocol path. Call _print_error_response directly
    # with a constructed dict to reach the else branch (lines 227-233).
    Lrpcc._print_error_response({
        "type": "FutureErrorType",
        "p1": 42,
        "p2": 99,
        "p3": 7,
        "message": "something went wrong",
    })
    output = escape_ansi(capsys.readouterr().out.strip())
    assert "Server reported an unknown error (type='FutureErrorType')" in output
    assert "p1=42" in output
    assert "p2=99" in output
    assert "p3=7" in output
    assert "message='something went wrong'" in output


def test_make_transport_no_transport_class(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "lrpcc_bad.py").write_text("# no Transport class\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    config = LrpccConfig({"transport_type": "bad", "definition_from_server": "always"})
    with pytest.raises(AttributeError, match="No class named 'Transport'"):
        Lrpcc._make_transport(config)


def test_make_transport_no_read_method(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "lrpcc_noread.py").write_text("class Transport:\n    pass\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    config = LrpccConfig({"transport_type": "noread", "definition_from_server": "always"})
    with pytest.raises(AttributeError, match="No method named 'read'"):
        Lrpcc._make_transport(config)


def test_make_transport_no_write_method(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    plugin = "class Transport:\n    def read(self): pass\n"
    (tmp_path / "lrpcc_nowrite.py").write_text(plugin, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    config = LrpccConfig({"transport_type": "nowrite", "definition_from_server": "always"})
    with pytest.raises(AttributeError, match="No method named 'write'"):
        Lrpcc._make_transport(config)


def test_run() -> None:
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml")
    with patch.object(sys, "argv", ["lrpcc", "--help"]), pytest.raises(SystemExit):
        lrpcc.run()


def test_run_cli_no_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)  # empty dir — find_config() will raise
    with patch("lrpc.tools.lrpcc.lrpcc.run_lrpcc_config_creator") as mock_creator:
        run_cli()
    mock_creator.assert_called_once()


def test_run_cli_with_config() -> None:
    # change_test_dir autouse fixture puts CWD at tests/lrpcc/ where lrpcc.config.yaml lives
    with patch("lrpc.tools.lrpcc.lrpcc.Lrpcc") as mock_lrpcc:
        run_cli()
    mock_lrpcc.assert_called_once()
    mock_lrpcc.return_value.run.assert_called_once()


def test_version_check_passes() -> None:
    with patch.object(LrpcClient, "check_server_version", return_value=True):
        # version_ok=True → "if not version_ok:" is False → log.info NOT called
        make_lrpcc("../testdata/TestServer1.lrpc.yaml", "", check_server_version=True)


def test_make_transport_spec_is_none(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "lrpcc_badspec.py").write_text("# plugin\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    config = LrpccConfig({"transport_type": "badspec", "definition_from_server": "always"})
    null_spec = patch("importlib.util.spec_from_file_location", return_value=None)
    with null_spec, pytest.raises(ImportError, match="Unable to load transport plugin"):
        Lrpcc._make_transport(config)


def test_make_transport_builtin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    config = LrpccConfig({"transport_type": "fake", "definition_from_server": "always"})

    class FakeTransport:
        def read(self, _count: int) -> bytes:
            return b""

        def write(self, _data: bytes) -> None:
            pass

    fake_module = types.SimpleNamespace(Transport=FakeTransport)

    with patch("lrpc.tools.lrpcc.lrpcc.import_module", return_value=fake_module):
        transport = Lrpcc._make_transport(config)

    assert isinstance(transport, FakeTransport)



def test_run_cli_run_raises() -> None:
    # change_test_dir autouse fixture puts CWD at tests/lrpcc/ where lrpcc.config.yaml lives
    with patch.object(Lrpcc, "run", side_effect=RuntimeError("simulated run failure")):
        run_cli()  # exception is caught and logged; function returns normally
