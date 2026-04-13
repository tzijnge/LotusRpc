from collections.abc import Hashable, Iterator
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
        self._definition = self._base_yaml_documents(definition_base)
        self._warnings_as_errors = warnings_as_errors

        if include_meta_def:
            self._definition = merge_definition(self._definition, self._load_meta_def_dict())

    def save_to(self, file: TextIO) -> None:
        yaml.dump(self._definition, file, sort_keys=False)

    def add_overlay(self, overlay_source: LrpcDefDefSourceType) -> None:
        for overlay in self._overlay_yaml_documents(overlay_source):
            merge_definition(self._definition, overlay)

    def lrpc_def(self) -> LrpcDef:
        self._validate(self._definition)
        lrpc_def = LrpcDef(cast(LrpcDefDict, self._definition))
        sa = SemanticAnalyzer(lrpc_def)
        sa.analyze(warnings_as_errors=self._warnings_as_errors)

        return lrpc_def

    @staticmethod
    def _overlay_yaml_documents(overlays: LrpcDefDefSourceType) -> Iterator[YamlValues]:
        if isinstance(overlays, (str, TextIOWrapper)):
            return yaml.safe_load_all(overlays)
        if isinstance(overlays, Path):
            with overlays.open(encoding="utf-8") as overlays_file:
                return yaml.safe_load_all(overlays_file)

        raise TypeError(f"Unsupported overlay type: {type(overlays)}")

    @staticmethod
    def _base_yaml_documents(base: LrpcDefDefSourceType) -> YamlValues:
        if isinstance(base, (str, TextIOWrapper)):
            return DefinitionLoader._safe_load_base(base)
        if isinstance(base, Path):
            with base.open(encoding="utf-8") as def_file:
                return DefinitionLoader._safe_load_base(def_file)

        raise TypeError(f"Unsupported definition base type: {type(base)}")

    @staticmethod
    def _load_meta_def_dict() -> YamlValues:
        with meta_def_file() as mdf, mdf.open(encoding="utf-8") as meta_def:
            return cast(YamlValues, yaml.safe_load(meta_def))

    @staticmethod
    def _validate(definition: YamlValues) -> None:
        try:
            jsonschema.validate(definition, load_lrpc_schema())
        except jsonschema.ValidationError as e:
            raise LrpcDefinitionError(e.message) from e

    @staticmethod
    def _safe_load_base(base: str | TextIO) -> YamlValues:
        def_dict: YamlValues = yaml.load(base, Loader=LrpcLoader)  # noqa: S506
        if not isinstance(def_dict, dict):
            raise TypeError("Invalid YAML input")

        return def_dict


def load_lrpc_def(
    definition: LrpcDefDefSourceType,
    *,
    warnings_as_errors: bool = True,
    include_meta_def: bool = True,
) -> LrpcDef:
    loader = DefinitionLoader(definition, warnings_as_errors=warnings_as_errors, include_meta_def=include_meta_def)
    return loader.lrpc_def()
