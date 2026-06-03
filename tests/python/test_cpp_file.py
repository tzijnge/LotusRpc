import tempfile
from io import StringIO
from pathlib import Path

import pytest

from lrpc.codegen.cppfile import CppFile


def make_cpp_file(indent: int = 4) -> tuple[CppFile, StringIO]:
    stream = StringIO()
    return CppFile.from_writer(stream.write, indent=indent), stream


def test_negative_indent_raises() -> None:
    with pytest.raises(ValueError, match="indent must be non-negative, got -1"):
        CppFile.from_writer(StringIO().write, indent=-1)


def test_zero_indent_is_valid() -> None:
    f, stream = make_cpp_file(indent=0)
    f.write("x")
    assert stream.getvalue() == "x\n"


def test_custom_indent() -> None:
    f, stream = make_cpp_file(indent=2)
    with f.block("ns"):
        f.write("x")
    assert stream.getvalue() == """\
ns
{
  x
}
"""


def test_write_non_empty() -> None:
    f, stream = make_cpp_file()
    f.write("hello")
    assert stream.getvalue() == "hello\n"


def test_write_empty_string_produces_no_indent() -> None:
    f, stream = make_cpp_file()
    with f.block("ns"):
        f.write("")
    assert stream.getvalue() == """\
ns
{

}
"""


def test_call_delegates_to_write() -> None:
    f, stream = make_cpp_file()
    f("hello")
    assert stream.getvalue() == "hello\n"


def test_newline() -> None:
    f, stream = make_cpp_file()
    f.newline()
    assert stream.getvalue() == "\n"


def test_pragma_once() -> None:
    f, stream = make_cpp_file()
    f.pragma_once()
    assert stream.getvalue() == "#pragma once\n"


def test_include_without_export() -> None:
    f, stream = make_cpp_file()
    f.include('"foo.hpp"')
    assert stream.getvalue() == '#include "foo.hpp"\n'


def test_include_with_iwyu_export() -> None:
    f, stream = make_cpp_file()
    f.include('"foo.hpp"', iwyu_export=True)
    assert stream.getvalue() == '#include "foo.hpp" // IWYU pragma: export\n'


def test_label() -> None:
    f, stream = make_cpp_file()
    with f.block("switch (x)"):
        f.label("case 1")
        f.write("break;")
    assert stream.getvalue() == """\
switch (x)
{
case 1:
    break;
}
"""


def test_block_basic() -> None:
    f, stream = make_cpp_file()
    with f.block("namespace foo"):
        f.write("int x;")
    assert stream.getvalue() == """\
namespace foo
{
    int x;
}
"""


def test_block_with_postfix() -> None:
    f, stream = make_cpp_file()
    with f.block("struct Foo", ";"):
        f.write("int x;")
    assert stream.getvalue() == """\
struct Foo
{
    int x;
};
"""


def test_block_with_trailing_newline() -> None:
    f, stream = make_cpp_file()
    with f.block("namespace foo", trailing_newline=True):
        f.write("int x;")
    assert stream.getvalue() == """\
namespace foo
{
    int x;
}

"""


def test_block_nested() -> None:
    f, stream = make_cpp_file()
    with f.block("namespace foo"), f.block("struct Bar", ";"):
        f.write("int x;")
    assert stream.getvalue() == """\
namespace foo
{
    struct Bar
    {
        int x;
    };
}
"""


def test_enter_returns_self() -> None:
    f, _ = make_cpp_file()
    assert f.__enter__() is f


def test_context_manager_closes_owned_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.hpp"
        with CppFile(str(path)) as f:
            f.write("hello")
        assert path.read_text(encoding="utf-8") == "hello\n"


def test_context_manager_does_not_close_stream() -> None:
    stream = StringIO()
    with CppFile.from_writer(stream.write) as f:
        f.write("hello")
    assert not stream.closed
