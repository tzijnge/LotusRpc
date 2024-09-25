import os
from os import path
from typing import TextIO, Any

import click
import jsonschema
import jsonschema.exceptions
import yaml
from lrpc import PlantUmlVisitor
from lrpc.schema import load_lrpc_schema
from lrpc.codegen import (
    ConstantsFileVisitor,
    EnumFileVisitor,
    ServerIncludeVisitor,
    ServiceIncludeVisitor,
    ServiceShimVisitor,
    StructFileVisitor,
)
from lrpc.core import LrpcDef
from lrpc.validation import SemanticAnalyzer


def create_dir_if_not_exists(target_dir: os.PathLike) -> None:
    if not path.exists(target_dir):
        os.makedirs(target_dir, 511, True)


def validate_yaml(definition: dict[str, Any], input_file_name: str) -> bool:
    try:
        jsonschema.validate(definition, load_lrpc_schema())
        return False
    except jsonschema.exceptions.ValidationError as e:
        print("#" * 80)
        print(" LRPC definition parsing error ".center(80, "#"))
        print(f" {input_file_name} ".center(80, "#"))
        print("#" * 80)
        print(e)
        return True


def validate_definition(lrpc_def: LrpcDef, warnings_as_errors: bool) -> bool:
    errors_found = False

    sa = SemanticAnalyzer(lrpc_def)
    sa.analyze()

    if warnings_as_errors:
        for e in sa.errors + sa.warnings:
            errors_found = True
            print(f"Error: {e}")
    else:
        for w in sa.warnings:
            print(f"Warning: {w}")

    return errors_found


def generate_rpc(lrpc_def: LrpcDef, output: os.PathLike) -> None:
    create_dir_if_not_exists(output)

    lrpc_def.accept(ServerIncludeVisitor(output))
    lrpc_def.accept(ServiceIncludeVisitor(output))
    lrpc_def.accept(StructFileVisitor(output))
    lrpc_def.accept(EnumFileVisitor(output))
    lrpc_def.accept(ServiceShimVisitor(output))
    lrpc_def.accept(ConstantsFileVisitor(output))
    lrpc_def.accept(PlantUmlVisitor(output))


@click.command()
@click.option(
    "-w", "--warnings_as_errors", help="Treat warnings as errors", required=False, default=None, is_flag=True, type=str
)
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
@click.argument("input_file", type=click.File("r"), metavar="input")
def generate(warnings_as_errors: bool, output: os.PathLike, input_file: TextIO) -> None:
    """Generate code for file INPUT"""

    definition = yaml.safe_load(input_file)
    errors_found = validate_yaml(definition, input_file.name)
    if errors_found:
        return

    lrpc_def = LrpcDef(definition)
    errors_found = validate_definition(lrpc_def, warnings_as_errors)
    if not errors_found:
        input_file.seek(0)
        generate_rpc(lrpc_def, output)


if __name__ == "__main__":
    # parameters are inserted by Click
    # pylint: disable=no-value-for-parameter
    generate()
