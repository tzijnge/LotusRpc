import tempfile
from importlib.metadata import version
from io import StringIO
from pathlib import Path

import pytest

from lrpc.codegen.byte_types_file_writer import ByteTypesFileWriter, write_byte_types_file
from lrpc.codegen.cppfile import CppFile


def _write(byte_type: str) -> str:
    mock_file = StringIO()
    ByteTypesFileWriter(CppFile.from_writer(mock_file.write), byte_type).write()
    return mock_file.getvalue()


def test_uint8_t() -> None:
    expected = """\
#pragma once

#include <cstdint>

#include "LrpcTypes.hpp"

namespace lrpc
{
    using byte = uint8_t;
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;
}
"""
    assert _write("uint8_t") == expected


def test_int8_t() -> None:
    expected = """\
#pragma once

#include <cstdint>

#include "LrpcTypes.hpp"

namespace lrpc
{
    using byte = int8_t;
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;
}
"""
    assert _write("int8_t") == expected


def test_etl_byte() -> None:
    expected = """\
#pragma once

#include <etl/byte.h>

#include "LrpcTypes.hpp"

namespace lrpc
{
    using byte = etl::byte;
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;
}
"""
    assert _write("etl::byte") == expected


def test_std_byte() -> None:
    expected = """\
#pragma once

#include <cstddef>

#include "LrpcTypes.hpp"

namespace lrpc
{
    using byte = std::byte;
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;
}
"""
    assert _write("std::byte") == expected


@pytest.mark.parametrize("byte_type", ["char", "char8_t", "unsigned char", "signed char"])
def test_char_types_have_no_extra_include(byte_type: str) -> None:
    expected = f"""\
#pragma once

#include "LrpcTypes.hpp"

namespace lrpc
{{
    using byte = {byte_type};
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;
}}
"""
    assert _write(byte_type) == expected


def test_write_byte_types_file() -> None:
    v = version("lotusrpc")
    with tempfile.TemporaryDirectory() as temp_dir:
        write_byte_types_file(Path(temp_dir), "uint8_t")
        output = Path(temp_dir).joinpath("LrpcByteTypes.hpp").read_text(encoding="utf-8")

    expected = f"""\
// This file has been generated with LRPC version {v}

#pragma once

#include <cstdint>

#include "LrpcTypes.hpp"

namespace lrpc
{{
    using byte = uint8_t;
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;
}}
"""
    assert output == expected
