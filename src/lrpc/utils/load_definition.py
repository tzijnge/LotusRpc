from collections.abc import Hashable
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Literal

import jsonschema
import mergedeep  # type: ignore[import-untyped]
import yaml

from lrpc.core import LrpcDef, LrpcDefDict
from lrpc.errors import LrpcDefinitionError
from lrpc.resources.meta import meta_def_file
from lrpc.schema import load_lrpc_schema
from lrpc.validation import SemanticAnalyzer

MergeStrategy = Literal["add", "replace"]

strategies: dict[MergeStrategy, mergedeep.Strategy] = {
    "add": mergedeep.Strategy.TYPESAFE_ADDITIVE,
    "replace": mergedeep.Strategy.TYPESAFE_REPLACE,
}


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


OverlayType = str | TextIOWrapper | Path


class DefinitionLoader:
    def __init__(
        self,
        *,
        warnings_as_errors: bool = True,
        include_meta_def: bool = True,
    ) -> None:
        self._warnings_as_errors = warnings_as_errors
        self._definition: LrpcDefDict = {}  # type: ignore[typeddict-item]

        if include_meta_def:
            self._add_meta()

    def add_overlay(self, overlay: OverlayType, merge_strategy: MergeStrategy) -> None:
        if isinstance(overlay, str):
            self._add_from_str(overlay, merge_strategy)
        elif isinstance(overlay, TextIOWrapper):
            self._add_from_file(overlay, merge_strategy)
        elif isinstance(overlay, Path):
            self._add_from_url(overlay, merge_strategy)
        else:
            raise TypeError(f"Unsupported overlay type: {type(overlay)}")

    def lrpc_def(self) -> LrpcDef:
        self._validate_definition()
        lrpc_def = LrpcDef(self._definition)
        sa = SemanticAnalyzer(lrpc_def)
        sa.analyze(warnings_as_errors=self._warnings_as_errors)

        return lrpc_def

    @staticmethod
    def _load_meta_def_dict() -> LrpcDefDict:
        with meta_def_file() as mdf, mdf.open(encoding="utf-8") as meta_def:
            return DefinitionLoader._yaml_safe_load(meta_def)

    def _validate_definition(self) -> None:
        try:
            jsonschema.validate(self._definition, load_lrpc_schema())
        except jsonschema.ValidationError as e:
            raise LrpcDefinitionError(e.message) from e

    @staticmethod
    def _yaml_safe_load(def_str: str | TextIO) -> LrpcDefDict:
        def_dict: LrpcDefDict = yaml.load(def_str, Loader=LrpcLoader)  # noqa: S506
        if not isinstance(def_dict, dict):
            raise TypeError("Invalid YAML input")

        return def_dict

    def _add_from_str(self, def_str: str, merge_strategy: MergeStrategy) -> None:
        user_def = self._yaml_safe_load(def_str)
        mergedeep.merge(self._definition, user_def, strategy=strategies[merge_strategy])

    def _add_from_url(self, def_url: Path, merge_strategy: MergeStrategy) -> None:
        with def_url.open(encoding="utf-8") as def_file:
            self._add_from_file(def_file, merge_strategy)

    def _add_from_file(self, def_file: TextIO, merge_strategy: MergeStrategy) -> None:
        user_def = self._yaml_safe_load(def_file)
        mergedeep.merge(self._definition, user_def, strategy=strategies[merge_strategy])

    def _add_meta(self) -> None:
        meta_def_dict = self._load_meta_def_dict()
        mergedeep.merge(self._definition, meta_def_dict, strategy=strategies["add"])


def load_lrpc_def(
    definition: OverlayType,
    *,
    warnings_as_errors: bool = True,
    include_meta_def: bool = True,
) -> LrpcDef:
    loader = DefinitionLoader(warnings_as_errors=warnings_as_errors, include_meta_def=include_meta_def)
    loader.add_overlay(definition, merge_strategy="add")
    return loader.lrpc_def()
