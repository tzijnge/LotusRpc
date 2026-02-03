from io import StringIO

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.function_shim_writer import FunctionShimWriter
from lrpc.core import LrpcFun, LrpcFunDict


def assert_func(func: LrpcFunDict, expected: str) -> None:
    mock_file = StringIO()
    writer = FunctionShimWriter(CppFile("test", mock_file))
    writer.write_function_shim(LrpcFun(func))

    assert mock_file.getvalue() == expected


def test_no_params_no_returns() -> None:
    func: LrpcFunDict = {"name": "test_func", "id": 42}
    expected = """void test_func_shim(Reader&, Writer& w)
{
\twriteHeader(w, 42);
\ttest_func();
}
"""

    assert_func(func, expected)


def test_single_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "a", "type": "uint8_t"}],
    }
    expected = """void test_func_shim(Reader& r, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto a = lrpc::read_unchecked<uint8_t>(r);
\ttest_func(a);
}
"""

    assert_func(func, expected)


def test_two_params() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [
            {"name": "a", "type": "uint8_t"},
            {"name": "b", "type": "uint16_t"},
        ],
    }
    expected = """void test_func_shim(Reader& r, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto a = lrpc::read_unchecked<uint8_t>(r);
\tconst auto b = lrpc::read_unchecked<uint16_t>(r);
\ttest_func(a, b);
}
"""

    assert_func(func, expected)


def test_single_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "a", "type": "uint8_t"}],
    }
    expected = """void test_func_shim(Reader&, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto response = test_func();
\tlrpc::write_unchecked<uint8_t>(w, response);
}
"""

    assert_func(func, expected)


def test_two_returns() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [
            {"name": "a", "type": "uint8_t"},
            {"name": "b", "type": "uint16_t"},
        ],
    }
    expected = """void test_func_shim(Reader&, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto response = test_func();
\tlrpc::write_unchecked<uint8_t>(w, std::get<0>(response));
\tlrpc::write_unchecked<uint16_t>(w, std::get<1>(response));
}
"""

    assert_func(func, expected)


def test_array_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "uint8_t", "count": 2}],
    }
    expected = """void test_func_shim(Reader& r, Writer& w)
{
\twriteHeader(w, 43);
\tetl::array<uint8_t, 2> x;
\tlrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(r, x, 2);
\ttest_func(x);
}
"""

    assert_func(func, expected)


def test_fixed_size_string_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "string_2"}],
    }
    expected = """void test_func_shim(Reader& r, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto x = lrpc::read_unchecked<lrpc::tags::string_n>(r, 2);
\ttest_func(x);
}
"""

    assert_func(func, expected)


def test_array_of_fixed_size_string_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "string_2", "count": 3}],
    }
    expected = """void test_func_shim(Reader& r, Writer& w)
{
\twriteHeader(w, 43);
\tetl::array<etl::string_view, 3> x;
\tlrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(r, x, 3, 2);
\ttest_func(x);
}
"""

    assert_func(func, expected)


def test_array_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "uint8_t", "count": 2}],
    }
    expected = """void test_func_shim(Reader&, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto response = test_func();
\tlrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(w, response, 2);
}
"""

    assert_func(func, expected)


def test_fixed_size_string_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "string_2"}],
    }
    expected = """void test_func_shim(Reader&, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto response = test_func();
\tlrpc::write_unchecked<lrpc::tags::string_n>(w, response, 2);
}
"""

    assert_func(func, expected)


def test_array_of_fixed_size_string_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "string_2", "count": 3}],
    }
    expected = """void test_func_shim(Reader&, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto response = test_func();
\tlrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(w, response, 3, 2);
}
"""

    assert_func(func, expected)


def test_many_params_and_returns() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [
            {"name": "p0", "type": "uint8_t"},
            {"name": "p1", "type": "uint8_t", "count": 2},
            {"name": "p2", "type": "string_10", "count": 3},
        ],
        "returns": [
            {"name": "r0", "type": "uint8_t"},
            {"name": "r1", "type": "uint8_t", "count": 4},
            {"name": "r2", "type": "string_20", "count": 5},
        ],
    }
    expected = """void test_func_shim(Reader& r, Writer& w)
{
\twriteHeader(w, 43);
\tconst auto p0 = lrpc::read_unchecked<uint8_t>(r);
\tetl::array<uint8_t, 2> p1;
\tlrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(r, p1, 2);
\tetl::array<etl::string_view, 3> p2;
\tlrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(r, p2, 3, 10);
\tconst auto response = test_func(p0, p1, p2);
\tlrpc::write_unchecked<uint8_t>(w, std::get<0>(response));
\tlrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(w, std::get<1>(response), 4);
\tlrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(w, std::get<2>(response), 5, 20);
}
"""

    assert_func(func, expected)
