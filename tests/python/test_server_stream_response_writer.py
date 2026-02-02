from io import StringIO

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.server_stream_response_writer import ServerStreamResponseWriter
from lrpc.core import LrpcStream, LrpcStreamDict


def assert_stream(stream: LrpcStreamDict, expected: str) -> None:
    mock_file = StringIO()
    writer = ServerStreamResponseWriter(CppFile("test", mock_file))
    writer.write_response(LrpcStream(stream))

    assert mock_file.getvalue() == expected


def test_no_params() -> None:
    func: LrpcStreamDict = {"name": "test_stream", "id": 42, "origin": "server"}
    expected = """void test_stream_response()
{
\tif (server == nullptr) { return; }
\t
\tauto w = server->getWriter();
\twriteHeader(w, 42);
\tupdateHeader(w);
\tserver->transmit(w);
}
"""

    assert_stream(func, expected)


def test_single_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "server",
        "params": [{"name": "p0", "type": "uint8_t"}],
    }
    expected = """void test_stream_response(uint8_t p0)
{
\tif (server == nullptr) { return; }
\t
\tauto w = server->getWriter();
\twriteHeader(w, 42);
\tlrpc::write_unchecked<uint8_t>(w, p0);
\tupdateHeader(w);
\tserver->transmit(w);
}
"""

    assert_stream(func, expected)


def test_two_params() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "server",
        "params": [{"name": "p0", "type": "uint8_t"}, {"name": "p1", "type": "bool"}],
    }
    expected = """void test_stream_response(uint8_t p0, bool p1)
{
\tif (server == nullptr) { return; }
\t
\tauto w = server->getWriter();
\twriteHeader(w, 42);
\tlrpc::write_unchecked<uint8_t>(w, p0);
\tlrpc::write_unchecked<bool>(w, p1);
\tupdateHeader(w);
\tserver->transmit(w);
}
"""

    assert_stream(func, expected)


def test_array_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "server",
        "params": [{"name": "p0", "type": "uint8_t", "count": 25}],
    }
    expected = """void test_stream_response(etl::span<const uint8_t> p0)
{
\tif (server == nullptr) { return; }
\t
\tauto w = server->getWriter();
\twriteHeader(w, 42);
\tlrpc::write_unchecked<lrpc::array_n<uint8_t>>(w, p0, 25);
\tupdateHeader(w);
\tserver->transmit(w);
}
"""

    assert_stream(func, expected)


def test_string_n_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "server",
        "params": [{"name": "p0", "type": "string_20"}],
    }
    expected = """void test_stream_response(etl::string_view p0)
{
\tif (server == nullptr) { return; }
\t
\tauto w = server->getWriter();
\twriteHeader(w, 42);
\tlrpc::write_unchecked<lrpc::string_n>(w, p0, 20);
\tupdateHeader(w);
\tserver->transmit(w);
}
"""

    assert_stream(func, expected)


def test_array_of_string_n_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "server",
        "params": [{"name": "p0", "type": "string_5", "count": 7}],
    }
    expected = """void test_stream_response(etl::span<const etl::string_view> p0)
{
\tif (server == nullptr) { return; }
\t
\tauto w = server->getWriter();
\twriteHeader(w, 42);
\tlrpc::write_unchecked<lrpc::array_n<lrpc::string_n>>(w, p0, 7, 5);
\tupdateHeader(w);
\tserver->transmit(w);
}
"""

    assert_stream(func, expected)
