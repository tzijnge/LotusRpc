import logging
import os
import traceback
from pathlib import Path
from typing import TextIO

import click

from lrpc.codegen import (
    ConstantsFileVisitor,
    EnumFileVisitor,
    MetaServiceVisitor,
    ServerIncludeVisitor,
    ServiceIncludeVisitor,
    ServiceShimVisitor,
    StructFileVisitor,
)
from lrpc.core import LrpcDef
from lrpc.resources.cpp import export_to
from lrpc.schema import export_lrpc_schema
from lrpc.utils import load_lrpc_def_from_file
from lrpc.visitors import PlantUmlVisitor

# pylint: disable=anomalous-backslash-in-string

logging.basicConfig(format="[LRPCG] %(levelname)-8s: %(message)s", level=logging.INFO)
log = logging.getLogger("LRPCG")


def create_dir_if_not_exists(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)


def copy_resources(output: Path) -> None:
    export_to(output)


def generate_rpc(lrpc_def: LrpcDef, output: Path, *, generate_core: bool) -> None:
    create_dir_if_not_exists(output)

    if generate_core:
        copy_resources(output)

    lrpc_def.accept(ServerIncludeVisitor(output))
    lrpc_def.accept(ServiceIncludeVisitor(output))
    lrpc_def.accept(StructFileVisitor(output))
    lrpc_def.accept(EnumFileVisitor(output))
    lrpc_def.accept(ServiceShimVisitor(output))
    lrpc_def.accept(ConstantsFileVisitor(output))
    lrpc_def.accept(MetaServiceVisitor(output))


def generate_puml(lrpc_def: LrpcDef, output: Path) -> None:
    create_dir_if_not_exists(output)
    lrpc_def.accept(PlantUmlVisitor(output))


@click.group()
@click.version_option(package_name="lotusrpc", message="%(version)s")
def run_cli() -> None:
    """\b
        __          __             ____  ____  ______
       / /   ____  / /___  _______/ __ \\/ __ \\/ ____/
      / /   / __ \\/ __/ / / / ___/ /_/ / /_/ / /
     / /___/ /_/ / /_/ /_/ (__  ) _, _/ ____/ /___
    /_____/\\____/\\__/\\__,_/____/_/ |_/_/    \\____/

    lrpcg is the LotusRPC generator tool. See
    https://tzijnge.github.io/LotusRpc/tools/#lrpcg for
    more information.
    """
    # All functionality provided by Click decorators


@run_cli.command()
@click.option("-d", "--definition_file", help="LRPC definition file", required=True, type=click.File("r"))
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
@click.option("--core/--no-core", help="Generate LRPC core files", required=False, default=True, type=bool)
@click.option(
    "-w",
    "--warnings_as_errors",
    help="Treat LRPC definition warnings as errors",
    required=False,
    default=False,
    is_flag=True,
    type=bool,
)
def cpp(definition_file: TextIO, output: str, core: bool, warnings_as_errors: bool) -> None:  # noqa: FBT001
    """Generate C++ server code for the specified lrpc definition file"""

    try:
        lrpc_def = load_lrpc_def_from_file(definition_file, warnings_as_errors=warnings_as_errors)
        generate_rpc(lrpc_def, Path(output), generate_core=core)
        log.info("Generated LRPC code for %s in %s", definition_file.name, output)

    # catching general exception here is considered ok, because application will terminate
    # pylint: disable=broad-exception-caught
    except Exception:
        log.exception("Error while generating code for %s", definition_file.name)

        traceback.print_exc()


@run_cli.command()
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
def cppcore(output: os.PathLike[str]) -> None:
    """Generate C++ server core files. Generating these files separately from the rest of the server
    allows for having multiple servers in a single project without conflicting and/or duplicate files.
    Use in combination with the 'cpp' command and the '--no-core' option"""
    copy_resources(Path(output))
    log.info("Generated LRPC core code in %s", output)


@run_cli.command()
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
def schema(output: os.PathLike[str]) -> None:
    """Export the schema for the LRPC definition file"""
    create_dir_if_not_exists(Path(output))
    export_lrpc_schema(Path(output))
    log.info("Exported LRPC schema to %s", output)


@run_cli.command()
@click.option("-d", "--definition_file", help="LRPC definition file", required=True, type=click.File("r"))
@click.option(
    "-w",
    "--warnings_as_errors",
    help="Treat LRPC definition warnings as errors",
    required=False,
    default=False,
    is_flag=True,
    type=bool,
)
@click.option("-o", "--output", help="Path to put the generated files", required=False, default=".", type=click.Path())
def puml(definition_file: TextIO, warnings_as_errors: bool, output: os.PathLike[str]) -> None:  # noqa: FBT001
    """Generate a PlantUML diagram for lrpc definition INPUT"""

    lrpc_def = load_lrpc_def_from_file(definition_file, warnings_as_errors=warnings_as_errors)
    generate_puml(lrpc_def, Path(output))
    log.info("Generated PlantUML diagram for %s in %s", definition_file.name, output)


if __name__ == "__main__":
    run_cli()
