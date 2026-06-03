from lrpc.codegen.cppfile import CppFile
from lrpc.codegen.utils import optionally_in_namespace

LRPC_META_SERVICE = """class LrpcMeta_service : public LrpcMeta_shim
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
};"""


# pylint: disable = too-few-public-methods
class MetaServiceFileWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_service(self, namespace: str | None = None) -> None:
        self._file.pragma_once()
        self._file.include('"LrpcMeta_shim.hpp"')
        self._file.include('"LrpcMeta_constants.hpp"')

        self._file.newline()
        optionally_in_namespace(self._file, self._write_service_class, namespace)

    def _write_service_class(self) -> None:
        for line in LRPC_META_SERVICE.splitlines():
            self._file.write(line)
