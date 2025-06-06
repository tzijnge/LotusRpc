import os
from typing import Optional
from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from ..codegen.common import write_file_banner
from ..codegen.utils import optionally_in_namespace
from ..visitors import LrpcVisitor
from ..core import LrpcDef, LrpcService, LrpcFun, LrpcVar, LrpcStream


# pylint: disable = too-many-instance-attributes
class ServiceShimVisitor(LrpcVisitor):

    def __init__(self, output: os.PathLike[str]) -> None:
        self.__file: CppFile
        self.__namespace: Optional[str]
        self.__output = output
        self.__function__and_stream_info: dict[int, str]
        self.__max_function_or_stream_id = 0
        self.__function_declarations: list[str]
        self.__shims: list[list[str]]
        self.__params: list[LrpcVar]
        self.__returns: list[LrpcVar]
        self.__function_or_stream_name: str
        self.__service_name: str
        self.__service_id: int

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.__namespace = lrpc_def.namespace()

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.__file = CppFile(f"{self.__output}/{service.name()}_ServiceShim.hpp")
        self.__function__and_stream_info = {}
        self.__max_function_or_stream_id = 0
        self.__function_declarations = []
        self.__shims = []
        self.__service_name = service.name()
        self.__service_id = service.id()

        write_file_banner(self.__file)
        self.__write_include_guard()
        self.__write_includes()

    def visit_lrpc_service_end(self) -> None:
        optionally_in_namespace(self.__file, self.__write_shim, self.__namespace)

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self.__params = []
        self.__returns = []
        self.__function_or_stream_name = function.name()
        self.__max_function_or_stream_id = max(self.__max_function_or_stream_id, function.id())
        self.__function__and_stream_info.update({function.id(): function.name()})

    def visit_lrpc_function_end(self) -> None:
        name = self.__function_or_stream_name
        params = self.__params_string()
        returns = self.__returns_string()
        self.__function_declarations.append(f"virtual {returns} {name}({params}) = 0;")

        shim = []
        shim.append(f"void {name}_shim(Reader& r, Writer& w)")
        shim.extend(self.__function_shim_body())
        self.__shims.append(shim)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.__params.append(param)

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self.__returns.append(ret)

    def visit_lrpc_stream(self, stream: LrpcStream) -> None:
        self.__params = []
        self.__returns = []
        self.__function_or_stream_name = stream.name()
        self.__max_function_or_stream_id = max(self.__max_function_or_stream_id, stream.id())
        self.__function__and_stream_info.update({stream.id(): stream.name()})

    def visit_lrpc_stream_end(self) -> None:
        name = self.__function_or_stream_name
        params = self.__params_string()
        self.__function_declarations.append(f"virtual void {name}({params}) = 0;")

        shim = []
        shim.append(f"void {name}_shim(Reader& r, Writer&)")
        shim.extend(self.__stream_shim_body())
        self.__shims.append(shim)

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self.__params.append(param)

    def __write_shim(self) -> None:
        with self.__file.block(f"class {self.__service_name}ServiceShim : public lrpc::Service", ";"):
            self.__file.label("public")
            self.__file(f"virtual ~{self.__service_name}ServiceShim() = default;")
            self.__file.newline()
            self.__file(f"uint8_t id() const override {{ return {self.__service_id}; }}")
            self.__file.newline()

            with self.__file.block("bool invoke(Reader &r, Writer &w) override"):
                self.__file("const auto functionOrStreamId = r.free_data().front();")
                self.__file("const auto functionOrStreamShim = shim(functionOrStreamId);")
                with self.__file.block(f"if (functionOrStreamShim == &{self.__service_name}ServiceShim::null_shim)"):
                    self.__file("return false;")
                self.__file("((this)->*(functionOrStreamShim))(r, w);")
                self.__file("return true;")

            self.__file.newline()

            with self.__file.block("void s0_requestStop()"):
                with self.__file.block("if (server != nullptr)"):
                    self.__file("auto w = server->getWriter();")
                    self.__file("w.write_unchecked<uint8_t>(3); // message size")
                    self.__file("w.write_unchecked<uint8_t>(id());")
                    self.__file("w.write_unchecked<uint8_t>(0);")
                    self.__file("server->transmit(w);")

            self.__file.newline()
            self.__file.label("protected")
            for decl in self.__function_declarations:
                self.__file.write(decl)

            self.__file.newline()

            for shim in self.__shims:
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
            with self.__file.block(
                f"static constexpr etl::array<ShimType, {self.__max_function_or_stream_id + 1}> shims", ";"
            ):
                with self.__file.block(""):
                    for fid in range(0, self.__max_function_or_stream_id + 1):
                        name = self.__function__and_stream_info.get(fid, null_shim_name)
                        self.__file(f"&{self.__service_name}ServiceShim::{name}_shim,")

            self.__file.newline()

            with self.__file.block("if (functionId > shims.size())"):
                self.__file.write(f"return &{self.__service_name}ServiceShim::null_shim;")

            self.__file.newline()

            self.__file.write("return shims.at(functionId);")

    def __function_shim_body(self) -> list[str]:
        body = []

        body.append("writeMessageHeader(r, w, id());")

        for p in self.__params:
            n = p.name()
            t = p.read_type()
            body.append(f"const auto {n} = lrpc::read_unchecked<{t}>(r);")

        param_list = ", ".join([p.name() for p in self.__params])

        response = "const auto response = " if len(self.__returns) != 0 else ""
        body.append(f"{response}{self.__function_or_stream_name}({param_list});")

        returns = self.__returns
        if len(returns) == 1:
            t = returns[0].write_type()
            body.append(f"lrpc::write_unchecked<{t}>(w, response);")
        else:
            for i, r in enumerate(returns):
                t = r.write_type()
                body.append(f"lrpc::write_unchecked<{t}>(w, std::get<{i}>(response));")

        body.append("updateMessageSize(w);")

        return body

    def __stream_shim_body(self) -> list[str]:
        body = []

        body.append("r.skip<uint8_t>(1); // stream ID")

        for p in self.__params:
            n = p.name()
            t = p.read_type()
            body.append(f"const auto {n} = lrpc::read_unchecked<{t}>(r);")

        param_list = ", ".join([p.name() for p in self.__params])

        body.append(f"{self.__function_or_stream_name}({param_list});")

        return body

    def __params_string(self) -> str:
        return ", ".join([f"{p.param_type()} {p.name()}" for p in self.__params])

    def __returns_string(self) -> str:
        if len(self.__returns) == 0:
            return "void"

        if len(self.__returns) == 1:
            return self.__returns[0].return_type()

        types = ", ".join([r.return_type() for r in self.__returns])
        return f"std::tuple<{types}>"

    def __write_include_guard(self) -> None:
        self.__file("#pragma once")

    def __write_includes(self) -> None:
        self.__file('#include "lrpccore/Service.hpp"')
        self.__file('#include "lrpccore/EtlRwExtensions.hpp"')
        self.__file(f'#include "{self.__service_name}.hpp"')

        self.__file.newline()
