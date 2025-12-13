from importlib import resources
from typing import ContextManager
from pathlib import Path


def load_meta_def() -> ContextManager[Path]:
    resource_path = resources.files(__package__).joinpath("meta.lrpc.yaml")
    return resources.as_file(resource_path)
