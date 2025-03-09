import logging
import os
import traceback
from os import path
from typing import TextIO

import click

from lrpc.codegen import (ConstantsFileVisitor, EnumFileVisitor,
                          MetaFileVisitor, ServerIncludeVisitor,
                          ServiceIncludeVisitor, ServiceShimVisitor,
                          StructFileVisitor)
from lrpc.core import LrpcDef
from lrpc.resources.cpp import export_to
from lrpc.utils import load_lrpc_def_from_file
from lrpc.visitors import PlantUmlVisitor

logging.basicConfig(format="[LRPCG] %(levelname)-8s: %(message)s", level=logging.INFO)


def create_dir_if_not_exists(target_dir: os.PathLike[str]) -> None:
    if not path.exists(target_dir):
        os.makedirs(target_dir, 511, True)

def copy_resources(output: os.PathLike[str]) -> None:
    export_to(output)

def generate_rpc(lrpc_def: LrpcDef, output: os.PathLike[str]) -> None:
    create_dir_if_not_exists(output)

    lrpc_def.accept(ServerIncludeVisitor(output))
    lrpc_def.accept(ServiceIncludeVisitor(output))
    lrpc_def.accept(StructFileVisitor(output))
    lrpc_def.accept(EnumFileVisitor(output))
    lrpc_def.accept(ServiceShimVisitor(output))
    lrpc_def.accept(ConstantsFileVisitor(output))
    lrpc_def.accept(MetaFileVisitor(output))

    copy_resources(output)

def generate_puml(lrpc_def: LrpcDef, output: os.PathLike[str]) -> None:
    create_dir_if_not_exists(output)
    lrpc_def.accept(PlantUmlVisitor(output))


@click.group()
@click.version_option(package_name="lotusrpc", message="%(version)s")
def run_cli() -> None:
    pass

@run_cli.command()
@click.option("-d", "--definition_file", help="LRPC definition file", required = True, type=click.File("r"))
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
@click.option(
    "-w", "--warnings_as_errors", help="Treat warnings as errors", required=False, default=False, is_flag=True, type=bool
)
def cpp(definition_file: TextIO, output: os.PathLike[str], warnings_as_errors: bool) -> None:
    """Generate C++ server code for the specified lrpc definition file"""

    try:
        lrpc_def = load_lrpc_def_from_file(definition_file, warnings_as_errors)
        generate_rpc(lrpc_def, output)
        logging.info("Generated LRPC code for %s in %s", definition_file.name, output)

    # catching general exception here is considered ok, because application will terminate
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logging.error("Error while generating code for %s", definition_file.name)
        logging.error(type(e))
        logging.error(str(e))

        traceback.print_exc()

@run_cli.command()
@click.option(
    "-w", "--warnings_as_errors", help="Treat warnings as errors", required=False, default=False, is_flag=True, type=bool
)
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
@click.argument("input_file", type=click.File("r"), metavar="input")
def puml(warnings_as_errors: bool, output: os.PathLike[str], input_file: TextIO) -> None:
    "Generate a PlantUML diagram for lrpc definition INPUT"""

    lrpc_def = load_lrpc_def_from_file(input_file, warnings_as_errors)
    generate_puml(lrpc_def, output)
    logging.info("Generated PlantUML diagram for %s in %s", input_file.name, output)

if __name__ == "__main__":
    # parameters are inserted by Click
    # pylint: disable=no-value-for-parameter
    run_cli()
