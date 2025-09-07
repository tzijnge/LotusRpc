from importlib import resources
from importlib.metadata import version
import os
from os import path


def create_dir_if_not_exists(target_dir: str) -> None:
    if not path.exists(target_dir):
        os.makedirs(target_dir, 511, True)


def export(resource: str, output: str) -> None:
    resource_path = resources.files(__package__).joinpath(resource)

    with resources.as_file(resource_path) as resource_file:
        with open(resource_file, mode="rt", encoding="utf8") as source:
            with open(path.join(output, resource_file.name), mode="wt", encoding="utf-8") as dest:
                v = version("lotusrpc")
                dest.write(f"// This file has been generated with LRPC version {v}\n")

                for l in source.readlines():
                    dest.write(l)


def export_to(output: os.PathLike[str]) -> None:
    core_dir = path.join(output, "lrpccore")
    create_dir_if_not_exists(core_dir)

    export("EtlRwExtensions.hpp", core_dir)
    export("Server.hpp", core_dir)
    export("Service.hpp", core_dir)
