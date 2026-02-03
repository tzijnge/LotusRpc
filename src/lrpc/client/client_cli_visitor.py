from collections.abc import Callable, Iterable, Sequence
from functools import partial
from importlib import metadata
from typing import Any

import click
import yaml
import yaml.parser

from lrpc.core import LrpcDef, LrpcEnum, LrpcEnumField, LrpcFun, LrpcService, LrpcStream, LrpcVar
from lrpc.visitors import LrpcVisitor

NONE_ARG = "7bc9ddaa-b6c9-4afb-93c1-5240ec91ab9c"


class YamlParamType(click.ParamType):
    """Convert command line input to a struct. Command line
    input must be valid YAML with every key being a field
    and every value being the value of the field"""

    name = "YAML"

    # function does not always return
    # pylint: disable=inconsistent-return-statements
    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> dict[str, Any]:  # noqa: RET503
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

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> Any:
        if not isinstance(value, str):
            self.fail(f"{value} is not a string", param, ctx)

        if value == "_":
            return NONE_ARG

        # value only contains underscores
        if len(value) != 0 and len(value.replace("_", "")) == 0:
            value = value.removeprefix("_")

        return self.contained_type.convert(value, param, ctx)


class VersionOption(click.Option):
    """``--version`` option which immediately prints the version
    and exits the program.
    """

    def __init__(
        self,
        param_decls: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> None:
        if not param_decls:
            param_decls = ("--version",)

        kwargs.setdefault("is_flag", True)
        kwargs.setdefault("expose_value", False)
        kwargs.setdefault("is_eager", True)
        kwargs.setdefault("help", "Show version and exit.")
        kwargs.setdefault("callback", self.show_version)

        super().__init__(param_decls, **kwargs)

    @staticmethod
    def show_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:  # noqa: FBT001
        if not value or ctx.resilient_parsing:
            return
        click.echo(metadata.version("lotusrpc"))
        ctx.exit()


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
        self.current_stream: click.Command
        self.current_stream_origin: LrpcStream.Origin
        self.current_stream_is_finite: bool
        self.enum_values: dict[str, list[str]] = {}

        self.callback = callback

    def visit_lrpc_def(self, lrpc_def: LrpcDef) -> None:
        self.root = click.Group(lrpc_def.name())
        self.root.params.append(VersionOption())

    def visit_lrpc_service(self, service: LrpcService) -> None:
        self.current_service = click.Group(service.name())

    def visit_lrpc_service_end(self) -> None:
        self.root.add_command(self.current_service)

    def visit_lrpc_enum_field(self, enum: LrpcEnum, field: LrpcEnumField) -> None:
        if enum.name() not in self.enum_values:
            self.enum_values.update({enum.name(): []})

        self.enum_values[enum.name()].append(field.name())

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        if self.current_service.name is None:
            raise ValueError("Click group initialized without name")
        self.current_function = click.Command(
            name=function.name(),
            callback=partial(self.__handle_command, self.current_service.name, function.name(), None),
            help=f"Call LRPC function {self.current_service.name}.{function.name()}",
        )

    def visit_lrpc_function_end(self) -> None:
        self.current_service.add_command(self.current_function)

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self.current_function.params.append(self.__make_arg(param))

    def visit_lrpc_stream(self, stream: LrpcStream) -> None:
        if self.current_service.name is None:
            raise ValueError("Click group initialized without name")

        self.current_stream_origin = stream.origin()
        self.current_stream_is_finite = stream.is_finite()

        if stream.origin() == LrpcStream.Origin.SERVER:
            command_help = f"Start or stop stream from server: {self.current_service.name}.{stream.name()}"
        else:
            command_help = f"Send stream message to server: {self.current_service.name}.{stream.name()}"

        self.current_stream = click.Command(
            name=stream.name(),
            callback=partial(
                self.__handle_command,
                self.current_service.name,
                stream.name(),
                self.current_stream_origin,
            ),
            help=command_help,
        )

        self.current_service.add_command(self.current_stream)

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        if self.current_stream_origin == LrpcStream.Origin.SERVER:
            if param.name() != "start":
                raise ValueError("Server stream takes a single parameter named 'start'")
            self.current_stream.params.append(self.__make_stream_start_stop_option())
        elif self.current_stream_is_finite and (param.name() == "final"):
            self.current_stream.params.append(self.__make_stream_final_option())
        else:
            self.current_stream.params.append(self.__make_arg(param))

    def visit_lrpc_stream_end(self) -> None:
        if self.current_stream_origin == LrpcStream.Origin.CLIENT:
            self.current_service.add_command(self.current_stream)

    def __make_arg(self, param: LrpcVar) -> click.Parameter:
        cb: (
            Callable[[click.Context, click.Parameter, str], bytes]
            | Callable[[click.Context, click.Parameter, tuple[str]], Iterable[bytes]]
            | None
        ) = None
        if param.base_type_is_bytearray():
            cb = self.__validate_array_of_bytearray if param.is_array() else self.__validate_bytearray

        return click.Argument(
            [param.name()],
            required=True,
            type=self.__click_type(param),
            nargs=param.array_size() if param.is_array() else 1,
            callback=cb,
        )

    def __make_stream_final_option(self) -> click.Option:
        return click.Option(
            ["--final"],
            is_flag=True,
            default=False,
            show_default=True,
            required=False,
            help="Indicate the final message in the stream",
        )

    def __make_stream_start_stop_option(self) -> click.Option:
        return click.Option(
            ["--start/--stop"],
            is_flag=True,
            default=True,
            show_default=True,
            required=False,
            help="Start or stop the stream",
        )

    @staticmethod
    def __validate_array_of_bytearray(
        ctx: click.Context,
        param: click.Parameter,
        value: tuple[str],
    ) -> Iterable[bytes]:
        return [ClientCliVisitor.__validate_bytearray(ctx, param, ba) for ba in value]

    @staticmethod
    def __validate_bytearray(ctx: click.Context, param: click.Parameter, ba: str) -> bytes:
        try:
            return bytes.fromhex(ba)
        except ValueError as e:
            raise click.BadParameter(
                "Parameter must contain an even number of case-insensitive hex digits, possibly whitespace separated.",
                ctx=ctx,
                param=param,
            ) from e

    def __click_type(self, param: LrpcVar) -> click.ParamType:
        t: click.ParamType = click.UNPROCESSED

        if param.base_type_is_integral():
            t = click.INT

        if param.base_type_is_string() or param.base_type_is_bytearray():
            t = click.STRING

        if param.base_type_is_float():
            t = click.FLOAT

        if param.base_type_is_bool():
            t = click.BOOL

        if param.base_type_is_custom():
            if param.base_type_is_enum():
                t = click.Choice(self.enum_values[param.base_type()])

            if param.base_type_is_struct():
                t = YamlParamType()

        if param.is_optional():
            t = OptionalParamType(t)

        return t

    def __handle_command(
        self,
        service: str,
        function_or_stream: str,
        origin: LrpcStream.Origin | None = None,
        **kwargs: Any,
    ) -> None:
        # click does not always pass the 'start' and 'final' options in the same
        # order as they were added to the command. Hence they need to be moved to
        # the end of the parameters dictionary
        if origin == LrpcStream.Origin.SERVER and "start" in kwargs:
            kwargs.update({"start": kwargs.pop("start")})
        elif "final" in kwargs:
            kwargs.update({"final": kwargs.pop("final")})

        for a, v in kwargs.items():
            if v == NONE_ARG:
                kwargs[a] = None
        try:
            self.callback(service, function_or_stream, **kwargs)
        except Exception as e:
            raise click.ClickException(str(e)) from e
