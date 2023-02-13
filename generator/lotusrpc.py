import click
from SematicAnalyzer import SemanticAnalyzer
from StructFileWriter import StructFileWriter
from EnumFileWriter import EnumFileWriter
from IncludeAllWriter import IncludeAllWriter
from DecoderShimWriter import DecoderShimWriter
import yaml
import jsonschema
import jsonschema.exceptions
from os import path
import os

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

def generate_structs(structs, output):
    for s in structs:
        sfw = StructFileWriter(s, structs, output)
        sfw.write()

def generate_enums(enums, output):
    for e in enums:
        sfw = EnumFileWriter(e, output)
        sfw.write()

def generate_include_all(rpc_name, structs, enums, output):
    writer = IncludeAllWriter(rpc_name, structs, enums, output)
    writer.write()

def generate_shims(services, structs, output):
    for i in services:
        writer = DecoderShimWriter(i, structs, output)
        writer.write()

def generate_rpc(input, output):
    create_dir_if_not_exists(output)

    definition = yaml.safe_load(input)

    structs = definition.get('structs', list())
    enums = definition.get('enums', list())

    generate_include_all(input.name, structs, enums, output)
    generate_structs(structs, output)
    generate_enums(enums, output)
    generate_shims(definition['services'], structs, output)

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