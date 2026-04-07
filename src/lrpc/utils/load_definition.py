from collections.abc import Hashable
from io import TextIOWrapper
from pathlib import Path
from typing import Any, TextIO, cast

import jsonschema
import yaml

from lrpc.core import LrpcDef, LrpcDefDict
from lrpc.errors import LrpcDefinitionError
from lrpc.resources.meta import meta_def_file
from lrpc.schema import load_lrpc_schema
from lrpc.validation import SemanticAnalyzer

from .overlay_merge import YamlValues, merge_definition


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


LrpcDefDefSourceType = str | TextIO | Path


class DefinitionLoader:
    def __init__(
        self,
        definition_base: LrpcDefDefSourceType,
        *,
        warnings_as_errors: bool = True,
        include_meta_def: bool = True,
    ) -> None:
        self._definition = self.create_definition(definition_base)
        self._warnings_as_errors = warnings_as_errors

        if include_meta_def:
            self._add_meta()

    def add_overlay(self, overlay: LrpcDefDefSourceType) -> None:
        if isinstance(overlay, str):
            self._add_from_str(overlay)
        elif isinstance(overlay, TextIOWrapper):
            self._add_from_file(overlay)
        elif isinstance(overlay, Path):
            self._add_from_url(overlay)
        else:
            raise TypeError(f"Unsupported overlay type: {type(overlay)}")

    def lrpc_def(self) -> LrpcDef:
        self._validate_definition()
        lrpc_def = LrpcDef(cast(LrpcDefDict, self._definition))
        sa = SemanticAnalyzer(lrpc_def)
        sa.analyze(warnings_as_errors=self._warnings_as_errors)

        return lrpc_def

    @staticmethod
    def _load_meta_def_dict() -> YamlValues:
        with meta_def_file() as mdf, mdf.open(encoding="utf-8") as meta_def:
            return DefinitionLoader._yaml_safe_load(meta_def)

    def _validate_definition(self) -> None:
        try:
            jsonschema.validate(self._definition, load_lrpc_schema())
        except jsonschema.ValidationError as e:
            raise LrpcDefinitionError(e.message) from e

    @staticmethod
    def _yaml_safe_load(def_str: str | TextIO) -> YamlValues:
        def_dict: YamlValues = yaml.load(def_str, Loader=LrpcLoader)  # noqa: S506
        if not isinstance(def_dict, dict):
            raise TypeError("Invalid YAML input")

        return def_dict

    def create_definition(self, definition_base: LrpcDefDefSourceType) -> YamlValues:
        if isinstance(definition_base, str):
            return self._load_from_str(definition_base)
        elif isinstance(definition_base, TextIOWrapper):
            return self._load_from_file(definition_base)
        elif isinstance(definition_base, Path):
            return self._load_from_url(definition_base)
        else:
            raise TypeError(f"Unsupported definition base type: {type(definition_base)}")

    def _load_from_str(self, def_str: str) -> YamlValues:
        return self._yaml_safe_load(def_str)

    def _load_from_url(self, def_url: Path) -> YamlValues:
        with def_url.open(encoding="utf-8") as def_file:
            return self._load_from_file(def_file)

    def _load_from_file(self, def_file: TextIO) -> YamlValues:
        return self._yaml_safe_load(def_file)

    def _add_from_str(self, def_str: str) -> None:
        self._definition = merge_definition(self._definition, self._load_from_str(def_str))

    def _add_from_url(self, def_url: Path) -> None:
        with def_url.open(encoding="utf-8") as def_file:
            self._add_from_file(def_file)

    def _add_from_file(self, def_file: TextIO) -> None:
        self._definition = merge_definition(self._definition, self._load_from_file(def_file))

    def _add_meta(self) -> None:
        meta_def_dict = self._load_meta_def_dict()
        self._definition = merge_definition(self._definition, meta_def_dict)


def load_lrpc_def(
    definition: LrpcDefDefSourceType,
    *,
    warnings_as_errors: bool = True,
    include_meta_def: bool = True,
) -> LrpcDef:
    loader = DefinitionLoader(definition, warnings_as_errors=warnings_as_errors, include_meta_def=include_meta_def)
    return loader.lrpc_def()
