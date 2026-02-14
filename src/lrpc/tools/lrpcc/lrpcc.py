"""LRPC client CLI"""

import binascii
import importlib.util
import logging
import os
import traceback
from importlib import import_module
from pathlib import Path
from typing import Final, cast

import click
import colorama

from lrpc.client import ClientCliVisitor, LrpcClient, LrpcResponse, LrpcTransport
from lrpc.core.meta import MetaErrorResponseDict
from lrpc.tools.lrpcc.lrpcc_config import CHECK_SERVER_VERSION, LrpccConfig
from lrpc.types import LrpcType
from lrpc.utils.load_definition import load_lrpc_def_from_url

# ruff: noqa: T201

colorama.init(autoreset=True)

log_level_map = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARN": logging.WARNING,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}

logging.basicConfig(format="[LRPCC] %(levelname)-8s: %(message)s", level=log_level_map["INFO"])
log = logging.getLogger("LRPCC")

LRPCC_CONFIG_ENV_VAR: Final = "LRPCC_CONFIG"
LRPCC_CONFIG_YAML: Final = "lrpcc.config.yaml"


def find_config() -> Path:
    configs = Path.cwd().rglob(pattern=f"**/{LRPCC_CONFIG_YAML}")
    config_path = next(configs, None)
    if config_path is None:
        if LRPCC_CONFIG_ENV_VAR in os.environ:
            env_var_value = os.environ[LRPCC_CONFIG_ENV_VAR]
            if not Path(env_var_value).exists():
                raise FileNotFoundError(
                    f"No configuration file found in location '{env_var_value}' "
                    f"(environment variable {LRPCC_CONFIG_ENV_VAR})",
                )
            config_path = Path(env_var_value)
        else:
            raise FileNotFoundError(
                f"No lrpcc configuration ({LRPCC_CONFIG_YAML}) in current working directory "
                f"(recursive) or environment variable {LRPCC_CONFIG_ENV_VAR}",
            )

    return config_path.resolve()


@click.group()
@click.version_option(package_name="lotusrpc", message="%(version)s")
def run_lrpcc_config_creator() -> None:
    """\b
        __          __             ____  ____  ______
       / /   ____  / /___  _______/ __ \\/ __ \\/ ____/
      / /   / __ \\/ __/ / / / ___/ /_/ / /_/ / /
     / /___/ /_/ / /_/ /_/ (__  ) _, _/ ____/ /___
    /_____/\\____/\\__/\\__,_/____/_/ |_/_/    \\____/

    lrpcc is the LotusRPC client CLI tool.

    lrpcc needs a configuration file named lrpcc.config.yaml.
    See https://tzijnge.github.io/LotusRpc/tools/#lrpcc for more
    information about the contents of the configuration file and
    usage in general. By default, lrpcc looks for the
    configuration file in the current working directory and all
    subdirectories recursively. If no configuration file is
    found, lrpcc tries to use the configuration file specified
    by the LRPCC_CONFIG environment variable.
    """


@run_lrpcc_config_creator.command()
@click.option(
    "-d",
    "--definition_url",
    type=click.Path(file_okay=True, dir_okay=False),
    required=True,
    help="Path to LRPC definition file, absolute or relative to current working directory",
)
@click.option(
    "-t",
    "--transport_type",
    type=click.Choice(["serial"]),
    required=True,
    help="lrpcc transport type",
)
def create(definition_url: str, transport_type: str) -> None:
    """Create a new lrpcc configuration file template"""
    LrpccConfig.create(Path(LRPCC_CONFIG_YAML), definition_url, transport_type)
    log.info("Created file %s", LRPCC_CONFIG_YAML)


