from importlib import resources
from typing import Any

import yaml


def load_lrpc_schema() -> Any:
    schema_text = resources.files(__package__).joinpath("lotusrpc-schema.json").read_text()
    return yaml.safe_load(schema_text)
