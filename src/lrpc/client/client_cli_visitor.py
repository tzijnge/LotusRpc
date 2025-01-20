from functools import partial
from typing import Any, Optional
from collections.abc import Callable

import click
import yaml
import yaml.parser
from ..visitors import LrpcVisitor
from ..core import LrpcDef, LrpcEnum, LrpcEnumField, LrpcFun, LrpcService, LrpcVar

NONE_ARG = "7bc9ddaa-b6c9-4afb-93c1-5240ec91ab9c"


class YamlParamType(click.ParamType):
    """Convert command line input to a struct. Command line
    input must be valid YAML with every key being a field
    and every value being the value of the field"""

    name = "YAML"

    # function does not always return
    # pylint: disable=inconsistent-return-statements
    def convert(self, value: Any, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> dict[str, Any]:
        if isinstance(value, dict):
            return value

        try:
            v = yaml.safe_load(value)
            if isinstance(v, dict):
                return v
        except yaml.parser.ParserError:
            pass

        self.fail(f"{value} does not contain valid YAML", param, ctx)


class OptionalParamType(click.ParamType):
    """Convert command line input to LRPC optional. "_" maps to None,
    any other input is converted to the underlying type. A string input
    which is a sequence of underscores must be escaped with an additional
    underscore"""

    name = "LRPC optional"

    def __init__(self, contained_type: click.ParamType) -> None:
        self.contained_type: click.ParamType = contained_type

    def convert(self, value: Any, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> Any:
        if not isinstance(value, str):
            self.fail(f"{value} is not a string", param, ctx)

        if value == "_":
            return NONE_ARG

        # value only contains underscores
        if len(value) != 0 and len(value.replace("_", "")) == 0:
            value = value.removeprefix("_")

        return self.contained_type.convert(value, param, ctx)


class ClientCliVisitor(LrpcVisitor):
    """
    Class to create an LRPC client CLI (based on click) from spec.
    Pass an instance of this class to LrpcDef.accept() to build the CLI.
    Call ClientCliVisitor.root() to activate the CLI
    """

    def __init__(self, callback: Callable[..., None]) -> None:
        self.root: click.Group
        self.current_service: click.Group
        self.current_function: click.Command
        self.enum_values: dict[str, list[str]] = {}

        self.callback = callback

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.root = click.Group(lrpc_def.name())
        self.root.add_command(self.__version_option())

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.current_service = click.Group(service.name())

    def visit_lrpc_service_end(self) -> None:
        self.root.add_command(self.current_service)

    def visit_lrpc_enum_field(self, enum: LrpcEnum, field: LrpcEnumField) -> None:
        if enum.name() not in self.enum_values:
            self.enum_values.update({enum.name(): []})

        self.enum_values[enum.name()].append(field.name())

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        assert self.current_service.name is not None
        self.current_function = click.Command(
            name=function.name(),
            callback=partial(self.__handle_command, self.current_service.name, function.name()),
            help=f"Call LRPC function {self.current_service.name}.{function.name()}",
        )

    def visit_lrpc_function_end(self) -> None:
        self.current_service.add_command(self.current_function)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        attributes = {"type": self.__click_type(param), "nargs": param.array_size() if param.is_array() else 1}
        required = True

        arg = click.Argument([param.name()], required, **attributes)
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

        return t

    def __handle_command(self, service: str, function: str, **kwargs: Any) -> None:
        for a, v in kwargs.items():
            if v == NONE_ARG:
                kwargs[a] = None

        self.callback(service, function, **kwargs)

    @staticmethod
    @click.command()
    @click.version_option(package_name="lotusrpc", message="%(version)s")
    def __version_option() -> None:
        # intentionally empty because all functionality is handled by the click decorator
        pass
