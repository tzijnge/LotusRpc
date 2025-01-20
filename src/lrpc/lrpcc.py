"""LRPC client CLI"""

import logging
import os
from glob import glob
from os import path
from typing import Any
from collections.abc import Callable
import click
import serial
import yaml
from lrpc.client import ClientCliVisitor, LrpcClient
from lrpc.utils import load_lrpc_def_from_url

logging.basicConfig(format="[LRPCC] %(levelname)-8s: %(message)s", level=logging.INFO)

LRPCC_CONFIG_ENV_VAR = "LRPCC_CONFIG"
LRPCC_CONFIG_YAML = "lrpcc.config.yaml"
DEFINITION_URL = "definition_url"
TRANSPORT_TYPE = "transport_type"
TRANSPORT_PARAMS = "transport_params"


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
        input_file = config[DEFINITION_URL]
        self.lrpc_def = load_lrpc_def_from_url(input_file, warnings_as_errors=True)

        self.client = LrpcClient(self.lrpc_def)
        self.transport_type: str = config[TRANSPORT_TYPE]
        self.transport_params: dict[str, Any] = config[TRANSPORT_PARAMS]

        if self.transport_type == "serial":
            self.__communicate: Callable[[bytes], dict[str, Any]] = self.__communicate_serial
        else:
            raise NotImplementedError(f"Unsupported transport type: {self.transport_type}")

    def __communicate_serial(self, encoded: bytes) -> dict[str, Any]:
        with serial.Serial(**self.transport_params) as transport:
            transport.write(encoded)
            while True:
                received = transport.read(1)
                if len(received) == 0:
                    return {"Error": "Timeout waiting for response"}

                response = self.client.process(received)
                if response:
                    return response

    def __command_handler(self, service_name: str, function_name: str, **kwargs: Any) -> None:
        encoded = self.client.encode(service_name, function_name, **kwargs)
        response = self.__communicate(encoded)
        print(response)

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


if __name__ == "__main__":
    run_cli()
