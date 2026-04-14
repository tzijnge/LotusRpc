from copy import deepcopy
from typing import Literal, cast, get_args

YamlValue = bool | int | float | str | None
YamlValues = YamlValue | list["YamlValues"] | dict[str, "YamlValues"]

MergeStrategy = Literal["add", "remove", "replace", "unspecified"]


def merge_definition(
    base: YamlValues,
    overlay: YamlValues,
) -> YamlValues:
    if not isinstance(base, dict):
        raise TypeError("base must be a dict")
    if not isinstance(overlay, dict):
        raise TypeError("overlay must be a dict")

    base_copy = deepcopy(base)
    overlay_copy = deepcopy(overlay)

    return _strip_nulls(_merge_dicts(base_copy, overlay_copy, "unspecified"))


def _merge_values(base: YamlValues, overlay: YamlValues, strategy: MergeStrategy) -> YamlValues:
    if isinstance(base, dict) and isinstance(overlay, dict):
        return _merge_dicts(base, overlay, strategy)

    if isinstance(base, list) and isinstance(overlay, list):
        return _merge_lists(base, overlay, strategy)

    raise TypeError(f"Unable to merge type '{type(base).__name__}' and type '{type(overlay).__name__}'")


def _merge_dicts(
    base: dict[str, YamlValues],
    overlay: dict[str, YamlValues],
    strategy: MergeStrategy,
) -> dict[str, YamlValues]:
    if strategy == "replace":
        return overlay

    new_strategy = _pop_strategy(overlay, strategy)
    for key, overlay_value in overlay.items():
        if isinstance(overlay_value, (dict, list)):
            base_value = base.get(key, type(overlay_value)())
            base[key] = _merge_values(base_value, overlay_value, new_strategy)
        else:
            base_value = base.get(key)
            base[key] = _merge_basic_item(key, base_value, overlay_value, new_strategy)
    return base


def _merge_lists(base: list[YamlValues], overlay: list[YamlValues], strategy: MergeStrategy) -> list[YamlValues]:
    if strategy == "replace":
        return overlay

    for overlay_item in overlay:
        if isinstance(overlay_item, list):
            raise NotImplementedError("Cannot merge list of list")
        if isinstance(overlay_item, dict):
            item_name = _get_name(overlay_item)
            item_strategy = _pop_strategy(overlay_item, strategy)
            base = _merge_list_of_named_composites(base, overlay_item, item_name, item_strategy)
        else:
            base = _merge_list_of_basic_items(base, overlay_item, strategy)
    return base


def _merge_list_of_named_composites(
    base: list[YamlValues],
    overlay_item: YamlValues,
    overlay_item_name: str,
    strategy: MergeStrategy,
) -> list[YamlValues]:
    base_item, index = _named_composite_from_list(base, overlay_item_name)

    if strategy in {"unspecified", "replace"}:
        if base_item is not None:
            base[index] = _merge_values(base_item, overlay_item, strategy)
        else:
            raise ValueError(f"Item {overlay_item_name} not found in base. Strategy is '{strategy}'")

    elif strategy == "remove":
        if base_item is not None:
            base.pop(index)
        else:
            raise ValueError(f"Item {overlay_item_name} not found in base. Strategy is '{strategy}'")

    # Strategy is add
    elif base_item is not None:
        base[index] = _merge_values(base_item, overlay_item, strategy)
    else:
        base.append(overlay_item)

    return base


def _merge_basic_item(key: str, base: YamlValues, overlay: YamlValues, strategy: MergeStrategy) -> YamlValues:
    if key == "name":
        # Property 'name' does not take part in merging
        return base

    if strategy == "unspecified":
        if overlay is None:
            # Remove basic item from base by assigning value None
            return None
        raise ValueError(f"Unable to merge '{key}' without merge strategy")

    if strategy == "add":
        if base is not None:
            raise ValueError(f"Property '{key}' cannot be added because it already exists in base")
        return overlay

    if base is None:
        raise ValueError(f"Overlay property '{key}' not found in base")

    if strategy == "remove":
        return None

    # strategy is replace
    return overlay


def _merge_list_of_basic_items(
    base: list[YamlValues],
    overlay_item: YamlValues,
    strategy: MergeStrategy,
) -> list[YamlValues]:
    if strategy == "unspecified":
        raise ValueError("Merge strategy not specified")

    if strategy == "remove":
        return [base_item for base_item in base if base_item != overlay_item]

    base.append(overlay_item)
    return base


def _strip_nulls(value: YamlValues) -> YamlValues:
    if isinstance(value, dict):
        return {k: _strip_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, (list, tuple)):
        return [_strip_nulls(v) for v in value if v is not None]
    return value


def _pop_strategy(item: dict[str, YamlValues], default: MergeStrategy = "unspecified") -> MergeStrategy:
    strategy = item.pop("merge_strategy", default)
    if not isinstance(strategy, str):
        raise TypeError(f"Invalid merge_strategy type. Expected 'str' but got '{type(strategy).__name__}'")

    if strategy not in get_args(MergeStrategy):
        raise ValueError(f"merge_strategy must be one of {get_args(MergeStrategy)}")

    return cast(MergeStrategy, strategy)


def _get_name(item: dict[str, YamlValues]) -> str:
    if "name" not in item:
        raise ValueError("Property 'name' not found")

    name = item["name"]

    if not isinstance(name, str):
        raise TypeError(f"Property 'name' is '{type(name).__name__}' instead of 'str'")

    return name


def _composite_has_name(item: YamlValues, name: str) -> bool:
    return isinstance(item, dict) and (_get_name(item) == name)


def _named_composite_from_list(subject: list[YamlValues], name: str) -> tuple[YamlValues, int]:
    for i, s in enumerate(subject):
        if _composite_has_name(s, name):
            return s, i

    return None, 0
