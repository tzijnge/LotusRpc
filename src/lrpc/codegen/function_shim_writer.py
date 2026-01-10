from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.core import LrpcFun, LrpcVar


class FunctionShimWriter:
    def __init__(self, file: CppFile) -> None:
        self._file = file

    def write_function_shim(self, function: LrpcFun) -> None:
        """Write a single function shim to the C++ file."""
        params = self._params_string(function.params())
        reader_param_name = " r" if len(params) != 0 else ""

        with self._file.block(f"void {function.name()}_shim(Reader&{reader_param_name}, Writer& w)"):
            self._write_function_shim_body(function)

    def _write_function_shim_body(self, function: LrpcFun) -> None:
        self._file.write(f"writeHeader(w, {function.id()});")

        self._write_param_readers(function)
        self._write_invocation(function)
        self._write_return_writers(function)

    def _write_param_readers(self, function: LrpcFun) -> None:
        def read_params(var: LrpcVar) -> str:
            params = ["r"]
            if var.is_array():
                params.append(f"{var.name()}")
                params.append(f"{var.array_size()}")
            if var.is_fixed_size_string():
                params.append(f"{var.string_size()}")

            return ", ".join(params)

        for p in function.params():
            if p.is_array():
                self._file.write(f"{p.field_type()} {p.name()};")
                assignment = ""
            else:
                assignment = f"const auto {p.name()} = "

            self._file.write(f"{assignment}lrpc::read_unchecked<{p.rw_type()}>({read_params(p)});")

    def _write_invocation(self, function: LrpcFun) -> None:
        param_list = ", ".join(function.param_names())

        response = "const auto response = " if len(function.returns()) != 0 else ""
        self._file.write(f"{response}{function.name()}({param_list});")

    def _write_return_writers(self, function: LrpcFun) -> None:
        def write_params(var: LrpcVar, index: int | None) -> str:
            params = ["w"]
            if index is None:
                params.append("response")
            else:
                params.append(f"std::get<{index}>(response)")

            if var.is_array():
                params.append(f"{var.array_size()}")
            if var.is_fixed_size_string():
                params.append(f"{var.string_size()}")

            return ", ".join(params)

        returns = function.returns()
        for i, r in enumerate(returns):
            return_index = None if len(returns) == 1 else i
            self._file.write(
                f"lrpc::write_unchecked<{r.rw_type()}>({write_params(r, return_index)});",
            )

    @staticmethod
    def _params_string(params: list[LrpcVar]) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in params])
