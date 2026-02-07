from contextlib import AbstractContextManager
from importlib import resources
from pathlib import Path


def meta_def_file() -> AbstractContextManager[Path]:
    resource_path = resources.files(__package__).joinpath("meta.lrpc.yaml")
    return resources.as_file(resource_path)
