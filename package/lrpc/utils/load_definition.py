import jsonschema
import yaml

from ..core import LrpcDef
from ..schema import load_lrpc_schema
from ..validation import SemanticAnalyzer


def load_lrpc_def(definition_url: str) -> LrpcDef:

    with open(definition_url, mode="rt", encoding="utf-8") as rpc_def:
        definition = yaml.safe_load(rpc_def)
        jsonschema.validate(definition, load_lrpc_schema())

        lrpc_def = LrpcDef(definition)
        sa = SemanticAnalyzer(lrpc_def)
        sa.analyze()

        assert len(sa.errors) == 0
        assert len(sa.warnings) == 0

        return lrpc_def
