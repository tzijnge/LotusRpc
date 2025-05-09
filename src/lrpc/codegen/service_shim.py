import os
from typing import Optional
from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..codegen.common import write_file_banner
from ..codegen.utils import optionally_in_namespace
from ..visitors import LrpcVisitor
from ..core import LrpcDef, LrpcService, LrpcFun, LrpcVar


# pylint: disable = too-many-instance-attributes
class ServiceShimVisitor(LrpcVisitor):

    def __init__(self, output: os.PathLike[str]) -> None:
        self.__file: CppFile
        self.__namespace: Optional[str]
        self.__output = output
        self.__function_info: dict[int, str]
        self.__max_function_id = 0
        self.__function_declarations: list[str]
        self.__function_shims: list[list[str]]
        self.__function_params: list[LrpcVar]
        self.__function_returns: list[LrpcVar]
        self.__function_name: str
        self.__service_name: str
        self.__service_id: int

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__namespace = lrpc_def.namespace()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__file = CppFile(f"{self.__output}/{service.name()}_ServiceShim.hpp")
        self.__function_info = {}
        self.__max_function_id = 0
        self.__function_declarations = []
        self.__function_shims = []
        self.__service_name = service.name()
        self.__service_id = service.id()

        write_file_banner(self.__file)
        self.__write_include_guard()
        self.__write_includes()

    def visit_lrpc_service_end(self) -> None:
        optionally_in_namespace(self.__file, self.__write_shim, self.__namespace)

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self.__function_params = []
        self.__function_returns = []
        self.__function_name = function.name()
        self.__max_function_id = max(self.__max_function_id, function.id())
        self.__function_info.update({function.id(): function.name()})

    def visit_lrpc_function_end(self) -> None:
        name = self.__function_name
        params = self.__params_string()
        returns = self.__returns_string()
        self.__function_declarations.append(f"virtual {returns} {name}({params}) = 0;")

        shim = []
        reader_name = "r" if len(self.__function_params) != 0 else ""
        writer_name = "w" if len(self.__function_returns) != 0 else ""
        shim.append(f"void {name}_shim(Reader& {reader_name}, Writer& {writer_name})")
        shim.extend(self.__function_shim_body())
        self.__function_shims.append(shim)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.__function_params.append(param)

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.__function_returns.append(ret)

    def __write_shim(self) -> None:
        with self.__file.block(f"class {self.__service_name}ServiceShim : public lrpc::Service", ";"):
            self.__file.label("public")
            self.__file(f"virtual ~{self.__service_name}ServiceShim() = default;")
            self.__file.newline()
            self.__file(f"uint8_t id() const override {{ return {self.__service_id}; }}")
            self.__file.newline()

            with self.__file.block("bool invoke(Reader &reader, Writer &writer) override"):
                self.__file("auto functionId = reader.read_unchecked<uint8_t>();")
                with self.__file.block(f"if (shim(functionId) == &{self.__service_name}ServiceShim::null_shim)"):
                    self.__file("return false;")
                self.__file("writer.write_unchecked<uint8_t>(id());")
                self.__file("writer.write_unchecked<uint8_t>(functionId);")
                self.__file("((this)->*(shim(functionId)))(reader, writer);")
                self.__file("return true;")

            self.__file.newline()
            self.__file.label("protected")
            for decl in self.__function_declarations:
                self.__file.write(decl)

            self.__file.newline()

            for shim in self.__function_shims:
                with self.__file.block(shim[0]):
                    for l in shim[1:]:
                        self.__file.write(l)

                self.__file.newline()

            self.__file.label("private")
            self.__write_shim_array()

    def __write_shim_array(self) -> None:
        null_shim_name = "null"
        self.__file.write(f"using ShimType = void ({self.__service_name}ServiceShim::*)(Reader &, Writer &);")
        self.__file.write(f"constexpr void {null_shim_name}_shim(Reader&, Writer&) {{}}")
        self.__file.newline()

        with self.__file.block("static ShimType shim(const size_t functionId)"):
            with self.__file.block(f"static constexpr etl::array<ShimType, {self.__max_function_id + 1}> shims", ";"):
                with self.__file.block(""):
                    for fid in range(0, self.__max_function_id + 1):
                        name = self.__function_info.get(fid, null_shim_name)
                        self.__file(f"&{self.__service_name}ServiceShim::{name}_shim,")

            self.__file.newline()

            with self.__file.block("if (functionId > shims.size())"):
                self.__file.write(f"return &{self.__service_name}ServiceShim::null_shim;")

            self.__file.newline()

            self.__file.write("return shims.at(functionId);")


    def __function_shim_body(self) -> list[str]:
        body = []

        for p in self.__function_params:
            n = p.name()
            t = p.read_type()
            body.append(f"const auto {n} = lrpc::read_unchecked<{t}>(r);")

        param_list = ", ".join([p.name() for p in self.__function_params])

        response = "const auto response = " if len(self.__function_returns) != 0 else ""
        body.append(f"{response}{self.__function_name}({param_list});")

        returns = self.__function_returns
        if len(returns) == 1:
            t = returns[0].write_type()
            body.append(f"lrpc::write_unchecked<{t}>(w, response);")
        else:
            for i, r in enumerate(returns):
                t = r.write_type()
                body.append(f"lrpc::write_unchecked<{t}>(w, std::get<{i}>(response));")

        return body

    def __params_string(self) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in self.__function_params])

    def __returns_string(self) -> str:
        if len(self.__function_returns) == 0:
            return "void"

        if len(self.__function_returns) == 1:
            return self.__function_returns[0].return_type()

        types = ", ".join([r.return_type() for r in self.__function_returns])
        return f"std::tuple<{types}>"

    def __write_include_guard(self) -> None:
        self.__file("#pragma once")

    def __write_includes(self) -> None:
        self.__file('#include "lrpccore/Service.hpp"')
        self.__file('#include "lrpccore/EtlRwExtensions.hpp"')
        self.__file(f'#include "{self.__service_name}.hpp"')

        self.__file.newline()
