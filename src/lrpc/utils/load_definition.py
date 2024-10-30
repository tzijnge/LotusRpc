from typing import TextIO, Union
import jsonschema
import yaml

from ..core import LrpcDef, LrpcDefDict
from ..schema import load_lrpc_schema
from ..validation import SemanticAnalyzer


def __yaml_safe_load(def_str: Union[str, TextIO]) -> LrpcDefDict:
    def_dict: LrpcDefDict = yaml.safe_load(def_str)
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
