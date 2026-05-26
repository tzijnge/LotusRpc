from io import StringIO

from lrpc.codegen.client_stream_shim_writer import ClientStreamShimWriter
from lrpc.codegen.cppfile import CppFile
from lrpc.core import LrpcStream, LrpcStreamDict


def assert_stream(stream: LrpcStreamDict, expected: str) -> None:
    mock_file = StringIO()
    writer = ClientStreamShimWriter(CppFile("test", mock_file))
    writer.write_shim(LrpcStream(stream))

    assert mock_file.getvalue() == expected


def test_no_params() -> None:
    func: LrpcStreamDict = {"name": "test_stream", "id": 42, "origin": "client"}
    expected = """void test_stream_shim(Reader& reader)
{
    test_stream();
}
"""

    assert_stream(func, expected)


def test_single_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "client",
        "params": [{"name": "p0", "type": "uint8_t"}],
    }
    expected = """void test_stream_shim(Reader& reader)
{
    const auto p0 = lrpc::read_unchecked<uint8_t>(reader);
    test_stream(p0);
}
"""

    assert_stream(func, expected)


def test_two_params() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "client",
        "params": [{"name": "p0", "type": "uint8_t"}, {"name": "p1", "type": "bool"}],
    }
    expected = """void test_stream_shim(Reader& reader)
{
    const auto p0 = lrpc::read_unchecked<uint8_t>(reader);
    const auto p1 = lrpc::read_unchecked<bool>(reader);
    test_stream(p0, p1);
}
"""

    assert_stream(func, expected)


def test_array_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "client",
        "params": [{"name": "p0", "type": "uint8_t", "count": 25}],
    }
    expected = """void test_stream_shim(Reader& reader)
{
    lrpc::array<uint8_t, 25> p0;
    lrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, p0, 25);
    test_stream(p0);
}
"""

    assert_stream(func, expected)


def test_string_n_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "client",
        "params": [{"name": "p0", "type": "string_20"}],
    }
    expected = """void test_stream_shim(Reader& reader)
{
    const auto p0 = lrpc::read_unchecked<lrpc::tags::string_n>(reader, 20);
    test_stream(p0);
}
"""

    assert_stream(func, expected)


def test_array_of_string_n_param() -> None:
    func: LrpcStreamDict = {
        "name": "test_stream",
        "id": 42,
        "origin": "client",
        "params": [{"name": "p0", "type": "string_5", "count": 7}],
    }
    expected = """void test_stream_shim(Reader& reader)
{
    lrpc::array<lrpc::string_view, 7> p0;
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, p0, 7, 5);
    test_stream(p0);
}
"""

    assert_stream(func, expected)
