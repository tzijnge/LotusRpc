from io import StringIO

from lrpc.codegen.cppfile import CppFile
from lrpc.codegen.meta_service_file_writer import MetaServiceFileWriter


def test_without_namespace() -> None:
    mock_file = StringIO()
    writer = MetaServiceFileWriter(CppFile.from_writer(mock_file.write))
    writer.write_service(None)

    expected = """#pragma once
#include "LrpcMeta_shim.hpp"
#include "LrpcMeta_constants.hpp"

class LrpcMeta_service : public LrpcMeta_shim
{
public:
    void error() override {}
    void error_stop() override {}

    void definition() override
    {
        lrpc::span<const uint8_t> data{lrpc_meta::CompressedDefinition};

        bool final{false};
        while (!final)
        {
            const auto transmitSize = std::min<size_t>(data.size(), lrpc_meta::DefinitionStreamChunkSize);
            final = (transmitSize != lrpc_meta::DefinitionStreamChunkSize) ||
                    (data.size() == lrpc_meta::DefinitionStreamChunkSize);

            definition_response(data.take<const lrpc::byte>(transmitSize), final);
        }
    }
    void definition_stop() override {}

    std::tuple<lrpc::string_view, lrpc::string_view, lrpc::string_view> version() override
    {
        return {
            lrpc_meta::DefinitionVersion,
            lrpc_meta::DefinitionHash,
            lrpc_meta::LrpcVersion};
    }
};
"""

    output = mock_file.getvalue()
    assert output == expected


def test_with_namespace() -> None:
    mock_file = StringIO()
    writer = MetaServiceFileWriter(CppFile.from_writer(mock_file.write))
    writer.write_service("my_namespace")

    expected = """\
#pragma once
#include "LrpcMeta_shim.hpp"
#include "LrpcMeta_constants.hpp"

namespace my_namespace
{
    class LrpcMeta_service : public LrpcMeta_shim
    {
    public:
        void error() override {}
        void error_stop() override {}

        void definition() override
        {
            lrpc::span<const uint8_t> data{lrpc_meta::CompressedDefinition};

            bool final{false};
            while (!final)
            {
                const auto transmitSize = std::min<size_t>(data.size(), lrpc_meta::DefinitionStreamChunkSize);
                final = (transmitSize != lrpc_meta::DefinitionStreamChunkSize) ||
                        (data.size() == lrpc_meta::DefinitionStreamChunkSize);

                definition_response(data.take<const lrpc::byte>(transmitSize), final);
            }
        }
        void definition_stop() override {}

        std::tuple<lrpc::string_view, lrpc::string_view, lrpc::string_view> version() override
        {
            return {
                lrpc_meta::DefinitionVersion,
                lrpc_meta::DefinitionHash,
                lrpc_meta::LrpcVersion};
        }
    };
}
"""

    output = mock_file.getvalue()
    assert output == expected
