import os
from typing import Optional
from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..codegen.utils import optionally_in_namespace
from ..visitors import LrpcVisitor
from ..core import LrpcDef, LrpcService, LrpcFun, LrpcVar


class ServiceShimVisitor(LrpcVisitor):

    def __init__(self, output: os.PathLike[str]) -> None:
        self.file: CppFile
        self.namespace: Optional[str]
        self.output = output
        self.function_info: dict
        self.max_function_id = 0
        self.function_declarations: list
        self.function_shims: list
        self.function_params: list
        self.function_returns: list
        self.function_name: str
        self.shim_array: list
        self.service_name: str
        self.service_id: int
        self.number_functions = 0

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.namespace = lrpc_def.namespace()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.file = CppFile(f"{self.output}/{service.name()}_ServiceShim.hpp")
        self.function_info = {}
        self.max_function_id = 0
        self.function_declarations = []
        self.function_shims = []
        self.shim_array = []
        self.service_name = service.name()
        self.service_id = service.id()
        self.number_functions = len(service.functions())

        self.__write_include_guard()
        self.__write_includes()

    def visit_lrpc_service_end(self) -> None:
        optionally_in_namespace(self.file, self.__write_shim, self.namespace)

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self.function_params = []
        self.function_returns = []
        self.function_name = function.name()
        self.max_function_id = max(self.max_function_id, function.id())
        self.function_info.update({function.id(): function.name()})

    def visit_lrpc_function_end(self) -> None:
        name = self.function_name
        params = self.__params_string()
        returns = self.__returns_string()
        self.function_declarations.append(f"virtual {returns} {name}({params}) = 0;")

        shim = []
        reader_name = "r" if len(self.function_params) != 0 else ""
        writer_name = "w" if len(self.function_returns) != 0 else ""
        shim.append(f"void {name}_shim(Reader& {reader_name}, Writer& {writer_name})")
        shim.extend(self.__function_shim_body())
        self.function_shims.append(shim)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.function_params.append(param)

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.function_returns.append(ret)

    def __write_shim(self) -> None:
        with self.file.block(f"class {self.service_name}ServiceShim : public lrpc::Service", ";"):
            self.file.label("public")
            self.file(f"uint32_t id() const override {{ return {self.service_id}; }}")
            self.file.newline()

            with self.file.block("void invoke(Reader &reader, Writer &writer) override"):
                self.file("auto functionId = reader.read_unchecked<uint8_t>();")
                self.file("writer.write_unchecked<uint8_t>(functionId);")
                self.file("((this)->*(shim(functionId)))(reader, writer);")

            self.file.newline()
            self.file.label("protected")
            for decl in self.function_declarations:
                self.file.write(decl)

            self.file.newline()

            for shim in self.function_shims:
                with self.file.block(shim[0]):
                    for l in shim[1:]:
                        self.file.write(l)

                self.file.newline()

            self.file.label("private")
            self.__write_shim_array()

    def __write_shim_array(self) -> None:
        null_shim_name = "null"
        self.file.write(f"using ShimType =  void ({self.service_name}ServiceShim::*)(Reader &, Writer &);")
        if self.max_function_id != (self.number_functions - 1):
            self.file.write(f"constexpr void {null_shim_name}_shim(Reader&, Writer&) {{}}")
            self.file.newline()

        with self.file.block("static ShimType shim(const size_t functionId)"):
            with self.file.block(f"static constexpr etl::array<ShimType, {self.max_function_id + 1}> shims", ";"):
                for fid in range(0, self.max_function_id + 1):
                    name = self.function_info.get(fid, null_shim_name)
                    self.file(f"&{self.service_name}ServiceShim::{name}_shim,")

            self.file.newline()
            self.file.write("return shims.at(functionId);")

    def __function_shim_body(self) -> list[str]:
        body = []

        for p in self.function_params:
            n = p.name()
            t = p.read_type()
            body.append(f"const auto {n} = lrpc::read_unchecked<{t}>(r);")

        param_list = ", ".join([p.name() for p in self.function_params])

        response = "const auto response = " if len(self.function_returns) != 0 else ""
        body.append(f"{response}{self.function_name}({param_list});")

        returns = self.function_returns
        if len(returns) == 1:
            t = returns[0].write_type()
            body.append(f"lrpc::write_unchecked<{t}>(w, response);")
        else:
            for i, r in enumerate(returns):
                t = r.write_type()
                body.append(f"lrpc::write_unchecked<{t}>(w, std::get<{i}>(response));")

        return body

    def __params_string(self) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in self.function_params])

    def __returns_string(self) -> str:
        if len(self.function_returns) == 0:
            return "void"

        if len(self.function_returns) == 1:
            return self.function_returns[0].return_type()

        types = ", ".join([r.return_type() for r in self.function_returns])
        return f"std::tuple<{types}>"

    def __write_include_guard(self) -> None:
        self.file("#pragma once")

    def __write_includes(self) -> None:
        self.file('#include "lrpc/Service.hpp"')
        self.file('#include "lrpc/EtlRwExtensions.hpp"')
        self.file(f'#include "{self.service_name}.hpp"')

        self.file.newline()
