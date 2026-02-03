from io import StringIO

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.client_stream_shim_writer import ClientStreamShimWriter
from lrpc.core import LrpcStream, LrpcStreamDict


def assert_stream(stream: LrpcStreamDict, expected: str) -> None:
    mock_file = StringIO()
    writer = ClientStreamShimWriter(CppFile("test", mock_file))
    writer.write_shim(LrpcStream(stream))

    assert mock_file.getvalue() == expected


def test_no_params() -> None:
    func: LrpcStreamDict = {"name": "test_stream", "id": 42, "origin": "client"}
    expected = """void test_stream_shim(Reader& r, Writer&)
{
\ttest_stream();
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
    expected = """void test_stream_shim(Reader& r, Writer&)
{
\tconst auto p0 = lrpc::read_unchecked<uint8_t>(r);
\ttest_stream(p0);
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
    expected = """void test_stream_shim(Reader& r, Writer&)
{
\tconst auto p0 = lrpc::read_unchecked<uint8_t>(r);
\tconst auto p1 = lrpc::read_unchecked<bool>(r);
\ttest_stream(p0, p1);
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
    expected = """void test_stream_shim(Reader& r, Writer&)
{
\tetl::array<uint8_t, 25> p0;
\tlrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(r, p0, 25);
\ttest_stream(p0);
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
    expected = """void test_stream_shim(Reader& r, Writer&)
{
\tconst auto p0 = lrpc::read_unchecked<lrpc::tags::string_n>(r, 20);
\ttest_stream(p0);
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
    expected = """void test_stream_shim(Reader& r, Writer&)
{
\tetl::array<etl::string_view, 7> p0;
\tlrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(r, p0, 7, 5);
\ttest_stream(p0);
}
"""

    assert_stream(func, expected)
