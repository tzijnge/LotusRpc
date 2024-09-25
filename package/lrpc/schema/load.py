from importlib import resources
from typing import Any

import yaml
import lrpc.schema as lrpc_schema


def load_lrpc_schema() -> Any:
    schema_file = resources.files(lrpc_schema).joinpath("lotusrpc-schema.json")
    schema_text = schema_file.read_text()
    return yaml.safe_load(schema_text)
