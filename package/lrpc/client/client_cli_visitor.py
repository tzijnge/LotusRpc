from functools import partial

import click
import yaml
import yaml.parser
from lrpc import LrpcVisitor
from lrpc.core import LrpcDef, LrpcEnum, LrpcEnumField, LrpcFun, LrpcService, LrpcVar

NONE_ARG = "7bc9ddaa-b6c9-4afb-93c1-5240ec91ab9c"


class YamlParamType(click.ParamType):
    """Convert command line input to a struct. Command line
    input must be valid YAML with every key being a field
    and every value being the value of the field"""

    name = "YAML"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value

        try:
            return yaml.safe_load(value)
        except yaml.parser.ParserError:
            self.fail(f"{value} does not contain valid YAML", param, ctx)


class OptionalParamType(click.ParamType):
    """Convert command line input to LRPC optional. "_" maps to None,
    any other input is converted to the underlying type. A string input
    which is a sequence of underscores must be escaped with an additional
    underscore"""

    name = "LRPC optional"

    def __init__(self, contained_type: click.ParamType) -> None:
        self.contained_type: click.ParamType = contained_type

    def convert(self, value, param, ctx):
        if not isinstance(value, str):
            self.fail(f"{value} is not a string", param, ctx)

        if value == "_":
            return NONE_ARG
        elif len(value) != 0 and len(value.replace("_", "")) == 0:  # value only contains underscores
            value = value.removeprefix("_")

        return self.contained_type.convert(value, param, ctx)


class ClientCliVisitor(LrpcVisitor):
    """
    Class to create an LRPC client CLI (based on click) from spec.
    Pass an instance of this class to LrpcDef.accept() to build the CLI.
    Call ClientCliVisitor.root() to activate the CLI
    """

    def __init__(self, callback) -> None:
        self.root: click.Group = None
        self.current_service: click.Group = None
        self.current_function: click.Command = None
        self.enum_values: dict[str, list[str]] = {}

        self.callback = callback

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.root = click.Group(lrpc_def.name())

    def visit_lrpc_service(self, service: LrpcService):
        self.current_service = click.Group(service.name())

    def visit_lrpc_service_end(self):
        self.root.add_command(self.current_service)

    def visit_lrpc_enum_field(self, enum: LrpcEnum, field: LrpcEnumField):
        if enum.name() not in self.enum_values:
            self.enum_values.update({enum.name(): []})

        self.enum_values[enum.name()].append(field.name())

    def visit_lrpc_function(self, function: LrpcFun):
        self.current_function = click.Command(
            name=function.name(),
            callback=partial(self.__handle_command, self.current_service.name, function.name()),
            help="my help 123",
        )

    def visit_lrpc_function_end(self):
        self.current_service.add_command(self.current_function)

    def visit_lrpc_function_param(self, param: LrpcVar):
        attributes = {"type": self.__click_type(param), "nargs": param.array_size() if param.is_array() else 1}

        arg = click.Argument([param.name()], **attributes)
        self.current_function.params.append(arg)

    def __click_type(self, param: LrpcVar) -> click.ParamType:
        t: click.ParamType = click.UNPROCESSED

        if param.base_type_is_integral():
            t = click.INT

        if param.base_type_is_string():
            t = click.STRING

        if param.base_type_is_enum():
            t = click.Choice(self.enum_values[param.base_type()])

        if param.base_type_is_float():
            t = click.FLOAT

        if param.base_type_is_bool():
            t = click.BOOL

        if param.base_type_is_custom():
            t = YamlParamType()

        if param.is_optional():
            return OptionalParamType(t)
        else:
            return t

    def __handle_command(self, service, function, **kwargs):
        for a, v in kwargs.items():
            if v == NONE_ARG:
                kwargs[a] = None

        return self.callback(service, function, **kwargs)
