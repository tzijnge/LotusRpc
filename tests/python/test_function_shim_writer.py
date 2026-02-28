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
    expected = """void test_func_shim(Reader&)
{
\ttest_func();
\tserver().transmit(id(), 42);
}
"""

    assert_func(func, expected)


def test_single_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "a", "type": "uint8_t"}],
    }
    expected = """void test_func_shim(Reader& r)
{
\tconst auto a = lrpc::read_unchecked<uint8_t>(r);
\ttest_func(a);
\tserver().transmit(id(), 43);
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
    expected = """void test_func_shim(Reader& r)
{
\tconst auto a = lrpc::read_unchecked<uint8_t>(r);
\tconst auto b = lrpc::read_unchecked<uint16_t>(r);
\ttest_func(a, b);
\tserver().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_single_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "a", "type": "uint8_t"}],
    }
    expected = """void test_func_shim(Reader&)
{
\tconst auto a = test_func();
\tconst auto _lrpc_paramWriter = [&a](Writer &w)
\t{
\t\tlrpc::write_unchecked<uint8_t>(w, a);
\t};
\tserver().transmit(id(), 43, _lrpc_paramWriter);
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
    expected = """void test_func_shim(Reader&)
{
\tconst auto a_b = test_func();
\tconst auto _lrpc_paramWriter = [&a_b](Writer &w)
\t{
\t\tlrpc::write_unchecked<uint8_t>(w, std::get<0>(a_b));
\t\tlrpc::write_unchecked<uint16_t>(w, std::get<1>(a_b));
\t};
\tserver().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)


def test_array_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "uint8_t", "count": 2}],
    }
    expected = """void test_func_shim(Reader& r)
{
\tetl::array<uint8_t, 2> x;
\tlrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(r, x, 2);
\ttest_func(x);
\tserver().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_fixed_size_string_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "string_2"}],
    }
    expected = """void test_func_shim(Reader& r)
{
\tconst auto x = lrpc::read_unchecked<lrpc::tags::string_n>(r, 2);
\ttest_func(x);
\tserver().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_array_of_fixed_size_string_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "string_2", "count": 3}],
    }
    expected = """void test_func_shim(Reader& r)
{
\tetl::array<etl::string_view, 3> x;
\tlrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(r, x, 3, 2);
\ttest_func(x);
\tserver().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_array_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "uint8_t", "count": 2}],
    }
    expected = """void test_func_shim(Reader&)
{
\tconst auto x = test_func();
\tconst auto _lrpc_paramWriter = [&x](Writer &w)
\t{
\t\tlrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(w, x, 2);
\t};
\tserver().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)


def test_fixed_size_string_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "string_2"}],
    }
    expected = """void test_func_shim(Reader&)
{
\tconst auto x = test_func();
\tconst auto _lrpc_paramWriter = [&x](Writer &w)
\t{
\t\tlrpc::write_unchecked<lrpc::tags::string_n>(w, x, 2);
\t};
\tserver().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)


def test_array_of_fixed_size_string_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "string_2", "count": 3}],
    }
    expected = """void test_func_shim(Reader&)
{
\tconst auto x = test_func();
\tconst auto _lrpc_paramWriter = [&x](Writer &w)
\t{
\t\tlrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(w, x, 3, 2);
\t};
\tserver().transmit(id(), 43, _lrpc_paramWriter);
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
    expected = """void test_func_shim(Reader& r)
{
\tconst auto p0 = lrpc::read_unchecked<uint8_t>(r);
\tetl::array<uint8_t, 2> p1;
\tlrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(r, p1, 2);
\tetl::array<etl::string_view, 3> p2;
\tlrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(r, p2, 3, 10);
\tconst auto r0_r1_r2 = test_func(p0, p1, p2);
\tconst auto _lrpc_paramWriter = [&r0_r1_r2](Writer &w)
\t{
\t\tlrpc::write_unchecked<uint8_t>(w, std::get<0>(r0_r1_r2));
\t\tlrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(w, std::get<1>(r0_r1_r2), 4);
\t\tlrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(w, std::get<2>(r0_r1_r2), 5, 20);
\t};
\tserver().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)
