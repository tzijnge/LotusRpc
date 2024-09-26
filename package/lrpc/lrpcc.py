"""LRPC client CLI"""

import os
import sys
from glob import glob
from os import path
from typing import Any, Callable, Optional

import click
import serial
import yaml
from lrpc.client import ClientCliVisitor, LrpcClient
from lrpc.core.definition import LrpcDef

LRPCC_CONFIG_ENV_VAR = "LRPCC_CONFIG"
LRPCC_CONFIG_YAML = "lrpcc.config.yaml"
DEFINITION_URL = "definition_url"
TRANSPORT_TYPE = "transport_type"
TRANSPORT_PARAMS = "transport_params"


def __load_config() -> Optional[dict]:
    configs = glob(f"**/{LRPCC_CONFIG_YAML}", recursive=True)
    if len(configs) == 0:
        if LRPCC_CONFIG_ENV_VAR in os.environ:
            configs.append(os.environ[LRPCC_CONFIG_ENV_VAR])
        else:
            return None

    config_url = path.abspath(configs[0])

    with open(config_url, mode="rt", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if DEFINITION_URL not in config:
        print(f"Missing field `{DEFINITION_URL}` in {config_url}")
        return None

    if TRANSPORT_TYPE not in config:
        print(f"Missing field `{TRANSPORT_TYPE}` in {config_url}")
        return None

    if TRANSPORT_PARAMS not in config:
        print(f"Missing field `{TRANSPORT_PARAMS}` in {config_url}")
        return None

    if not path.isabs(config[DEFINITION_URL]):
        config[DEFINITION_URL] = path.join(path.dirname(config_url), config[DEFINITION_URL])

    return config


@click.group()
def run_lrpcc_config_creator() -> None:
    """
    No or invalid config file found. lrpcc needs a configuration file
    named lrpcc.config.yaml. See https://github.com/tzijnge/LotusRpc for
    more information about the contents of the configuration file.
    By default, lrpcc looks for the configuration file in the current
    working directory and all subdirectories recursively. If no configuration
    file is found, lrpcc tries to use the configuration file specified by
    the LRPCC_CONFIG environment variable.

    Use the CREATE command to create a new configuration file template
    """


@run_lrpcc_config_creator.command()
@click.option(
    "-d",
    "--definition",
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

    print(f"Created file {LRPCC_CONFIG_YAML}")


class Lrpcc:
    def __init__(self, config: dict) -> None:
        self.lrpc_def: LrpcDef = LrpcDef.load(config[DEFINITION_URL])
        self.client = LrpcClient(config[DEFINITION_URL])
        self.transport_type: str = config[TRANSPORT_TYPE]
        self.transport_params: dict = config[TRANSPORT_PARAMS]

        if self.transport_type == "serial":
            self.__communicate: Callable = self.__communicate_serial
        else:
            print(f"Unsupported transport type: {self.transport_type}")
            sys.exit(1)

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
    config = __load_config()

    if config:
        Lrpcc(config).run()
    else:
        run_lrpcc_config_creator()


if __name__ == "__main__":
    run_cli()
