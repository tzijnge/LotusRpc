from io import StringIO

from lrpc.codegen.cppfile import CppFile
from lrpc.codegen.server_stream_response_writer import ServerStreamResponseWriter
from lrpc.core import LrpcStream, LrpcStreamDict


def assert_stream(stream: LrpcStreamDict, expected: str) -> None:
    mock_file = StringIO()
    writer = ServerStreamResponseWriter(CppFile.from_writer(mock_file.write))
    writer.write_response(LrpcStream(stream))

    assert mock_file.getvalue() == expected


def test_no_params() -> None:
    func: LrpcStreamDict = {"name": "test_stream", "id": 42, "origin": "server"}
    expected = """void test_stream_response()
{
    server().transmit(id(), 42);
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
    const auto _lrpc_paramWriter = [&p0](Writer &writer)
    {
        lrpc::write_unchecked<uint8_t>(writer, p0);
    };
    server().transmit(id(), 42, _lrpc_paramWriter);
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
    const auto _lrpc_paramWriter = [&p0, &p1](Writer &writer)
    {
        lrpc::write_unchecked<uint8_t>(writer, p0);
        lrpc::write_unchecked<bool>(writer, p1);
    };
    server().transmit(id(), 42, _lrpc_paramWriter);
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
    expected = """void test_stream_response(lrpc::span<const uint8_t> p0)
{
    const auto _lrpc_paramWriter = [&p0](Writer &writer)
    {
        lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, p0, 25);
    };
    server().transmit(id(), 42, _lrpc_paramWriter);
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
    expected = """void test_stream_response(lrpc::string_view p0)
{
    const auto _lrpc_paramWriter = [&p0](Writer &writer)
    {
        lrpc::write_unchecked<lrpc::tags::string_n>(writer, p0, 20);
    };
    server().transmit(id(), 42, _lrpc_paramWriter);
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
    expected = """void test_stream_response(lrpc::span<const lrpc::string_view> p0)
{
    const auto _lrpc_paramWriter = [&p0](Writer &writer)
    {
        lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, p0, 7, 5);
    };
    server().transmit(id(), 42, _lrpc_paramWriter);
}
"""

    assert_stream(func, expected)
