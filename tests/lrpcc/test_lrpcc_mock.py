import os
import re
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Literal

import pytest

from lrpc.tools.lrpcc import Lrpcc, LrpccConfig, LrpccConfigDict

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
    meta_version_response = "06ff80000000" if check_server_version else ""

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
    # meta.definition message with definition from TestRetrieveDefinition.lrpc.yaml
    # binary blob is generated in LrpcMeta_constants.hpp after running the definition file
    # through lrpcg
    response = b""
    response += b"\x15\xff\x01\x10\xfd\x37\x7a\x58\x5a\x00\x00\x04\xe6\xd6\xb4\x46\x02\x00\x21\x01\x00"
    response += b"\x15\xff\x01\x10\x16\x00\x00\x00\x74\x2f\xe5\xa3\xe0\x03\x98\x01\x64\x5d\x00\x37\x00"
    response += b"\x15\xff\x01\x10\x18\x49\xfd\xfa\xfb\x56\x60\x9f\xc6\xef\x9a\xb1\x72\x37\x10\x50\x00"
    response += b"\x15\xff\x01\x10\x15\xa2\x39\xaf\xd9\xf5\xfe\x63\x42\x9e\xd9\x48\x31\xe9\x89\x0d\x00"
    response += b"\x15\xff\x01\x10\x78\xe5\x1b\x90\x10\x21\xe8\x03\x62\x22\xf2\x83\x2a\x2b\xed\x7e\x00"
    response += b"\x15\xff\x01\x10\x4a\xad\xf8\x1c\xc4\x22\xda\x9f\xc3\xbc\xb7\xb0\x68\x37\xd5\x1e\x00"
    response += b"\x15\xff\x01\x10\x95\x62\x29\x1b\x5d\x5a\xef\xc2\x07\xdf\x55\x7f\xc6\x1f\x28\x9f\x00"
    response += b"\x15\xff\x01\x10\xbc\xda\x78\x17\x66\x0f\xdb\x8d\xf0\x66\x34\x56\xc6\xc5\x71\x06\x00"
    response += b"\x15\xff\x01\x10\x19\x43\x6c\x4f\x19\x01\x4e\xd2\x80\x87\xe9\xda\xc4\xa4\xc1\xdf\x00"
    response += b"\x15\xff\x01\x10\x29\x0b\x69\xb5\x42\xda\x59\x58\x1b\xb5\xec\x36\x3d\xf9\x92\x6f\x00"
    response += b"\x15\xff\x01\x10\xc8\xd7\x63\x60\xb5\x20\x39\x41\x5e\x8f\x54\x17\x22\x84\xb3\x0d\x00"
    response += b"\x15\xff\x01\x10\x1c\x1e\xe3\x58\x5a\x76\xc2\x0e\x7e\xb2\x8b\x10\xa4\x0c\xc3\x58\x00"
    response += b"\x15\xff\x01\x10\x97\x76\xb5\x43\xc2\x04\xdf\x7a\xda\xd7\xe0\xa3\x74\x71\x39\x56\x00"
    response += b"\x15\xff\x01\x10\xc4\x00\x37\xcc\x59\xdf\x46\xc4\x8e\xda\x6f\x0a\x52\xb5\xe2\xb1\x00"
    response += b"\x15\xff\x01\x10\x2c\xb0\xc9\x0d\xc2\xd7\x68\xdc\x5d\xd4\x8a\xdc\x24\x5f\x4f\x30\x00"
    response += b"\x15\xff\x01\x10\x85\x78\x7b\xd9\x9d\x58\x93\xfa\x23\x81\x90\xe7\xda\x45\xf7\xdf\x00"
    response += b"\x15\xff\x01\x10\x52\x31\x20\x04\xda\x1a\x08\x03\x16\xcb\x60\x8e\xec\xce\x8e\x54\x00"
    response += b"\x15\xff\x01\x10\xb6\x21\xd3\xd0\x7b\xc4\x8b\xbc\xbf\xb6\x3b\x6e\x03\xd7\x89\x75\x00"
    response += b"\x15\xff\x01\x10\xec\x13\xe5\xc1\x68\xd9\xe0\x27\xe4\x83\x2f\x3d\x1c\x2d\xe0\x41\x00"
    response += b"\x15\xff\x01\x10\x06\x3e\xbd\xa9\xf6\xd7\x35\x2a\x50\xa7\x2c\x97\x7d\x27\xb5\x1d\x00"
    response += b"\x15\xff\x01\x10\xd2\x11\xe0\x8a\xa2\xc6\xf9\x88\x33\xaf\x1a\xcd\xba\x4d\x5e\x3c\x00"
    response += b"\x15\xff\x01\x10\x05\x81\x6e\x43\x64\x8a\x6e\xb9\xed\x9b\x37\x1e\xdc\x20\xd1\x3f\x00"
    response += b"\x15\xff\x01\x10\x99\x89\xf1\x35\x7a\x99\x44\x65\x05\x84\xeb\x46\xbd\xa3\xbf\x08\x00"
    response += b"\x15\xff\x01\x10\x8a\xb3\x6c\x41\x48\x1d\xc3\x4d\x6e\x89\x7b\xdf\xc4\x3a\xca\xec\x00"
    response += b"\x15\xff\x01\x10\x51\x6b\x00\x00\x81\xd8\x95\x64\xb5\x6d\x99\x56\x00\x01\x80\x03\x00"
    response += b"\x15\xff\x01\x10\x99\x07\x00\x00\x7e\x02\x42\x5f\xb1\xc4\x67\xfb\x02\x00\x00\x00\x00"
    response += b"\x09\xff\x01\x04\x00\x04\x59\x5a\x01"
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
    # meta.definition message with definition from TestRetrieveDefinition.lrpc.yaml
    # binary blob is generated in LrpcMeta_constants.hpp after running the definition file
    # through lrpcg
    response = b""
    response += b"\x15\xff\x01\x10\xfd\x37\x7a\x58\x5a\x00\x00\x04\xe6\xd6\xb4\x46\x02\x00\x21\x01\x00"
    response += b"\x15\xff\x01\x10\x16\x00\x00\x00\x74\x2f\xe5\xa3\xe0\x03\x98\x01\x64\x5d\x00\x37\x00"
    response += b"\x15\xff\x01\x10\x18\x49\xfd\xfa\xfb\x56\x60\x9f\xc6\xef\x9a\xb1\x72\x37\x10\x50\x00"
    response += b"\x15\xff\x01\x10\x15\xa2\x39\xaf\xd9\xf5\xfe\x63\x42\x9e\xd9\x48\x31\xe9\x89\x0d\x00"
    response += b"\x15\xff\x01\x10\x78\xe5\x1b\x90\x10\x21\xe8\x03\x62\x22\xf2\x83\x2a\x2b\xed\x7e\x00"
    response += b"\x15\xff\x01\x10\x4a\xad\xf8\x1c\xc4\x22\xda\x9f\xc3\xbc\xb7\xb0\x68\x37\xd5\x1e\x00"
    response += b"\x15\xff\x01\x10\x95\x62\x29\x1b\x5d\x5a\xef\xc2\x07\xdf\x55\x7f\xc6\x1f\x28\x9f\x00"
    response += b"\x15\xff\x01\x10\xbc\xda\x78\x17\x66\x0f\xdb\x8d\xf0\x66\x34\x56\xc6\xc5\x71\x06\x00"
    response += b"\x15\xff\x01\x10\x19\x43\x6c\x4f\x19\x01\x4e\xd2\x80\x87\xe9\xda\xc4\xa4\xc1\xdf\x00"
    response += b"\x15\xff\x01\x10\x29\x0b\x69\xb5\x42\xda\x59\x58\x1b\xb5\xec\x36\x3d\xf9\x92\x6f\x00"
    response += b"\x15\xff\x01\x10\xc8\xd7\x63\x60\xb5\x20\x39\x41\x5e\x8f\x54\x17\x22\x84\xb3\x0d\x00"
    response += b"\x15\xff\x01\x10\x1c\x1e\xe3\x58\x5a\x76\xc2\x0e\x7e\xb2\x8b\x10\xa4\x0c\xc3\x58\x00"
    response += b"\x15\xff\x01\x10\x97\x76\xb5\x43\xc2\x04\xdf\x7a\xda\xd7\xe0\xa3\x74\x71\x39\x56\x00"
    response += b"\x15\xff\x01\x10\xc4\x00\x37\xcc\x59\xdf\x46\xc4\x8e\xda\x6f\x0a\x52\xb5\xe2\xb1\x00"
    response += b"\x15\xff\x01\x10\x2c\xb0\xc9\x0d\xc2\xd7\x68\xdc\x5d\xd4\x8a\xdc\x24\x5f\x4f\x30\x00"
    response += b"\x15\xff\x01\x10\x85\x78\x7b\xd9\x9d\x58\x93\xfa\x23\x81\x90\xe7\xda\x45\xf7\xdf\x00"
    response += b"\x15\xff\x01\x10\x52\x31\x20\x04\xda\x1a\x08\x03\x16\xcb\x60\x8e\xec\xce\x8e\x54\x00"
    response += b"\x15\xff\x01\x10\xb6\x21\xd3\xd0\x7b\xc4\x8b\xbc\xbf\xb6\x3b\x6e\x03\xd7\x89\x75\x00"
    response += b"\x15\xff\x01\x10\xec\x13\xe5\xc1\x68\xd9\xe0\x27\xe4\x83\x2f\x3d\x1c\x2d\xe0\x41\x00"
    response += b"\x15\xff\x01\x10\x06\x3e\xbd\xa9\xf6\xd7\x35\x2a\x50\xa7\x2c\x97\x7d\x27\xb5\x1d\x00"
    response += b"\x15\xff\x01\x10\xd2\x11\xe0\x8a\xa2\xc6\xf9\x88\x33\xaf\x1a\xcd\xba\x4d\x5e\x3c\x00"
    response += b"\x15\xff\x01\x10\x05\x81\x6e\x43\x64\x8a\x6e\xb9\xed\x9b\x37\x1e\xdc\x20\xd1\x3f\x00"
    response += b"\x15\xff\x01\x10\x99\x89\xf1\x35\x7a\x99\x44\x65\x05\x84\xeb\x46\xbd\xa3\xbf\x08\x00"
    response += b"\x15\xff\x01\x10\x8a\xb3\x6c\x41\x48\x1d\xc3\x4d\x6e\x89\x7b\xdf\xc4\x3a\xca\xec\x00"
    response += b"\x15\xff\x01\x10\x51\x6b\x00\x00\x81\xd8\x95\x64\xb5\x6d\x99\x56\x00\x01\x80\x03\x00"
    response += b"\x15\xff\x01\x10\x99\x07\x00\x00\x7e\x02\x42\x5f\xb1\xc4\x67\xfb\x02\x00\x00\x00\x00"
    response += b"\x09\xff\x01\x04\x00\x04\x59\x5a\x01"
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


def test_definition_from_server_when_server_has_no_embedded_definition(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(ValueError, match="No embedded definition found on server"):
        make_lrpcc("", "05ff010001", check_server_version=False, definition_from_server="always")
