import re
import os
import pytest
from lrpc.lrpcc import Lrpcc

# pylint: disable=protected-access


@pytest.fixture(autouse=True)
def change_test_dir(request: pytest.FixtureRequest):  # type: ignore[no-untyped-def]
    os.chdir(request.fspath.dirname)  # type: ignore[attr-defined]
    yield
    os.chdir(request.config.invocation_params.dir)


def escape_ansi(line: str) -> str:
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


def make_lrpcc(definition_url: str, response: bytes = b"") -> Lrpcc:
    lrpcc_config = {
        "definition_url": definition_url,
        "transport_type": "mock",
        "transport_params": {"response": response},
    }
    return Lrpcc(lrpcc_config)


def test_server1_f13(capsys: pytest.CaptureFixture[str]) -> None:
    response = b"\x05\x00\x0d\xcd\xab"
    lrpcc = make_lrpcc("../testdata/TestServer1.lrpc.yaml", response)
    lrpcc._command_handler("s0", "f13")

    expected_response = """a: 43981 (0xabcd)
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


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
    response = b"\x06\x42\x00\xd2\x04\x38"
    response += b"\x06\x42\x00\x0a\x1a\x4d"
    response += b"\x06\x42\x00\xe8\xfd\x03"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    with pytest.raises(TimeoutError) as e:
        lrpcc._command_handler("srv1", "server_infinite", start=True)

    assert str(e.value) == "Timeout waiting for response"

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
    response = b"\x06\x42\x00\xd2\x04\x38"
    response += b"\x06\x42\x00\x0a\x1a\x4d"
    response += b"\x06\x42\x00\xe8\xfd\x03"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    lrpcc._command_handler("srv1", "server_infinite", start=False)

    assert escape_ansi(capsys.readouterr().out) == ""


def test_server_finite_start(capsys: pytest.CaptureFixture[str]) -> None:
    response = b"\x06\x42\x21\x00\x00\x00"
    response += b"\x06\x42\x21\x01\x01\x00"
    response += b"\x06\x42\x21\x00\x01\x01"

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
    response = b"\x06\x42\x21\x00\x00\x00"
    response += b"\x06\x42\x21\x01\x01\x00"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)

    with pytest.raises(TimeoutError) as e:
        lrpcc._command_handler("srv1", "server_finite", start=True)

    assert str(e.value) == "Timeout waiting for response"

    expected_response = """[#0]
p0: False
p1: Open
[#1]
p0: True
p1: Closed
"""
    assert escape_ansi(capsys.readouterr().out) == expected_response


def test_server_finite_stop(capsys: pytest.CaptureFixture[str]) -> None:
    response = b"\x06\x42\x21\x00\x00\x00"
    response += b"\x06\x42\x21\x01\x01\x00"

    lrpcc = make_lrpcc("../testdata/TestServer5.lrpc.yaml", response)
    lrpcc._command_handler("srv1", "server_finite", start=False)

    assert escape_ansi(capsys.readouterr().out) == ""
