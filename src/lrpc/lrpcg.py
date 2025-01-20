import logging
import os
from os import path
from typing import TextIO
import click
from lrpc.visitors import PlantUmlVisitor
from lrpc.codegen import (
    ConstantsFileVisitor,
    EnumFileVisitor,
    ServerIncludeVisitor,
    ServiceIncludeVisitor,
    ServiceShimVisitor,
    StructFileVisitor,
    MetaFileVisitor,
)
from lrpc.core import LrpcDef
from lrpc.utils import load_lrpc_def_from_file

logging.basicConfig(format="[LRPCC] %(levelname)-8s: %(message)s", level=logging.INFO)


def create_dir_if_not_exists(target_dir: os.PathLike[str]) -> None:
    if not path.exists(target_dir):
        os.makedirs(target_dir, 511, True)


def generate_rpc(lrpc_def: LrpcDef, output: os.PathLike[str]) -> None:
    create_dir_if_not_exists(output)

    lrpc_def.accept(ServerIncludeVisitor(output))
    lrpc_def.accept(ServiceIncludeVisitor(output))
    lrpc_def.accept(StructFileVisitor(output))
    lrpc_def.accept(EnumFileVisitor(output))
    lrpc_def.accept(ServiceShimVisitor(output))
    lrpc_def.accept(ConstantsFileVisitor(output))
    lrpc_def.accept(MetaFileVisitor(output))
    lrpc_def.accept(PlantUmlVisitor(output))


@click.command()
@click.version_option(package_name="lotusrpc", message="%(version)s")
@click.option(
    "-w", "--warnings_as_errors", help="Treat warnings as errors", required=False, default=None, is_flag=True, type=str
)
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
@click.argument("input_file", type=click.File("r"), metavar="input")
def run_cli(warnings_as_errors: bool, output: os.PathLike[str], input_file: TextIO) -> None:
    """Generate code for file INPUT"""

    try:
        lrpc_def = load_lrpc_def_from_file(input_file, warnings_as_errors)
        generate_rpc(lrpc_def, output)
        logging.info("Generated LRPC code for %s in %s", input_file.name, output)

    # catching general exception here is considered ok, because application will terminate
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logging.error("Error while generating code for %s", input_file.name)
        logging.error(type(e))
        logging.error(str(e))


if __name__ == "__main__":
    # parameters are inserted by Click
    # pylint: disable=no-value-for-parameter
    run_cli()
