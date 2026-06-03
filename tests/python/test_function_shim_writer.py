from io import StringIO

from lrpc.codegen.cppfile import CppFile
from lrpc.codegen.function_shim_writer import FunctionShimWriter
from lrpc.core import LrpcFun, LrpcFunDict


def assert_func(func: LrpcFunDict, expected: str) -> None:
    mock_file = StringIO()
    writer = FunctionShimWriter(CppFile.from_writer(mock_file.write))
    writer.write_function_shim(LrpcFun(func))

    assert mock_file.getvalue() == expected


def test_no_params_no_returns() -> None:
    func: LrpcFunDict = {"name": "test_func", "id": 42}
    expected = """void test_func_shim(Reader& /*reader*/)
{
    test_func();
    server().transmit(id(), 42);
}
"""

    assert_func(func, expected)


def test_single_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "a", "type": "uint8_t"}],
    }
    expected = """void test_func_shim(Reader& reader)
{
    const auto a = lrpc::read_unchecked<uint8_t>(reader);
    test_func(a);
    server().transmit(id(), 43);
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
    expected = """void test_func_shim(Reader& reader)
{
    const auto a = lrpc::read_unchecked<uint8_t>(reader);
    const auto b = lrpc::read_unchecked<uint16_t>(reader);
    test_func(a, b);
    server().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_single_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "a", "type": "uint8_t"}],
    }
    expected = """void test_func_shim(Reader& /*reader*/)
{
    const auto a = test_func();
    const auto _lrpc_paramWriter = [&a](Writer &writer)
    {
        lrpc::write_unchecked<uint8_t>(writer, a);
    };
    server().transmit(id(), 43, _lrpc_paramWriter);
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
    expected = """void test_func_shim(Reader& /*reader*/)
{
    const auto a_b = test_func();
    const auto _lrpc_paramWriter = [&a_b](Writer &writer)
    {
        lrpc::write_unchecked<uint8_t>(writer, std::get<0>(a_b));
        lrpc::write_unchecked<uint16_t>(writer, std::get<1>(a_b));
    };
    server().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)


def test_array_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "uint8_t", "count": 2}],
    }
    expected = """void test_func_shim(Reader& reader)
{
    lrpc::array<uint8_t, 2> x;
    lrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, x, 2);
    test_func(x);
    server().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_fixed_size_string_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "string_2"}],
    }
    expected = """void test_func_shim(Reader& reader)
{
    const auto x = lrpc::read_unchecked<lrpc::tags::string_n>(reader, 2);
    test_func(x);
    server().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_array_of_fixed_size_string_param() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "params": [{"name": "x", "type": "string_2", "count": 3}],
    }
    expected = """void test_func_shim(Reader& reader)
{
    lrpc::array<lrpc::string_view, 3> x;
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, x, 3, 2);
    test_func(x);
    server().transmit(id(), 43);
}
"""

    assert_func(func, expected)


def test_array_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "uint8_t", "count": 2}],
    }
    expected = """void test_func_shim(Reader& /*reader*/)
{
    const auto x = test_func();
    const auto _lrpc_paramWriter = [&x](Writer &writer)
    {
        lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, x, 2);
    };
    server().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)


def test_fixed_size_string_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "string_2"}],
    }
    expected = """void test_func_shim(Reader& /*reader*/)
{
    const auto x = test_func();
    const auto _lrpc_paramWriter = [&x](Writer &writer)
    {
        lrpc::write_unchecked<lrpc::tags::string_n>(writer, x, 2);
    };
    server().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)


def test_array_of_fixed_size_string_return() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 43,
        "returns": [{"name": "x", "type": "string_2", "count": 3}],
    }
    expected = """void test_func_shim(Reader& /*reader*/)
{
    const auto x = test_func();
    const auto _lrpc_paramWriter = [&x](Writer &writer)
    {
        lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, x, 3, 2);
    };
    server().transmit(id(), 43, _lrpc_paramWriter);
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
    expected = """void test_func_shim(Reader& reader)
{
    const auto p0 = lrpc::read_unchecked<uint8_t>(reader);
    lrpc::array<uint8_t, 2> p1;
    lrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, p1, 2);
    lrpc::array<lrpc::string_view, 3> p2;
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, p2, 3, 10);
    const auto r0_r1_r2 = test_func(p0, p1, p2);
    const auto _lrpc_paramWriter = [&r0_r1_r2](Writer &writer)
    {
        lrpc::write_unchecked<uint8_t>(writer, std::get<0>(r0_r1_r2));
        lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, std::get<1>(r0_r1_r2), 4);
        lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, std::get<2>(r0_r1_r2), 5, 20);
    };
    server().transmit(id(), 43, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)


def test_returns_alias() -> None:
    func: LrpcFunDict = {
        "name": "test_func",
        "id": 250,
        "returns": [
            {"name": "a", "type": "uint8_t"},
            {"name": "b", "type": "uint16_t"},
        ],
        "returns_alias": "a_and_b",
    }
    expected = """void test_func_shim(Reader& /*reader*/)
{
    const auto _a_and_b = test_func();
    const auto _lrpc_paramWriter = [&_a_and_b](Writer &writer)
    {
        lrpc::write_unchecked<uint8_t>(writer, std::get<0>(_a_and_b));
        lrpc::write_unchecked<uint16_t>(writer, std::get<1>(_a_and_b));
    };
    server().transmit(id(), 250, _lrpc_paramWriter);
}
"""

    assert_func(func, expected)