# pylint: disable = too-few-public-methods
class Lrpcc:
    def __init__(self, config: LrpccConfig) -> None:
        self._set_log_level(config.log_level())

        transport = self._make_transport(config)
        from_server = config.definition_from_server()

        if from_server == "always":
            self.client = LrpcClient.from_server(transport)
        elif from_server == "never":
            def_url = config.definition_url()
            lrpc_def = load_lrpc_def_from_url(def_url, warnings_as_errors=True)
            self.client = LrpcClient(lrpc_def, transport)
        else:  # once
            def_url = config.definition_url()
            if def_url.exists():
                lrpc_def = load_lrpc_def_from_url(def_url, warnings_as_errors=True, include_meta_def=False)
                self.client = LrpcClient(lrpc_def, transport)
            else:
                self.client = LrpcClient.from_server(transport, save_to=def_url)

        if config.check_server_version():
            version_ok = self.client.check_server_version()
            if not version_ok:
                log.info(
                    "Use the '%s' setting in the config file (%s) to disable the version check",
                    CHECK_SERVER_VERSION,
                    find_config(),
                )

    @classmethod
    def _set_log_level(cls, log_level: str) -> None:
        if log_level not in log_level_map:
            log.info("Invalid log level: %s. Using log level INFO", log_level)
        else:
            log.setLevel(log_level_map[log_level])

    @staticmethod
    def _make_transport(config: LrpccConfig) -> LrpcTransport:
        transport_type = config.transport_type()
        transport_params = config.transport_params()

        transport_plugin = Path.cwd().joinpath(f"lrpcc_{transport_type}.py")
        if transport_plugin.exists():
            spec = importlib.util.spec_from_file_location(
                f".lrpcc_{transport_type}",
                Path.cwd().joinpath(f"lrpcc_{transport_type}.py"),
            )
            if spec is not None and spec.loader is not None:
                log.debug("Using transport plugin from: %s", transport_plugin)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                raise ImportError(f"Unable to load transport plugin from {transport_plugin}")
        else:
            module = import_module(f"lrpc.plugins.lrpcc_{transport_type}")
            log.debug("Using built-in LRPCC transport %s", transport_type)

        if not hasattr(module, "Transport"):
            raise AttributeError(f"No class named 'Transport' in {module}")

        transport_module = module.Transport
        if not hasattr(transport_module, "read"):
            raise AttributeError(f"No method named 'read' in {transport_module}")

        if not hasattr(transport_module, "write"):
            raise AttributeError(f"No method named 'write' in {transport_module}")

        log.debug("Constructing LRPCC transport with params: %s", transport_params)

        transport: LrpcTransport = transport_module(**transport_params)
        return transport

    def _command_handler(self, service_name: str, function_or_stream_name: str, **kwargs: LrpcType) -> None:
        for index, response in enumerate(self.client.communicate(service_name, function_or_stream_name, **kwargs)):
            self._print_response(response, index)

    @staticmethod
    def _print_response(response: LrpcResponse, index: int) -> None:
        if response.is_error_response:
            error_payload = cast(MetaErrorResponseDict, response.payload)
            Lrpcc._print_error_response(error_payload)
            return

        if response.is_stream_response:
            print(colorama.Fore.CYAN + f"[#{index}]")

        payload = response.payload
        max_response_name_width = 0
        if len(payload) != 0:
            max_response_name_width = max(len(k) for k in payload)

        for name, value in payload.items():
            name_text = colorama.Fore.GREEN + name.ljust(max_response_name_width) + colorama.Style.RESET_ALL
            hex_repr = (
                colorama.Style.BRIGHT + colorama.Fore.LIGHTBLACK_EX + f" ({hex(value)})"
                if (isinstance(value, int) and not isinstance(value, bool))
                else ""
            )
            if isinstance(value, bytes):
                print(f"{name_text}: [{binascii.hexlify(value, ' ').decode('utf-8')}]")
            else:
                print(f"{name_text}: {value}{hex_repr}")

    @staticmethod
    def _print_error_line(line: str) -> None:
        print(colorama.Fore.RED + line + colorama.Fore.RESET)

    @staticmethod
    def _print_error_response(response: MetaErrorResponseDict) -> None:
        if response["type"] == "UnknownService":
            Lrpcc._print_error_line(
                f"Server reported call to unknown service with ID {response['p1']}. "
                f"Function or stream ID is {response['p2']}",
            )
        elif response["type"] == "UnknownFunctionOrStream":
            Lrpcc._print_error_line(
                f"Server reported call to unknown function or stream with ID "
                f"{response['p2']} in service with ID {response['p1']}",
            )
        else:
            Lrpcc._print_error_line(
                f"Server reported an unknown error (type='{response['type']}') with the following properties:",
            )
            Lrpcc._print_error_line(f"p1={response['p1']}")
            Lrpcc._print_error_line(f"p2={response['p2']}")
            Lrpcc._print_error_line(f"p3={response['p3']}")
            Lrpcc._print_error_line(f"message='{response['message']}'")

    def run(self) -> None:
        cli = ClientCliVisitor(self._command_handler)
        self.client.definition().accept(cli, visit_meta_service=False)
        cli.root()


def run_cli() -> None:
    try:
        config_path = find_config()
        config = LrpccConfig.load(config_path)

    # catching general exception here is considered ok, because application will terminate
    # pylint: disable=broad-exception-caught
    except Exception:
        log.exception("Unable to find or load an LRPCC config")
        log.info("Entering LRPCC config creator")
        run_lrpcc_config_creator()
        return

    try:
        Lrpcc(config).run()

    # catching general exception here is considered ok, because application will terminate
    # pylint: disable=broad-exception-caught
    except Exception:
        log.exception("Error running LRPCC")
        log.info(traceback.format_exc())


if __name__ == "__main__":
    run_cli()
