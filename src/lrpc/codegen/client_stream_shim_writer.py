from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.core import LrpcStream, LrpcVar


# pylint: disable = too-few-public-methods
class ClientStreamShimWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_shim(self, stream: LrpcStream) -> None:
        with self._file.block(f"void {stream.name()}_shim(Reader& r, Writer&)"):
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

        self._file.write(f"{assignment}lrpc::read_unchecked<{param.rw_type()}>({self._read_params(param)});")

    @staticmethod
    def _read_params(var: LrpcVar) -> str:
        params = ["r"]
        if var.is_array():
            params.append(f"{var.name()}")
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)
