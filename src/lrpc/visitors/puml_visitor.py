import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator, Optional, Union

from .lrpc_visitor import LrpcVisitor

if TYPE_CHECKING:
    from ..core import (
        LrpcConstant,
        LrpcDef,
        LrpcEnum,
        LrpcEnumField,
        LrpcFun,
        LrpcService,
        LrpcStream,
        LrpcStruct,
        LrpcVar,
    )


def in_color(t: Union[str, int], c: str) -> str:
    return f"<color:{c}>{t}</color>"


def var_string(p: "LrpcVar") -> str:
    t = in_color(p.base_type(), "DarkCyan")
    if p.base_type_is_string():
        if p.is_auto_string():
            t = in_color("string", "DarkCyan")
        else:
            t = in_color("string", "DarkCyan") + "<" + in_color(f"{p.string_size()}", "ForestGreen") + ">"

    if p.is_optional():
        t = in_color("optional", "DarkCyan") + f"<{t}>"

    if p.is_array():
        t = in_color("array", "DarkCyan") + f"<{t}, " + in_color(p.array_size(), "ForestGreen") + ">"

    return t + " " + in_color(p.name(), "CornflowerBlue")


def enum_field_string(e: "LrpcEnumField") -> str:
    name = in_color(e.name(), "CornflowerBlue")
    enum_id = in_color(e.id(), "ForestGreen")
    return f"{name} = {enum_id}"


def const_string(p: "LrpcConstant") -> str:
    t = in_color(p.cpp_type(), "DarkCyan")
    n = in_color(p.name(), "CornflowerBlue")
    return t + " " + n


class PumlFile:
    def __init__(self, filename: str) -> None:
        self.text = "@startmindmap\n"
        self.filename = filename

    def write(self, t: str) -> None:
        self.text += t

    @contextmanager
    def font(self, f: str) -> Iterator[None]:
        self.write(f"<font:{f}>")
        yield
        self.write("</font>")

    @contextmanager
    def color(self, c: str) -> Iterator[None]:
        self.write(f"<color:{c}>")
        yield
        self.write("</color>")

    @contextmanager
    def size(self, s: int) -> Iterator[None]:
        self.write(f"<size:{s}>")
        yield
        self.write("</size>")

    @contextmanager
    def bold(self) -> Iterator[None]:
        self.write("**")
        yield
        self.write("**")

    @contextmanager
    def enclosed_in(self, open_str: str, close_str: str) -> Iterator[None]:
        self.write(open_str)
        yield
        self.write(close_str)

    @staticmethod
    def icon(i: str) -> str:
        return f"<&{i}>"

    def insert_icon(self, i: str) -> None:
        self.write(self.icon(i))

    def legend(self, items: list[tuple[str, str, str, str]], size: int) -> None:
        self.write("legend left\n")

        for color, pre_icon, icon, text in items:
            with self.size(size):
                with self.color(color):
                    self.write(pre_icon)
                    if len(icon) != 0:
                        self.insert_icon(icon)
                self.write(" " + text)

            self.write("\n")

        self.write("endlegend\n")

    def block(self, name: str, background: str, level: int, icon: Optional[str] = None) -> None:
        indent = "*" * level
        self.write(f"{indent}[#{background}]: ")
        if icon:
            self.insert_icon(icon)
            self.write(" ")

        with self.bold():
            self.write(name)

        self.write("\n----")

    def list_item(self, text: str, level: int = 1, font: Optional[str] = None) -> None:
        indent = "*" * level
        if level != 0:
            indent += " "
        self.write(f"\n{indent}")
        if font:
            with self.font(font):
                self.write(text)
        else:
            self.write(text)

    def list_end(self) -> None:
        self.write(";\n")

    def dump_to_file(self) -> None:
        self.write("\n@endmindmap")
        with open(self.filename, mode="w", encoding="utf-8") as file:
            file.write(self.text)

    def function_string(self, fun: "LrpcFun", max_function_or_stream_id: int) -> None:
        with self.font("monospaced"):
            with self.enclosed_in("[", "]"):
                with self.color("Orange"):
                    id_width = len(str(max_function_or_stream_id))
                    id_str = f"{fun.id()}".rjust(id_width)
                    self.write(f"F  {id_str}")
            with self.bold():
                self.write(fun.name())
            with self.color("Magenta"):
                self.write("(")
            self.write(", ".join([var_string(p) for p in fun.params()]))
            with self.color("Magenta"):
                self.write(")")
            with self.color("Orange"):
                self.insert_icon("arrow-right")
            with self.color("Magenta"):
                self.write(" (")
            self.write(", ".join([var_string(r) for r in fun.returns()]))
            with self.color("Magenta"):
                self.write(")")

    def stream_string(self, stream: "LrpcStream", max_function_or_stream_id: int) -> None:
        with self.font("monospaced"):
            with self.enclosed_in("[", "]"):
                with self.color("Green"):
                    id_width = len(str(max_function_or_stream_id))
                    infinite = " " if stream.is_finite() else self.icon("infinity")
                    id_str = f"{stream.id()}".rjust(id_width)
                    self.write(f"S{infinite} {id_str}")
            with self.bold():
                self.write(stream.name())
            with self.color("Magenta"):
                self.write("(")
            self.write(", ".join([var_string(p) for p in stream.params()]))
            with self.color("Magenta"):
                self.write(")")
            with self.color("Orange"):
                self.insert_icon("arrow-right")
            with self.color("Magenta"):
                self.write(" (")
            self.write(", ".join([var_string(r) for r in stream.returns()]))
            with self.color("Magenta"):
                self.write(")")


