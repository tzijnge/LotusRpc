import os
from importlib import resources
from os import path

import click
import jsonschema
import jsonschema.exceptions
import yaml
from lrpc import PlantUmlVisitor
from lrpc import schema as lrpc_schema
from lrpc.codegen import (ConstantsFileVisitor, EnumFileVisitor,
                          ServerIncludeVisitor, ServiceIncludeVisitor,
                          ServiceShimVisitor, StructFileVisitor)
from lrpc.core import LrpcDef
from lrpc.validation import SemanticAnalyzer


def create_dir_if_not_exists(target_dir):
    if not path.exists(target_dir):
        os.makedirs(target_dir, 511, True)

def validate_yaml(definition, input: str):
    url = resources.files(lrpc_schema) / 'lotusrpc-schema.json'
    with open(url, mode='rt', encoding='utf-8') as schema_file:
        schema = yaml.safe_load(schema_file)

        try:
            jsonschema.validate(definition, schema)
            return False
        except jsonschema.exceptions.ValidationError as e:
            print('#' * 80)
            print(' LRPC definition parsing error '.center(80, '#'))
            print(f' {input} '.center(80, '#'))
            print('#' * 80)
            print(e)
            return True

def validate_definition(lrpc_def: LrpcDef, warnings_as_errors: bool):
    errors_found = False

    sa = SemanticAnalyzer(lrpc_def)
    sa.analyze()

    if warnings_as_errors:
        for e in sa.errors + sa.warnings:
            errors_found = True
            print(f'Error: {e}')
    else:
        for w in sa.warnings:
            print(f'Warning: {w}')

    return errors_found

def generate_rpc(lrpc_def: LrpcDef, output: str):
    create_dir_if_not_exists(output)

    lrpc_def.accept(ServerIncludeVisitor(output))
    lrpc_def.accept(ServiceIncludeVisitor(output))
    lrpc_def.accept(StructFileVisitor(output))
    lrpc_def.accept(EnumFileVisitor(output))
    lrpc_def.accept(ServiceShimVisitor(output))
    lrpc_def.accept(ConstantsFileVisitor(output))
    lrpc_def.accept(PlantUmlVisitor(output))

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

    definition = yaml.safe_load(input)
    errors_found = validate_yaml(definition, input)
    if errors_found:
        return

    lrpc_def = LrpcDef(definition)
    errors_found = validate_definition(lrpc_def, warnings_as_errors)
    if not errors_found:
        input.seek(0)
        generate_rpc(lrpc_def, output)

if __name__ == "__main__":
    generate()
