import click
from SematicAnalyzer import SemanticAnalyzer
from StructFileWriter import StructFileWriter
from EnumFileWriter import EnumFileWriter
from IncludeAllWriter import IncludeAllWriter
from ServiceShimWriter import ServiceShimWriter
import yaml
import jsonschema
import jsonschema.exceptions
from os import path
import os
from LrpcDef import LrpcDef

def create_dir_if_not_exists(dir):
    if not path.exists(dir):
        os.makedirs(dir, 511, True)

def check_input(input, warnings_as_errors):
    errors_found = False

    with open(f'{path.dirname(__file__)}/lotusrpc-schema.json', 'r') as schema_file:
        schema = yaml.safe_load(schema_file)

        definition = yaml.safe_load(input)
        try:
            jsonschema.validate(definition, schema)
        except jsonschema.exceptions.ValidationError as e:
            print('############################################')
            print(f'############### {input.name} ###############')
            print('############################################')
            print(e)

        sa = SemanticAnalyzer()
        sa.analyze(definition)

        if warnings_as_errors:
            for e in sa.errors + sa.warnings:
                errors_found = True
                print(f'Error: {e}')
        else:
            for w in sa.warnings:
                print(f'Warning: {w}')

    return errors_found

def generate_structs(lrpc_def: LrpcDef, output: str):
    for s in lrpc_def.structs():
        sfw = StructFileWriter(s, lrpc_def, output)
        sfw.write()

def generate_enums(lrpc_def: LrpcDef, output: str):
    for e in lrpc_def.enums():
        sfw = EnumFileWriter(e, lrpc_def, output)
        sfw.write()

def generate_include_all(lrpc_def: LrpcDef, output: str):
    writer = IncludeAllWriter(lrpc_def, output)
    writer.write()

def generate_shims(lrpc_def: LrpcDef, output: str):
    for s in lrpc_def.services():
        writer = ServiceShimWriter(s, lrpc_def, output)
        writer.write()

def generate_rpc(input: str, output: str):
    create_dir_if_not_exists(output)

    lrpc_def = LrpcDef(yaml.safe_load(input))

    generate_include_all(lrpc_def, output)
    generate_structs(lrpc_def, output)
    generate_enums(lrpc_def, output)
    generate_shims(lrpc_def, output)

@click.command()
@click.option('-w', '--warnings_as_errors',
                help='Treat warnings as errors',
                required=False,
                default=None,
                is_flag=True,
                type=str)
@click.option('-o', '--output',
                help='Path to put the generated files',
                required=False,
                default='.',
                type=click.Path())
@click.argument('input',
                type=click.File('r'))
def generate(warnings_as_errors, output, input):
    '''Generate code for file(s) INPUTS'''
    errors_found = check_input(input, warnings_as_errors)
    if not errors_found:
        input.seek(0)
        generate_rpc(input, output)

if __name__ == "__main__":
    generate()