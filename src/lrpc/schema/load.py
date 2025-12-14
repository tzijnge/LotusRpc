import shutil
from importlib import resources
from pathlib import Path
from typing import Any

import yaml


def export_lrpc_schema(output: Path) -> None:
    schema_file = resources.files(__package__).joinpath("lotusrpc-schema.json")

    with resources.as_file(schema_file) as f:
        shutil.copy2(f, output.joinpath(schema_file.name))


def load_lrpc_schema() -> dict[str, Any]:
    schema_file = resources.files(__package__).joinpath("lotusrpc-schema.json")
    schema_text = schema_file.read_text(encoding="utf-8")
    schema = yaml.safe_load(schema_text)

    if not isinstance(schema, dict):
        raise TypeError(f"Invalid YAML input for {schema_file.name}")

    return schema
