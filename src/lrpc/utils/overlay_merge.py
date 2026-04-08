from copy import deepcopy
from typing import Literal, cast, get_args

YamlValue = bool | int | float | str | None
YamlValues = YamlValue | list["YamlValues"] | dict[str, "YamlValues"]

MergeStrategy = Literal["add", "remove", "replace"]


def merge_definition(
    base: YamlValues,
    overlay: YamlValues,
    strategy: MergeStrategy = "add",
) -> YamlValues:
    if not isinstance(base, dict):
        raise TypeError("base must be a dict")
    if not isinstance(overlay, dict):
        raise TypeError("overlay must be a dict")

    base_copy = deepcopy(base)
    overlay_copy = deepcopy(overlay)

    return _strip_nulls(_merge_values(base_copy, overlay_copy, strategy))


def _merge_values(base: YamlValues, overlay: YamlValues, strategy: MergeStrategy) -> YamlValues:
    if isinstance(overlay, dict):
        if not isinstance(base, dict):
            return overlay
        return _merge_dicts(base, overlay, strategy)

    if isinstance(overlay, list):
        if not isinstance(base, list):
            return overlay
        return _merge_lists(base, overlay, strategy)

    return overlay


def _pop_strategy(item: dict[str, YamlValues], default: MergeStrategy = "add") -> MergeStrategy:
    strategy = item.pop("merge_strategy", default)
    if not isinstance(strategy, str):
        raise TypeError("merge_strategy must be a string")

    if strategy not in get_args(MergeStrategy):
        raise ValueError(f"merge_strategy must be one of {get_args(MergeStrategy)}")

    return cast(MergeStrategy, strategy)


def _get_name(item: dict[str, YamlValues]) -> str:
    if "name" not in item:
        raise ValueError("Expected property 'name' not found")

    name = item["name"]

    if not isinstance(name, str):
        raise TypeError("Property 'name' must be a string")

    return name


def _is_named_composite(item: YamlValues) -> bool:
    return isinstance(item, dict) and "name" in item


def _composite_has_name(item: YamlValues, expected_name: str) -> bool:
    return isinstance(item, dict) and (_get_name(item) == expected_name)


def _merge_dicts(
    base: dict[str, YamlValues],
    overlay: dict[str, YamlValues],
    strategy: MergeStrategy,
) -> dict[str, YamlValues]:
    if strategy == "replace":
        return overlay

    new_strategy = _pop_strategy(overlay, strategy)
    for key, overlay_value in overlay.items():
        if isinstance(overlay_value, dict):
            base_value = base.get(key, {})
            base[key] = _merge_values(base_value, overlay_value, new_strategy)
        elif isinstance(overlay_value, list):
            base_value = base.get(key, [])
            if isinstance(base_value, list):
                base[key] = _merge_values(base_value, overlay_value, new_strategy)
            else:
                base[key] = overlay_value
        else:
            base[key] = overlay_value
    return base


def _merge_lists(base: list[YamlValues], overlay: list[YamlValues], strategy: MergeStrategy) -> list[YamlValues]:
    if strategy == "replace":
        return overlay
    if strategy == "remove":
        return _remove_items_from_list(base, overlay)

    return _merge_items_into_list(base, overlay)


def _merge_items_into_list(base: list[YamlValues], overlay: list[YamlValues]) -> list[YamlValues]:
    for overlay_item in overlay:
        if _is_named_composite(overlay_item):
            # type of overlay_item verified in _is_composite_name
            item_strategy = _pop_strategy(overlay_item, "add")  # type: ignore[arg-type]
            item_name = _get_name(overlay_item)  # type: ignore[arg-type]
            base = _apply_item_strategy(base, overlay_item, item_name, item_strategy)
        else:
            base.append(overlay_item)
    return base


def _apply_item_strategy(
    base: list[YamlValues],
    overlay_item: YamlValues,
    overlay_item_name: str,
    strategy: MergeStrategy,
) -> list[YamlValues]:
    if strategy == "remove":
        return [base_item for base_item in base if not _composite_has_name(base_item, overlay_item_name)]

    if strategy == "replace":
        for i, base_item in enumerate(base):
            if _composite_has_name(base_item, overlay_item_name):
                base[i] = overlay_item
                return base
        base.append(overlay_item)
        return base

    for i, base_item in enumerate(base):
        if _composite_has_name(base_item, overlay_item_name):
            base[i] = _merge_values(base_item, overlay_item, strategy)
            return base
    base.append(overlay_item)
    return base


def _remove_items_from_list(base: list[YamlValues], overlay: list[YamlValues]) -> list[YamlValues]:
    for overlay_item in overlay:
        if _is_named_composite(overlay_item):
            # type of overlay_item verified in _is_composite_name
            name = _get_name(overlay_item)  # type: ignore[arg-type]
            base = [item for item in base if not _composite_has_name(item, name)]
        elif overlay_item in base:
            base.remove(overlay_item)

    return base


def _strip_nulls(value: YamlValues) -> YamlValues:
    if isinstance(value, dict):
        return {k: _strip_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, (list, tuple)):
        return [_strip_nulls(v) for v in value if v is not None]
    return value
