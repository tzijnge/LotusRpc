from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.utils import optionally_in_namespace

LRPC_META_SERVICE = """class LrpcMeta_service : public LrpcMeta_shim
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
};"""


# pylint: disable = too-few-public-methods
class MetaServiceFileWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_service(self, namespace: str | None = None) -> None:
        self._file.write("#pragma once")
        self._file.write('#include "LrpcMeta_shim.hpp"')
        self._file.write('#include "LrpcMeta_constants.hpp"')

        self._file.newline()
        optionally_in_namespace(self._file, self._write_service_class, namespace)

    def _write_service_class(self) -> None:
        for line in LRPC_META_SERVICE.splitlines():
            self._file.write(line)
