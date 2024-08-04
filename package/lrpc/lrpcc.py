'''LRPC client CLI'''
from lrpc.core.definition import LrpcDef
from lrpc.client import ClientCliVisitor, LrpcClient
import serial
import sys
from glob import glob
import yaml
from os import path
import os
import click



# TODO:
# - Create schema for lrpcc.config.yaml
# - Introduce constants for often used strings in this file




def __load_config():
    configs = glob('**/lrpcc.config.yaml', recursive=True)
    if len(configs) == 0:
        if ('LRPCC_CONFIG' in os.environ):
            configs.append(os.environ['LRPCC_CONFIG'])
        else:
            return None

    config_url = path.abspath(configs[0])

    with open(config_url, 'rt') as config_file:
        config = yaml.safe_load(config_file)

    if 'definition_url' not in config:
        print(f'Missing field `definition_url` in {config_url}')
        return None

    if 'transport_type' not in config:
        print(f'Missing field `transport_type` in {config_url}')
        return None

    if 'transport_params' not in config:
        print(f'Missing field `transport_params` in {config_url}')
        return None

    if not path.isabs(config['definition_url']):
        config['definition_url'] = path.join(path.dirname(config_url), config['definition_url'])

    return config

@click.group()
def run_lrpcc_config_creator():
    '''
No or invalid config file found. lrpcc needs a configuration file
named lrpcc.config.yaml. See https://github.com/tzijnge/LotusRpc for
more information about the contents of the configuration file.
By default, lrpcc looks for the configuration file in the current
working directory and all subdirectories recursively. If no configuration
file is found, lrpcc tries to use the configuration file specified by
the LRPCC_CONFIG environment variable.

Use the CREATE command to create a new configuration file template
'''
    pass

@run_lrpcc_config_creator.command()
@click.option('-d', '--definition',
                type=click.Path(file_okay=True, dir_okay=False),
                required=True,
                help='Path to LRPC definition file, absolute or relative to current working directory')
@click.option('-t', '--transport_type',
                type=click.Choice(['serial']),
                required=True,
                help='lrpcc transport type')
def create(definition, transport_type: str):
    '''Create a new lrpcc configuration file template'''
    transport_params = {}

    if transport_type == 'serial':
        transport_params['port'] = '<PORT>'
        transport_params['baudrate'] = '<BAUDRATE>'

    lrpcc_config = {
        'definition_url': definition,
        'transport_type': transport_type,
        'transport_params': transport_params
    }
    with open('lrpcc.config.yaml', 'wt') as lrpcc_config_file:
        yaml.safe_dump(lrpcc_config, lrpcc_config_file)

    print('Created file lrpcc.config.yaml')

class Lrpcc:
    def __init__(self, config) -> None:
        self.lrpc_def: LrpcDef = LrpcDef.load(config['definition_url'])
        self.client = LrpcClient(config['definition_url'])
        self.transport_type: str = config['transport_type']
        self.transport_params: dict = config['transport_params']
        self.__communicate: callable = None

        if self.transport_type == 'serial':
            self.__communicate: callable = self.__communicate_serial
        else:
            print(f'Unsupported transport type: {self.transport_type}')
            sys.exit(1)

    def __communicate_serial(self, encoded: bytes):
        with serial.Serial(**self.config['transport_params']) as transport:
            transport.write(encoded)
            while True:
                received = transport.read(1)
                if len(received) == 0:
                    print('Timeout waiting for response')
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