'''LRPC client CLI'''
from lrpc.core.definition import LrpcDef
from lrpc.client import ClientCliVisitor, LrpcClient
import serial
import sys
from glob import glob
import yaml
from os import path
import os

class Lrpcc:
    def __init__(self) -> None:
        self.config: dict = {}
        self.__communicate: callable = None

    def __communicate_serial(self, client: LrpcClient, encoded: bytes):
        with serial.Serial(**self.config['transport_params']) as transport:
            transport.write(encoded)
            while True:
                received = transport.read(1)
                if len(received) == 0:
                    print('Timeout waiting for response')
                    break

                response = client.process(received)
                if response is not None:
                    return response

    def __command_handler(self, service_name: str, function_name: str, **kwargs):
        client = LrpcClient(self.config['definition_url'])
        encoded = client.encode(service_name, function_name, **kwargs)

        response = self.__communicate(client, encoded)
        print(response)


    def __show_help(self) -> None:
        help = '''
No or invalid config file found. lrpcc needs a configuration file
named lrpcc.config.yaml. See https://github.com/tzijnge/LotusRpc for
more information about the contents of the configuration file.
By default, lrpcc looks for the configuration file in the current
working directory and all subdirectories recursively. If no configuration
file is found, lrpcc tries to use the configuration file specified by
the LRPCC_CONFIG environment variable. 
'''
        print(help)

    def __load_config(self):
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

    def run(self):
        self.config = self.__load_config()

        if not self.config:
            self.__show_help()
            sys.exit(1)

        if self.config['transport_type'] == 'serial':
            self.__communicate = self.__communicate_serial
        else:
            print(f'Unsupported transport type: {self.config["transport_type"]}')
            sys.exit(1)

        lrpc_def: LrpcDef = LrpcDef.load(self.config['definition_url'])
        cli = ClientCliVisitor(self.__command_handler)
        lrpc_def.accept(cli)
        cli.root()

def cli():
    Lrpcc().run()

if __name__ == "__main__":
    cli()