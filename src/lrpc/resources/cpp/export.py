from importlib import resources
from importlib.metadata import version
from pathlib import Path


def _create_dir_if_not_exists(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)


def _export(resource: str, output: Path) -> None:
    resource_path = resources.files(__package__).joinpath(resource)

    with (
        resources.as_file(resource_path) as resource_file,
        resource_file.open(encoding="utf8") as source,
        output.joinpath(resource_file.name).open(mode="w", encoding="utf-8") as dest,
    ):
        v = version("lotusrpc")
        dest.write(f"// This file has been generated with LRPC version {v}\n")
        dest.write(source.read())


def export_resources_to(output: Path) -> None:
    core_dir = output.joinpath("lrpccore")
    _create_dir_if_not_exists(core_dir)

    _export("EtlRwExtensions.hpp", core_dir)
    _export("Server.hpp", core_dir)
    _export("Service.hpp", core_dir)
    _export("MetaError.hpp", core_dir)
    _export("LrpcTypes.hpp", core_dir)
