"""LRPC client CLI"""

from lrpc.core.definition import LrpcDef
from lrpc.client import ClientCliVisitor, LrpcClient
import serial
import sys
from glob import glob
import yaml
from os import path
import os
import click

LRPCC_CONFIG_ENV_VAR = "LRPCC_CONFIG"
LRPCC_CONFIG_YAML = "lrpcc.config.yaml"
DEFINITION_URL = "definition_url"
TRANSPORT_TYPE = "transport_type"
TRANSPORT_PARAMS = "transport__params"


def __load_config():
    configs = glob(f"**/{LRPCC_CONFIG_YAML}", recursive=True)
    if len(configs) == 0:
        if LRPCC_CONFIG_ENV_VAR in os.environ:
            configs.append(os.environ[LRPCC_CONFIG_ENV_VAR])
        else:
            return None

    config_url = path.abspath(configs[0])

    with open(config_url, "rt") as config_file:
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
def run_lrpcc_config_creator():
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
    pass


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
def create(definition, transport_type: str):
    """Create a new lrpcc configuration file template"""
    transport_params = {}

    if transport_type == "serial":
        transport_params["port"] = "<PORT>"
        transport_params["baudrate"] = "<BAUDRATE>"

    lrpcc_config = {
        DEFINITION_URL: definition,
        TRANSPORT_TYPE: transport_type,
        TRANSPORT_PARAMS: transport_params,
    }
    with open(LRPCC_CONFIG_YAML, "wt") as lrpcc_config_file:
        yaml.safe_dump(lrpcc_config, lrpcc_config_file)

    print(f"Created file {LRPCC_CONFIG_YAML}")


class Lrpcc:
    def __init__(self, config) -> None:
        self.lrpc_def: LrpcDef = LrpcDef.load(config[DEFINITION_URL])
        self.client = LrpcClient(config[DEFINITION_URL])
        self.transport_type: str = config[TRANSPORT_TYPE]
        self.transport_params: dict = config[TRANSPORT_PARAMS]
        self.__communicate: callable = None

        if self.transport_type == "serial":
            self.__communicate: callable = self.__communicate_serial
        else:
            print(f"Unsupported transport type: {self.transport_type}")
            sys.exit(1)

    def __communicate_serial(self, encoded: bytes):
        with serial.Serial(**self.config[TRANSPORT_PARAMS]) as transport:
            transport.write(encoded)
            while True:
                received = transport.read(1)
                if len(received) == 0:
                    print("Timeout waiting for response")
                    break

                response = self.client.process(received)
                if response is not None:
                    return response

    def __command_handler(self, service_name: str, function_name: str, **kwargs):
        encoded = self.client.encode(service_name, function_name, **kwargs)
        response = self.__communicate(encoded)
        print(response)

    def run(self):
        cli = ClientCliVisitor(self.__command_handler)
        self.lrpc_def.accept(cli)
        cli.root()


def cli():
    config = __load_config()

    if config:
        Lrpcc(config).run()
    else:
        run_lrpcc_config_creator()


if __name__ == "__main__":
    cli()
