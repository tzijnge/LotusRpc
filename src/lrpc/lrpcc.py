"""LRPC client CLI"""

import importlib.util
import logging
import os
import traceback
from glob import glob
from importlib import import_module
from os import path
from pathlib import Path
from typing import Any, Union

import click
import yaml

from lrpc.client import ClientCliVisitor, LrpcClient
from lrpc.utils import load_lrpc_def_from_url

logging.basicConfig(format="[LRPCC] %(levelname)-8s: %(message)s", level=logging.INFO)

LRPCC_CONFIG_ENV_VAR = "LRPCC_CONFIG"
LRPCC_CONFIG_YAML = "lrpcc.config.yaml"
DEFINITION_URL = "definition_url"
TRANSPORT_TYPE = "transport_type"
TRANSPORT_PARAMS = "transport_params"
LOG_LEVEL = "log_level"

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

def __load_config() -> dict[str, Any]:
    configs = glob(f"**/{LRPCC_CONFIG_YAML}", recursive=True)
    if len(configs) == 0:
        if LRPCC_CONFIG_ENV_VAR in os.environ:
            env_var_value = os.environ[LRPCC_CONFIG_ENV_VAR]
            if not path.exists(env_var_value):
                raise ValueError(
                    f"No configuration file found in location {env_var_value} (environment variable {LRPCC_CONFIG_ENV_VAR})"
                )
            configs.append(env_var_value)
        else:
            raise ValueError(
                f"No lrpcc configuration ({LRPCC_CONFIG_YAML}) in current working directory (recursive) or environment variable {LRPCC_CONFIG_ENV_VAR}"
            )

    config_url = path.abspath(configs[0])

    with open(config_url, mode="rt", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
        if not isinstance(config, dict):
            raise ValueError(f"Invalid YAML input for {config_file.name}")

    if DEFINITION_URL not in config:
        raise ValueError(f"Missing field `{DEFINITION_URL}` in {config_url}")

    if TRANSPORT_TYPE not in config:
        raise ValueError(f"Missing field `{TRANSPORT_TYPE}` in {config_url}")

    if TRANSPORT_PARAMS not in config:
        raise ValueError(f"Missing field `{TRANSPORT_PARAMS}` in {config_url}")

    if not path.isabs(config[DEFINITION_URL]):
        config[DEFINITION_URL] = path.join(path.dirname(config_url), config[DEFINITION_URL])

    return config


@click.group()
@click.version_option(package_name="lotusrpc", message="%(version)s")
def run_lrpcc_config_creator() -> None:
    """
    lrpcc needs a configuration file named lrpcc.config.yaml.
    See https://github.com/tzijnge/LotusRpc for more information
    about the contents of the configuration file. By default,
    lrpcc looks for the configuration file in the current working
    directory and all subdirectories recursively. If no configuration
    file is found, lrpcc tries to use the configuration file specified by
    the LRPCC_CONFIG environment variable.
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
    transport_params = {}

    if transport_type == "serial":
        transport_params["port"] = "<PORT>"
        transport_params["baudrate"] = "<BAUDRATE>"

    lrpcc_config = {
        DEFINITION_URL: definition_url,
        TRANSPORT_TYPE: transport_type,
        TRANSPORT_PARAMS: transport_params,
    }
    with open(LRPCC_CONFIG_YAML, mode="wt", encoding="utf-8") as lrpcc_config_file:
        yaml.safe_dump(lrpcc_config, lrpcc_config_file)

    logging.info("Created file %s", LRPCC_CONFIG_YAML)


# pylint: disable = too-few-public-methods
class Lrpcc:
    def __init__(self, config: dict[str, Any]) -> None:
        self.__set_log_level(config.get(LOG_LEVEL, "INFO"))

        def_url = config[DEFINITION_URL]
        self.lrpc_def = load_lrpc_def_from_url(def_url, warnings_as_errors=True)

        self.client = LrpcClient(self.lrpc_def)

        self.__set_transport(config[TRANSPORT_TYPE], config[TRANSPORT_PARAMS])


    @classmethod
    def __set_log_level(cls, log_level: str) -> None:
        if log_level not in log_level_map:
            logging.info("Invalid log level: %s. Using log level INFO", log_level)
        else:
            logging.getLogger().setLevel(log_level_map[log_level])

    def __set_transport(self, transport_type: str, transport_params: dict[str, Any]) -> None:
        transport_plugin = Path(os.getcwd() + f"/lrpcc_{transport_type}.py")
        if transport_plugin.exists():
            spec = importlib.util.spec_from_file_location(f".lrpcc_{transport_type}", os.getcwd() + f"/lrpcc_{transport_type}.py")
            if spec is not None and spec.loader is not None:
                logging.debug("Using transport plugin from: %s", transport_plugin)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                raise ImportError(f"Unable to load transport plugin from {transport_plugin}")
        else:
            module = import_module(f"lrpc.plugins.lrpcc_{transport_type}")
            logging.debug("Using built-in LRPCC transport %s", transport_type)

        if not hasattr(module, "Transport"):
            raise ImportError(f"No class named 'Transport' in {module}")

        transport_module = getattr(module, "Transport")
        if not hasattr(transport_module, "read"):
            raise ImportError(f"No method named 'read' in {transport_module}")

        if not hasattr(transport_module, "write"):
            raise ImportError(f"No method named 'write' in {transport_module}")

        logging.debug("Constructing LRPCC transport with these params: %s", transport_params)
        self.__transport = transport_module(**transport_params)

    def __communicate(self, encoded: bytes) -> Union[dict[str, Any], LrpcClient.VoidResponse]:
        self.__transport.write(encoded)
        while True:
            received = self.__transport.read(1)
            if len(received) == 0:
                return {"Error": "Timeout waiting for response"}

            response = self.client.process(received)

            if not isinstance(response, LrpcClient.IncompleteResponse):
                return response

    def __command_handler(self, service_name: str, function_name: str, **kwargs: Any) -> None:
        encoded = self.client.encode(service_name, function_name, **kwargs)
        response = self.__communicate(encoded)
        if isinstance(response, LrpcClient.VoidResponse):
            return

        for name, value in response.items():
            post_value = f" ({hex(value)})" if isinstance(value, int) else ""
            print(f"{name}: {value}{post_value}")

    def run(self) -> None:
        cli = ClientCliVisitor(self.__command_handler)
        self.lrpc_def.accept(cli)
        cli.root()


def run_cli() -> None:
    try:
        config = __load_config()

    # catching general exception here is considered ok, because application will terminate
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logging.error(str(e))
        logging.info("Entering lrpcc config creator")
        run_lrpcc_config_creator()
        return

    try:
        Lrpcc(config).run()

    # catching general exception here is considered ok, because application will terminate
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logging.error("Error running lrpcc for %s", config[DEFINITION_URL])
        logging.error(str(e))
        print(traceback.format_exc())


if __name__ == "__main__":
    run_cli()
