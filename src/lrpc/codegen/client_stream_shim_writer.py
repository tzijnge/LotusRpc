from lrpc.codegen.common import rw_read_params
from lrpc.codegen.cppfile import CppFile
from lrpc.core import LrpcStream, LrpcVar


# pylint: disable = too-few-public-methods
class ClientStreamShimWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_shim(self, stream: LrpcStream) -> None:
        with self._file.block(f"void {stream.name()}_shim(Reader& reader)"):
            for p in stream.params():
                self._write_param_readers(p)

            param_list = ", ".join(stream.param_names())
            self._file.write(f"{stream.name()}({param_list});")

    def _write_param_readers(self, param: LrpcVar) -> None:
        if param.is_array():
            self._file.write(f"{param.field_type()} {param.name()};")
            assignment = ""
        else:
            assignment = f"const auto {param.name()} = "

        self._file.write(f"{assignment}lrpc::read_unchecked<{param.rw_type()}>({rw_read_params(param)});")
