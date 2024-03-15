import click
from lrpc.codegen import StructFileVisitor, ConstantsFileVisitor, EnumFileVisitor, IncludeAllVisitor, ServiceShimVisitor, SemanticAnalyzer
from lrpc.core import LrpcDef
import yaml
import jsonschema
import jsonschema.exceptions
from os import path
import os
from lrpc import PlantUmlVisitor

def create_dir_if_not_exists(dir):
    if not path.exists(dir):
        os.makedirs(dir, 511, True)

def validate_yaml(definition, input: str):
    with open(f'{path.dirname(__file__)}/../../../misc/lotusrpc-schema.json', 'r') as schema_file:
        schema = yaml.safe_load(schema_file)

        try:
            jsonschema.validate(definition, schema)
            return False
        except jsonschema.exceptions.ValidationError as e:
            print('#' * 80)
            print(' LRPC definition parsing error '.center(80, '#'))
            print(f' {input.name} '.center(80, '#'))
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

    lrpc_def.accept(IncludeAllVisitor(output))
    lrpc_def.accept(StructFileVisitor(output))
    lrpc_def.accept(EnumFileVisitor(output))
    lrpc_def.accept(ServiceShimVisitor(output))
    lrpc_def.accept(ConstantsFileVisitor(output))
    lrpc_def.accept(PlantUmlVisitor())

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