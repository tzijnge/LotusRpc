from importlib import resources
import shutil
import os
from os import path

def create_dir_if_not_exists(target_dir: str) -> None:
    if not path.exists(target_dir):
        os.makedirs(target_dir, 511, True)

def export(resource: str, output: str) -> None:
    resource_file = resources.files(__package__).joinpath(resource)

    with resources.as_file(resource_file) as f:
        shutil.copy2(f, path.join(output, resource_file.name))

def export_to(output: os.PathLike[str]) -> None:
    core_dir = path.join(output, "lrpccore")
    create_dir_if_not_exists(core_dir)

    export("EtlRwExtensions.hpp", core_dir)
    export("Server.hpp", core_dir)
    export("Service.hpp", core_dir)
