from contextlib import suppress
from typing import Literal

YamlValue = bool | int | float | str | None
YamlValues = YamlValue | list["YamlValues"] | dict[str, "YamlValues"]

MergeStrategy = Literal["add", "remove", "replace"]


def merge_definition(
    base: YamlValues,
    overlay: YamlValues,
    default_operation: MergeStrategy = "add",
) -> YamlValues:
    if not isinstance(base, dict):
        raise TypeError("base must be a dict")
    if not isinstance(overlay, dict):
        raise TypeError("overlay must be a dict")

    result = _merge_values(base, overlay, default_operation)
    return _strip_nulls(result)


def _merge_values(
    base: YamlValues,
    overlay: YamlValues,
    operation: MergeStrategy = "add",
) -> YamlValues:
    if isinstance(overlay, dict):
        if not isinstance(base, dict):
            return overlay

        overlay_copy = dict(overlay)
        current_operation: MergeStrategy = overlay_copy.pop("merge_strategy", operation)

        if current_operation == "replace":
            return overlay_copy
        result = dict(base)
        for key, overlay_value in overlay_copy.items():
            if isinstance(overlay_value, dict):
                result[key] = _merge_values(result[key], overlay_value, current_operation)
            elif isinstance(overlay_value, list):
                result_value = result[key]
                if not isinstance(result_value, list):
                    result[key] = list(overlay_value)
                else:
                    result[key] = _merge_lists(result_value, overlay_value, current_operation)
            else:
                result[key] = overlay_value
        return result

    if isinstance(overlay, list):
        if not isinstance(base, list):
            return list(overlay)
        return _merge_lists(base, overlay, operation)

    return overlay


def _merge_lists(
    base: list[YamlValues],
    overlay: list[YamlValues],
    operation: MergeStrategy = "add",
) -> list[YamlValues]:
    if operation == "replace":
        return list(overlay)
    if operation == "remove":
        return _remove_items_from_list(base, overlay)
    return _add_items_to_list(base, overlay)


def _add_items_to_list(base: list[YamlValues], overlay: list[YamlValues]) -> list[YamlValues]:
    result = list(base)

    for overlay_item in overlay:
        if isinstance(overlay_item, dict) and "name" in overlay_item:
            item_copy = dict(overlay_item)
            item_operation = item_copy.pop("merge_strategy", "add")

            if item_operation == "remove":
                name = overlay_item["name"]
                result = [item for item in result if not (isinstance(item, dict) and item.get("name") == name)]
                continue

            if item_operation == "replace":
                name = overlay_item["name"]
                found = False
                for i, base_item in enumerate(result):
                    if isinstance(base_item, dict) and base_item.get("name") == name:
                        result[i] = item_copy
                        found = True
                        break
                if not found:
                    result.append(item_copy)
                continue

            name = overlay_item["name"]
            found = False
            for i, base_item in enumerate(result):
                if isinstance(base_item, dict) and base_item.get("name") == name:
                    result[i] = _merge_values(base_item, item_copy, "add")
                    found = True
                    break
            if not found:
                result.append(item_copy)
        else:
            result.append(overlay_item)

    return result


def _remove_items_from_list(base: list[YamlValues], overlay: list[YamlValues]) -> list[YamlValues]:
    result = list(base)

    for overlay_item in overlay:
        if isinstance(overlay_item, dict) and "name" in overlay_item:
            name = overlay_item["name"]
            result = [item for item in result if not (isinstance(item, dict) and item.get("name") == name)]
        else:
            with suppress(ValueError):
                result.remove(overlay_item)

    return result


def _strip_nulls(value: YamlValues) -> YamlValues:
    if isinstance(value, dict):
        return {k: _strip_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, (list, tuple)):
        return [_strip_nulls(v) for v in value if v is not None]
    return value
