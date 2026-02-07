from importlib.metadata import version
from io import StringIO

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.meta_constants_writer import MetaConstantsWriter


def test_with_namespace() -> None:
    mock_file = StringIO()
    writer = MetaConstantsWriter(CppFile("test", mock_file))
    writer.write_constants(
        definition_version=None,
        definition_hash=None,
        compressed_definition=b"",
        definition_stream_chunk_size=20,
        namespace="test123",
    )

    lrpc_version = version("lotusrpc")

    expected = (
        """#pragma once
#include <stdint.h>
#include <etl/array.h>
#include <etl/string_view.h>

namespace test123
{
\tnamespace lrpc_meta
\t{
\t\tstatic constexpr etl::string_view DefinitionVersion {};
\t\tstatic constexpr etl::string_view DefinitionHash {};
\t\tstatic constexpr etl::string_view LrpcVersion {"""
        f'"{lrpc_version}"'
        """};
\t\t
\t\tstatic constexpr size_t DefinitionStreamChunkSize {20};
\t\t
\t\tstatic constexpr etl::array<uint8_t, 0> CompressedDefinition =
\t\t{
\t\t\t// Use the 'embed_definition' setting in the definition file to embed the definition in the generated server code
\t\t};
\t}
}
"""
    )

    output = mock_file.getvalue()
    assert output == expected


def test_without_namespace() -> None:
    mock_file = StringIO()
    writer = MetaConstantsWriter(CppFile("test", mock_file))
    writer.write_constants(
        definition_version=None,
        definition_hash=None,
        compressed_definition=b"",
        definition_stream_chunk_size=30,
        namespace=None,
    )

    lrpc_version = version("lotusrpc")

    expected = (
        """#pragma once
#include <stdint.h>
#include <etl/array.h>
#include <etl/string_view.h>

namespace lrpc_meta
{
\tstatic constexpr etl::string_view DefinitionVersion {};
\tstatic constexpr etl::string_view DefinitionHash {};
\tstatic constexpr etl::string_view LrpcVersion {"""
        f'"{lrpc_version}"'
        """};
\t
\tstatic constexpr size_t DefinitionStreamChunkSize {30};
\t
\tstatic constexpr etl::array<uint8_t, 0> CompressedDefinition =
\t{
\t\t// Use the 'embed_definition' setting in the definition file to embed the definition in the generated server code
\t};
}
"""
    )

    output = mock_file.getvalue()
    assert output == expected


def test_with_definition_hash_and_version() -> None:
    mock_file = StringIO()
    writer = MetaConstantsWriter(CppFile("test", mock_file))
    writer.write_constants(
        definition_version="1.2.3.4",
        definition_hash="AABBCCDD",
        compressed_definition=b"",
        definition_stream_chunk_size=20,
        namespace="test123",
    )

    lrpc_version = version("lotusrpc")

    expected = (
        """#pragma once
#include <stdint.h>
#include <etl/array.h>
#include <etl/string_view.h>

namespace test123
{
\tnamespace lrpc_meta
\t{
\t\tstatic constexpr etl::string_view DefinitionVersion {"1.2.3.4"};
\t\tstatic constexpr etl::string_view DefinitionHash {"AABBCCDD"};
\t\tstatic constexpr etl::string_view LrpcVersion {"""
        f'"{lrpc_version}"'
        """};
\t\t
\t\tstatic constexpr size_t DefinitionStreamChunkSize {20};
\t\t
\t\tstatic constexpr etl::array<uint8_t, 0> CompressedDefinition =
\t\t{
\t\t\t// Use the 'embed_definition' setting in the definition file to embed the definition in the generated server code
\t\t};
\t}
}
"""
    )

    output = mock_file.getvalue()
    assert output == expected


def test_without_namespace_with_compressed_definition() -> None:
    mock_file = StringIO()
    compressed_def = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13"
    writer = MetaConstantsWriter(CppFile("test", mock_file))
    writer.write_constants(
        definition_version=None,
        definition_hash=None,
        compressed_definition=compressed_def,
        definition_stream_chunk_size=30,
        namespace=None,
    )

    lrpc_version = version("lotusrpc")

    expected = (
        """#pragma once
#include <stdint.h>
#include <etl/array.h>
#include <etl/string_view.h>

namespace lrpc_meta
{
\tstatic constexpr etl::string_view DefinitionVersion {};
\tstatic constexpr etl::string_view DefinitionHash {};
\tstatic constexpr etl::string_view LrpcVersion {"""
        f'"{lrpc_version}"'
        """};
\t
\tstatic constexpr size_t DefinitionStreamChunkSize {30};
\t
\tstatic constexpr etl::array<uint8_t, 20> CompressedDefinition =
\t{
\t\t0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
\t\t0x10, 0x11, 0x12, 0x13,
\t};
}
"""
    )

    output = mock_file.getvalue()
    assert output == expected
