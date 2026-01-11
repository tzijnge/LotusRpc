from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.core import LrpcStruct, LrpcVar


class StructCodecWriter:
    def __init__(self, file: CppFile, descriptor: LrpcStruct, namespace: str | None) -> None:
        self._file = file
        self._descriptor = descriptor
        self._namespace = namespace

    def write_encoder(self) -> None:
        name = self._name()
        self._file("template<>")
        with self._file.block(
            f"inline void write_unchecked<{name}>(etl::byte_stream_writer& writer, const {name}& obj)",
        ):
            for f in self._descriptor.fields():
                t = f.rw_type(self._namespace)
                p = StructCodecWriter._write_params(f)
                self._file.write(f"lrpc::write_unchecked<{t}>({p});")

    def write_decoder(self) -> None:
        self._file("template<>")
        name = self._name()
        with self._file.block(f"inline {name} read_unchecked<{name}>(etl::byte_stream_reader& reader)"):
            self._file(f"{name} obj;")

            for f in self._descriptor.fields():
                assignment = StructCodecWriter._read_assignment(f)
                t = f.rw_type(self._namespace)
                p = StructCodecWriter._read_params(f)
                self._file.write(f"{assignment}lrpc::read_unchecked<{t}>({p});")

            self._file("return obj;")

    def _name(self) -> str:
        return f"{self._namespace}::{self._descriptor.name()}" if self._namespace else self._descriptor.name()

    @staticmethod
    def _write_params(var: LrpcVar) -> str:
        params = ["writer", f"obj.{var.name()}"]
        if var.is_array():
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)

    @staticmethod
    def _read_params(var: LrpcVar) -> str:
        params = ["reader"]
        if var.is_array():
            params.append(f"obj.{var.name()}")
            params.append(f"{var.array_size()}")
        if var.is_fixed_size_string():
            params.append(f"{var.string_size()}")

        return ", ".join(params)

    @staticmethod
    def _read_assignment(var: LrpcVar) -> str:
        return "" if var.is_array() else f"obj.{var.name()} = "
