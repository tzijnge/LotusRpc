from io import StringIO

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.meta_service_file_writer import MetaServiceFileWriter


def test_without_namespace() -> None:
    mock_file = StringIO()
    writer = MetaServiceFileWriter(CppFile("test", mock_file))
    writer.write_service(None)

    expected = """#pragma once
#include "LrpcMeta_shim.hpp"
#include "LrpcMeta_constants.hpp"

class LrpcMeta_service : public LrpcMeta_shim
{
public:
\tvoid error() override {}
\tvoid error_stop() override {}

\tvoid definition() override
\t{
\t\tetl::span<const uint8_t> data{lrpc_meta::CompressedDefinition};

\t\tbool final{false};
\t\twhile (!final)
\t\t{
\t\t\tconst auto transmitSize = etl::min<size_t>(data.size(), lrpc_meta::DefinitionStreamChunkSize);
\t\t\tfinal = (transmitSize != lrpc_meta::DefinitionStreamChunkSize) ||
\t\t\t\t\t(data.size() == lrpc_meta::DefinitionStreamChunkSize);

\t\t\tdefinition_response(data.take<const LRPC_BYTE_TYPE>(transmitSize), final);
\t\t}
\t}
\tvoid definition_stop() override {}

\tstd::tuple<etl::string_view, etl::string_view, etl::string_view> version() override
\t{
\t\treturn {
\t\t\tlrpc_meta::DefinitionVersion,
\t\t\tlrpc_meta::DefinitionHash,
\t\t\tlrpc_meta::LrpcVersion};
\t}
};
"""

    output = mock_file.getvalue()
    assert output == expected


def test_with_namespace() -> None:
    mock_file = StringIO()
    writer = MetaServiceFileWriter(CppFile("test", mock_file))
    writer.write_service("my_namespace")

    expected = """\
#pragma once
#include "LrpcMeta_shim.hpp"
#include "LrpcMeta_constants.hpp"

namespace my_namespace
{
\tclass LrpcMeta_service : public LrpcMeta_shim
\t{
\tpublic:
\t\tvoid error() override {}
\t\tvoid error_stop() override {}
\t
\t\tvoid definition() override
\t\t{
\t\t\tetl::span<const uint8_t> data{lrpc_meta::CompressedDefinition};
\t
\t\t\tbool final{false};
\t\t\twhile (!final)
\t\t\t{
\t\t\t\tconst auto transmitSize = etl::min<size_t>(data.size(), lrpc_meta::DefinitionStreamChunkSize);
\t\t\t\tfinal = (transmitSize != lrpc_meta::DefinitionStreamChunkSize) ||
\t\t\t\t\t\t(data.size() == lrpc_meta::DefinitionStreamChunkSize);
\t
\t\t\t\tdefinition_response(data.take<const LRPC_BYTE_TYPE>(transmitSize), final);
\t\t\t}
\t\t}
\t\tvoid definition_stop() override {}
\t
\t\tstd::tuple<etl::string_view, etl::string_view, etl::string_view> version() override
\t\t{
\t\t\treturn {
\t\t\t\tlrpc_meta::DefinitionVersion,
\t\t\t\tlrpc_meta::DefinitionHash,
\t\t\t\tlrpc_meta::LrpcVersion};
\t\t}
\t};
}
"""

    output = mock_file.getvalue()
    assert output == expected
