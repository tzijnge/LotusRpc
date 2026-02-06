from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.core import LrpcStream, LrpcVar


# pylint: disable = too-few-public-methods
class ServerStreamResponseWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_response(self, stream: LrpcStream) -> None:
        returns = stream.returns()

        with self._file.block(f"void {stream.name()}_response({self._response_params(returns)})"):
            if len(returns) == 0:
                self._file.write(f"server().transmit(id(), {stream.id()});")
            else:
                response = "" if len(returns) == 0 else self._response_captures(returns)
                writer = "" if len(returns) == 0 else "w"

                with self._file.block(f"const auto paramWriter = [{response}](Writer &{writer})", ";"):
                    for r in returns:
                        self._file.write(f"lrpc::write_unchecked<{r.rw_type()}>({self._write_params(r)});")

                self._file.write(f"server().transmit(id(), {stream.id()}, paramWriter);")

    @staticmethod
    def _write_params(var: LrpcVar) -> str:
        params = ["w", var.name()]

        if var.is_array():
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)

    @staticmethod
    def _response_params(params: list[LrpcVar]) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in params])

    @staticmethod
    def _response_captures(params: list[LrpcVar]) -> str:
        return ", ".join([f"&{p.name()}" for p in params])