# pylint: disable = too-many-instance-attributes
class PlantUmlVisitor(LrpcVisitor):

    def __init__(self, output: os.PathLike[str]) -> None:
        self.__output = output
        self.__puml: PumlFile
        self.__max_function_or_stream_id = 0

        self.__enum_fields: list[LrpcEnumField] = []
        self.__enum_indent = 2
        self.__enum_indent_max = 7
        self.__enum_fields_max = 10
        self.__struct_indent = 2

        self.__struct_indent_max = 7
        self.__struct_fields: list[LrpcVar] = []
        self.__struct_fields_max = 10

        self.__constants: list[LrpcConstant] = []
        self.__const_items_max = 10

    def visit_lrpc_def(self, lrpc_def: "LrpcDef") -> None:
        self.__puml = PumlFile(f"{self.__output}/{lrpc_def.name()}.puml")

        self.__puml.block(lrpc_def.name(), "Yellow", level=1)
        self.__puml.list_item(f"Namespace: {lrpc_def.namespace()}", level=0)
        self.__puml.list_item(f"RX buffer size: {lrpc_def.rx_buffer_size()}", level=0)
        self.__puml.list_item(f"TX Buffer size: {lrpc_def.tx_buffer_size()}", level=0)
        self.__puml.list_end()

    def visit_lrpc_def_end(self) -> None:
        self.__puml.write("\n")

        legend_items = [
            ("Yellow", "", "medical-cross", "Server"),
            ("PeachPuff", "", "medical-cross", "Services"),
            ("Orange", "F", "", "Function"),
            ("Green", "S", "infinity", "Infinite stream"),
            ("Green", "S", "", "Finite stream"),
            ("Blue", "", "medical-cross", "Structs"),
            ("PaleGreen", "", "medical-cross", "Enums"),
            ("Pink", "", "medical-cross", "Constants"),
            ("Black", "", "external-link", "External"),
        ]
        self.__puml.legend(legend_items, 20)

        self.__puml.dump_to_file()

    def visit_lrpc_constants(self) -> None:
        self.__puml.block("Constants", "Pink", 2)
        self.__constants = []

    def visit_lrpc_constant(self, constant: "LrpcConstant") -> None:
        self.__constants.append(constant)

    def visit_lrpc_constants_end(self) -> None:
        const_strings = [const_string(c) for c in self.__constants[0 : self.__const_items_max]]
        if len(self.__constants) > self.__const_items_max:
            const_strings.append("...")

        for c in const_strings:
            self.__puml.list_item(c, font="monospaced")

        self.__puml.list_end()

    def visit_lrpc_enum(self, enum: "LrpcEnum") -> None:
        icon = "external-link" if enum.is_external() else None
        self.__puml.block(enum.name(), "PaleGreen", self.__enum_indent, icon)

    def visit_lrpc_enum_end(self, _: "LrpcEnum") -> None:
        enum_field_strings = [enum_field_string(ef) for ef in self.__enum_fields[0 : self.__enum_fields_max]]
        if len(self.__enum_fields) > self.__enum_fields_max:
            enum_field_strings.append("...")

        for s in enum_field_strings:
            self.__puml.list_item(s, font="monospaced")

        self.__puml.list_end()

        self.__enum_indent = self.__enum_indent + 1
        if self.__enum_indent > self.__enum_indent_max:
            self.__enum_indent = 2

    def visit_lrpc_enum_field(self, _: "LrpcEnum", field: "LrpcEnumField") -> None:
        self.__enum_fields.append(field)

    def visit_lrpc_function(self, function: "LrpcFun") -> None:
        self.__puml.write("***_ ")
        self.__puml.function_string(function, self.__max_function_or_stream_id)
        self.__puml.write("\n")

    def visit_lrpc_stream(self, stream: "LrpcStream") -> None:
        self.__puml.write("***_ ")
        self.__puml.stream_string(stream, self.__max_function_or_stream_id)
        self.__puml.write("\n")

    def visit_lrpc_service(self, service: "LrpcService") -> None:
        self.__puml.block(service.name(), "PeachPuff", 2)
        self.__puml.list_item(f"ID: {service.id()}", level=0)
        self.__puml.list_end()

        function_ids = [f.id() for f in service.functions()]
        stream_ids = [s.id() for s in service.streams()]
        self.__max_function_or_stream_id = max(function_ids + stream_ids)

    def visit_lrpc_struct(self, struct: "LrpcStruct") -> None:
        self.__struct_fields = []
        icon = "external-link" if struct.is_external() else None
        self.__puml.block(struct.name(), "lightblue", self.__struct_indent, icon)

    def visit_lrpc_struct_end(self) -> None:
        struct_field_strings = [var_string(sf) for sf in self.__struct_fields[0 : self.__struct_fields_max]]
        if len(self.__struct_fields) > self.__struct_fields_max:
            struct_field_strings.append("...")

        for s in struct_field_strings:
            self.__puml.list_item(s, font="monospaced")

        self.__puml.list_end()

        self.__struct_indent = self.__struct_indent + 1
        if self.__struct_indent > self.__struct_indent_max:
            self.__struct_indent = 2

    def visit_lrpc_struct_field(self, _: "LrpcStruct", field: "LrpcVar") -> None:
        self.__struct_fields.append(field)
