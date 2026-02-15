import os
import re
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Literal

import pytest

from lrpc.tools.lrpcc import Lrpcc, LrpccConfig, LrpccConfigDict
from tests.embedded_definition import embedded_definition_for_testing

# pylint: disable=protected-access
# ruff: noqa: SLF001


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    os.chdir(request.fspath.dirname)  # type: ignore[attr-defined]
    yield
    os.chdir(request.config.invocation_params.dir)


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
    meta_version_response = "06ff02000000" if check_server_version else ""

    lrpcc_config: LrpccConfigDict = {
        "definition_url": definition_url,
        "transport_type": "mock",
        "transport_params": {"response": meta_version_response + response},
        "check_server_version": check_server_version,
        "definition_from_server": definition_from_server,
    }
    return Lrpcc(LrpccConfig(lrpcc_config))


def test_server1_f13(capsys: pytest.CaptureFixture[str]) -> None:
    response = "05000dcdab"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("s0", "f13")

    expected_response = """a: 43981 (0xabcd)
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server1_f13_with_version_check(capsys: pytest.CaptureFixture[str]) -> None:
    response = "05000dcdab"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=True)
    lrpcc._command_handler("s0", "f13")

    expected_response = """a: 43981 (0xabcd)
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server1_f29(capsys: pytest.CaptureFixture[str]) -> None:
    response = "07001d03334455"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("s0", "f29", p0=b"\x77\x88\x99")

    expected_response = """r0: [33 44 55]
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server1_f30(capsys: pytest.CaptureFixture[str]) -> None:
    response = "03001e"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("s0", "f30", p0=[b"\x33\x44", b"\x55\x66"])

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server1_stream0(capsys: pytest.CaptureFixture[str]) -> None:
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", check_server_version=False)
    lrpcc._command_handler("s0", "stream0", p0=b"\x77\x88\x99", final=False)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server1_stream0_final(capsys: pytest.CaptureFixture[str]) -> None:
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", check_server_version=False)
    lrpcc._command_handler("s0", "stream0", p0=b"\x77\x88\x99", final=True)

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
    response = "064200d20438"
    response += "0642000a1a4d"
    response += "064200e8fd03"

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
    response = "064200d20438"
    response += "0642000a1a4d"
    response += "064200e8fd03"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    lrpcc._command_handler("srv1", "server_infinite", start=False)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server_finite_start(capsys: pytest.CaptureFixture[str]) -> None:
    response = "064221000000"
    response += "064221010100"
    response += "064221000101"

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
    response = "064221000000"
    response += "064221010100"

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
    response = "064221000000"
    response += "064221010100"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    lrpcc._command_handler("srv1", "server_finite", start=False)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_error_response_unknown_service(capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture) -> None:
    response = "0bff000044550000000000"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("s0", "f13")

    expected_log = "Server reported error 'UnknownService' for call to s0.f13"
    expected_print = "Server reported call to unknown service with ID 68. Function or stream ID is 85"

    assert len(caplog.messages) == 1
    assert caplog.messages[0] == expected_log
    assert escape_ansi(capsys.readouterr().out.strip()) == expected_print


def test_error_response_unknown_function_or_stream(
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    response = "0bff000144550000000000"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response, check_server_version=False)
    lrpcc._command_handler("s0", "f13")

    expected_log = "Server reported error 'UnknownFunctionOrStream' for call to s0.f13"
    expected_print = "Server reported call to unknown function or stream with ID 85 in service with ID 68"

    assert len(caplog.messages) == 1
    assert caplog.messages[0] == expected_log
    assert escape_ansi(capsys.readouterr().out.strip()) == expected_print


def test_definition_from_server_always(capsys: pytest.CaptureFixture[str]) -> None:
    response = embedded_definition_for_testing()
    # actual response to s0.f0
    response += b"\x03\x00\x00"

    lrpcc = make_lrpcc(
        "",
        response.hex(),
        check_server_version=False,
        definition_from_server="always",
    )
    lrpcc._command_handler("s0", "f0")

    assert escape_ansi(capsys.readouterr().out) == ""


def test_definition_from_server_once(capsys: pytest.CaptureFixture[str]) -> None:
    response = embedded_definition_for_testing()
    # actual response to s0.f0. Times 2 to make sure s0.f0 can be called again without retrieving the
    # embedded definition again
    response += b"\x03\x00\x00"
    response += b"\x03\x00\x00"

    with tempfile.TemporaryDirectory() as temp_dir:
        definition_file = Path(temp_dir).joinpath("test_definition_from_server_once.lrpc.yaml")
        assert not definition_file.exists()

        lrpcc = make_lrpcc(
            str(definition_file),
            response.hex(),
            check_server_version=False,
            definition_from_server="once",
        )
        lrpcc._command_handler("s0", "f0")
        assert definition_file.exists()

        lrpcc._command_handler("s0", "f0")

        assert escape_ansi(capsys.readouterr().out) == ""


def test_definition_from_server_when_server_has_no_embedded_definition() -> None:
    with pytest.raises(ValueError, match="No embedded definition found on server"):
        make_lrpcc("", "05ff010001", check_server_version=False, definition_from_server="always")
