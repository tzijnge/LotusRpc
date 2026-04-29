---
title: Definition overlays
toc: true
toc_icon: layer-group
---

## Overview

LotusRPC supports merging overlay definitions on top of a base definition. This lets you create variants of an interface without duplicating the entire base structure — for example, platform-specific or variant-specific interfaces that only differ in a few places.

## Overlay files

Overlay files are YAML files like the main definition file and typically also carry the `.lrpc.yaml` extension. An overlay follows the same structure as the base definition, but only describes the slice that is being modified. Every overlay (or section of an overlay) must also include a `merge_strategy` property.

Overlay files can contain multiple [YAML documents](https://yaml.org/spec/1.2.2/#91-documents) to specify several overlay actions in a single file.

Use overlays with `lrpcg` via the `-ov` flag:

``` bash
lrpcg cpp -d base.lrpc.yaml -ov overlay1.lrpc.yaml -ov overlay2.lrpc.yaml -o generated/
```

## Merge strategy

The `merge_strategy` property controls how overlay properties are applied. It is inherited from parent to child properties.

| Strategy  | Behavior                    | Precondition                    |
|-----------|-----------------------------|---------------------------------|
| `add`     | Add a property to the base  | Item does not exist in base[^1] |
| `remove`  | Remove a property from base | Item exists in base             |
| `replace` | Replace a property in base  | Item exists in base             |

[^1]: When adding a composite named item to a list, the item is added in full if no item with that name exists in the base. When an item with that name does exist, the merge is applied recursively to sub-properties.

- Composite properties (`add`, `remove`, `replace`) are matched by their `name` field.
- Basic list items (strings, integers) are matched by value.
- Replacing a basic list item directly is not supported; apply a `remove` followed by an `add`.
- A basic scalar property can also be removed by setting it to `null` without specifying a `merge_strategy`.
- A merge fails if the precondition is not met.

## Example 1: Adding a parameter

Base definition:

``` yaml
name: overlay_example
settings:
  namespace: ov_ex
services:
  - name: MyService
    functions:
      - name: DoWork
        params:
          - name: timeout
            type: uint32_t
```

Overlay:

``` yaml
services:
  - name: MyService
    functions:
      - name: DoWork
        params:
          - name: retries
            type: uint8_t
        merge_strategy: add
```

Result: `DoWork` now has both `timeout` and `retries` parameters.

## Example 2: Removing a parameter

Overlay:

``` yaml
services:
  - name: MyService
    functions:
      - name: DoWork
        params:
          - name: timeout
            merge_strategy: remove
```

Result: `DoWork` no longer has the `timeout` parameter.

## Example 3: Removing a property with null

Overlay:

``` yaml
settings:
  namespace: null
```

Result: The `namespace` setting is removed; code is generated in the global namespace.

## Example 4: Replacing an entire service

Overlay:

``` yaml
services:
  - name: MyService
    functions:
      - name: NewFunction
    merge_strategy: replace
```

Result: `MyService` is completely replaced; all previous functions are removed.
