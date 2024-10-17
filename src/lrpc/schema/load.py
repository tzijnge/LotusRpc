from importlib import resources
from typing import Any

import yaml


def load_lrpc_schema() -> dict[str, Any]:
    schema_file = resources.files(__package__).joinpath("lotusrpc-schema.json")
    schema_text = schema_file.read_text(encoding="utf-8")
    schema = yaml.safe_load(schema_text)

    if not isinstance(schema, dict):
        raise ValueError(f"Invalid YAML input for {schema_file.name}")

    return schema
