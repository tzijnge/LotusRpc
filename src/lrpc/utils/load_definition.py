from collections.abc import Hashable
from pathlib import Path
from typing import Any, TextIO

import jsonschema
import yaml

from ..core import LrpcDef, LrpcDefDict
from ..resources.meta import load_meta_def
from ..schema import load_lrpc_schema
from ..validation import SemanticAnalyzer


# pylint: disable = too-many-ancestors
class LrpcLoader(yaml.SafeLoader):
    """Purpose of this class is to determine if functions are specified
    first or if streams are specified first in the definition file. The
    result is stored in `functions_before_streams`, unless that field
    has already been specified in the definition file"""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Hashable, Any]:  # noqa: FBT001, FBT002
        mapping = super().construct_mapping(node, deep=deep)

        if ("streams" not in mapping) and ("functions" not in mapping):
            return mapping

        if "functions_before_streams" in mapping:
            return mapping

        functions_index = float("inf")
        streams_index = float("inf")

        for sub_node in node.value:
            for sub_sub_node in sub_node:
                if sub_sub_node.value == "streams":
                    streams_index = sub_sub_node.start_mark.index
                if sub_sub_node.value == "functions":
                    functions_index = sub_sub_node.start_mark.index

        mapping["functions_before_streams"] = functions_index < streams_index

        return mapping


def __yaml_safe_load(def_str: str | TextIO) -> LrpcDefDict:
    def_dict: LrpcDefDict = yaml.load(def_str, Loader=LrpcLoader)  # noqa: S506
    if not isinstance(def_dict, dict):
        raise TypeError("Invalid YAML input")

    return def_dict


def __load_meta_def() -> LrpcDefDict:
    with load_meta_def() as meta_def, meta_def.open(encoding="utf-8") as meta_def_file:
        meta_def_dict = __yaml_safe_load(meta_def_file)
        jsonschema.validate(meta_def_dict, load_lrpc_schema())
        return meta_def_dict


def load_lrpc_def_from_dict(user_def: LrpcDefDict, meta_def: LrpcDefDict, *, warnings_as_errors: bool) -> LrpcDef:
    user_def["services"].extend(meta_def["services"])

    if "enums" not in meta_def:
        raise ValueError("meta definition is expected to have an error type enum")

    if "enums" in user_def:
        user_def["enums"].extend(meta_def["enums"])
    else:
        user_def["enums"] = meta_def["enums"]

    jsonschema.validate(user_def, load_lrpc_schema())

    lrpc_def = LrpcDef(user_def)
    sa = SemanticAnalyzer(lrpc_def)
    sa.analyze(warnings_as_errors=warnings_as_errors)

    return lrpc_def


def load_lrpc_def_from_str(def_str: str, *, warnings_as_errors: bool) -> LrpcDef:
    user_def = __yaml_safe_load(def_str)
    meta_def = __load_meta_def()
    return load_lrpc_def_from_dict(user_def, meta_def, warnings_as_errors=warnings_as_errors)


def load_lrpc_def_from_url(def_url: Path, *, warnings_as_errors: bool) -> LrpcDef:
    with def_url.open(encoding="utf-8") as def_file:
        return load_lrpc_def_from_file(def_file, warnings_as_errors=warnings_as_errors)


def load_lrpc_def_from_file(def_file: TextIO, *, warnings_as_errors: bool) -> LrpcDef:
    user_def = __yaml_safe_load(def_file)
    meta_def = __load_meta_def()
    return load_lrpc_def_from_dict(user_def, meta_def, warnings_as_errors=warnings_as_errors)
