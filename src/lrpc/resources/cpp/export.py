from importlib import resources
from importlib.metadata import version
from pathlib import Path


def create_dir_if_not_exists(target_dir: Path) -> None:
    if not target_dir.exists():
        Path.mkdir(target_dir, 511, exist_ok=True)


def export(resource: str, output: Path) -> None:
    resource_path = resources.files(__package__).joinpath(resource)

    with (
        resources.as_file(resource_path) as resource_file,
        resource_file.open(encoding="utf8") as source,
        output.joinpath(resource_file.name).open(mode="w", encoding="utf-8") as dest,
    ):
        v = version("lotusrpc")
        dest.write(f"// This file has been generated with LRPC version {v}\n")

        dest.writelines(source.readlines())


def export_to(output: Path) -> None:
    core_dir = output.joinpath("lrpccore")
    create_dir_if_not_exists(core_dir)

    export("EtlRwExtensions.hpp", core_dir)
    export("Server.hpp", core_dir)
    export("Service.hpp", core_dir)
    export("MetaError.hpp", core_dir)
