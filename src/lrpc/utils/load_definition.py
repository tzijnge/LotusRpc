from typing import TextIO, Union, Any
from collections.abc import Hashable
import jsonschema
import yaml

from ..core import LrpcDef, LrpcDefDict
from ..schema import load_lrpc_schema
from ..validation import SemanticAnalyzer


# pylint: disable = too-many-ancestors
class LrpcLoader(yaml.SafeLoader):
    """Purpose of this class is to determine if functions are specified
    first or if streams are specified first in the definition file. The
    result is stored in `functions_before_streams`, unless that field
    has already been specified in the definition file"""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Hashable, Any]:
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


def __yaml_safe_load(def_str: Union[str, TextIO]) -> LrpcDefDict:
    def_dict: LrpcDefDict = yaml.load(def_str, Loader=LrpcLoader)
    if not isinstance(def_dict, dict):
        raise ValueError("Invalid YAML input")

    return def_dict


def load_lrpc_def_from_dict(definition: LrpcDefDict, warnings_as_errors: bool) -> LrpcDef:
    jsonschema.validate(definition, load_lrpc_schema())

    lrpc_def = LrpcDef(definition)
    sa = SemanticAnalyzer(lrpc_def)
    sa.analyze(warnings_as_errors)

    return lrpc_def


def load_lrpc_def_from_str(def_str: str, warnings_as_errors: bool) -> LrpcDef:
    def_dict = __yaml_safe_load(def_str)
    return load_lrpc_def_from_dict(def_dict, warnings_as_errors)


def load_lrpc_def_from_url(def_url: str, warnings_as_errors: bool) -> LrpcDef:
    with open(def_url, mode="rt", encoding="utf-8") as def_file:
        def_dict = __yaml_safe_load(def_file)
        return load_lrpc_def_from_dict(def_dict, warnings_as_errors)


def load_lrpc_def_from_file(def_file: TextIO, warnings_as_errors: bool) -> LrpcDef:
    def_dict = __yaml_safe_load(def_file)
    return load_lrpc_def_from_dict(def_dict, warnings_as_errors)
