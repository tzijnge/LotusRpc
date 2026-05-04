---
title: Python definition model
toc: true
toc_icon: sitemap
---

**Audience:** This page is for Python developers who need to read, inspect, or query a LotusRPC interface definition from code.
{: .notice--info}

## Overview

LotusRPC parses a definition file into a tree of Python objects rooted at `LrpcDef`. These objects can be queried directly — no visitor pattern required — and they are also the arguments passed to visitor methods when walking the full definition tree.

``` python
from lrpc.utils import load_lrpc_def
from lrpc.core import LrpcDef, LrpcService, LrpcFun, LrpcStream, LrpcVar
from lrpc.core import LrpcStruct, LrpcEnum, LrpcEnumField, LrpcConstant, RpcSettings
```

For walking the entire definition tree, see [Python visitor API](visitor.md).

## Loading a definition

Use `load_lrpc_def` to parse a definition file into an `LrpcDef` object:

``` python
from lrpc.utils import load_lrpc_def

lrpc_def = load_lrpc_def("example.lrpc.yaml")
```

The `definition` argument accepts a file path (`str` or `Path`), a raw YAML string, or an open file object (`TextIO`).

| Parameter            | Default | Description                                                                |
|----------------------|---------|----------------------------------------------------------------------------|
| `warnings_as_errors` | `True`  | Raise an error when the definition produces validation warnings            |
| `include_meta_def`   | `True`  | Include the built-in [meta service](../advanced/meta.md) in the definition |

For definitions that use [overlays](../reference/overlays.md), use `DefinitionLoader` — see [Python client API](client.md#loading-a-definition).

## Object model

`LrpcDef` is the root. It holds:

- **Settings** — buffer sizes, namespace, version (`RpcSettings`)
- **Services** — each service holds functions and streams (`LrpcService` → `LrpcFun` / `LrpcStream`)
- **Structs** — user-defined aggregate types (`LrpcStruct` → `LrpcVar` fields)
- **Enums** — user-defined enumerations (`LrpcEnum` → `LrpcEnumField`)
- **Constants** — typed scalar constants (`LrpcConstant`)

Function parameters, return values, and struct fields are all `LrpcVar` objects.

## LrpcDef

| Method                                  | Returns                 | Description                                     |
|-----------------------------------------|-------------------------|-------------------------------------------------|
| `name()`                                | `str`                   | Definition name                                 |
| `settings()`                            | `RpcSettings`           | Definition settings                             |
| `definition_hash()`                     | `Optional[str]`         | SHA3-256 hash of the definition file            |
| `services()`                            | `list[LrpcService]`     | User services (excluding meta)                  |
| `service_by_name(name)`                 | `Optional[LrpcService]` | Look up a service by name                       |
| `service_by_id(id)`                     | `Optional[LrpcService]` | Look up a service by ID                         |
| `function(service_name, function_name)` | `Optional[LrpcFun]`     | Look up a function by service and function name |
| `stream(service_name, stream_name)`     | `Optional[LrpcStream]`  | Look up a stream by service and stream name     |
| `structs()`                             | `list[LrpcStruct]`      | All structs                                     |
| `struct(name)`                          | `LrpcStruct`            | Look up a struct by name                        |
| `enums()`                               | `list[LrpcEnum]`        | All enums                                       |
| `enum(name)`                            | `LrpcEnum`              | Look up an enum by name                         |
| `constants()`                           | `list[LrpcConstant]`    | All constants                                   |
| `constant(name)`                        | value                   | Value of a named constant                       |
| `user_settings()`                       | any                     | Contents of the `user_settings` YAML section    |

To traverse every element in order, pass a visitor to `accept()` — see [Python visitor API](visitor.md).

## RpcSettings

| Method                     | Returns         | Description                                      |
|----------------------------|-----------------|--------------------------------------------------|
| `namespace()`              | `Optional[str]` | C++ namespace for generated code                 |
| `version()`                | `Optional[str]` | User-defined version string                      |
| `rx_buffer_size()`         | `int`           | Receive buffer size in bytes                     |
| `tx_buffer_size()`         | `int`           | Transmit buffer size in bytes                    |
| `definition_hash_length()` | `int`           | Number of hash characters embedded in the server |
| `embed_definition()`       | `bool`          | Whether the definition is embedded in the server |
| `byte_type()`              | `str`           | The element type used for `lrpc::byte`           |

See [Settings reference](../reference/settings.md) for the meaning and allowed values of each setting.

## LrpcService

| Method                   | Returns                | Description                |
|--------------------------|------------------------|----------------------------|
| `name()`                 | `str`                  | Service name               |
| `id()`                   | `int`                  | Service ID (0–254)         |
| `functions()`            | `list[LrpcFun]`        | Functions in this service  |
| `function_by_name(name)` | `Optional[LrpcFun]`    | Look up a function by name |
| `function_by_id(id)`     | `Optional[LrpcFun]`    | Look up a function by ID   |
| `streams()`              | `list[LrpcStream]`     | Streams in this service    |
| `stream_by_name(name)`   | `Optional[LrpcStream]` | Look up a stream by name   |
| `stream_by_id(id)`       | `Optional[LrpcStream]` | Look up a stream by ID     |

## LrpcFun

| Method             | Returns         | Description                                 |
|--------------------|-----------------|---------------------------------------------|
| `name()`           | `str`           | Function name                               |
| `id()`             | `int`           | Function ID                                 |
| `params()`         | `list[LrpcVar]` | Parameters                                  |
| `param(name)`      | `LrpcVar`       | Look up a parameter by name                 |
| `param_names()`    | `list[str]`     | Names of all parameters                     |
| `returns()`        | `list[LrpcVar]` | Return values                               |
| `ret(name)`        | `LrpcVar`       | Look up a return value by name              |
| `number_returns()` | `int`           | Number of return values                     |
| `returns_alias()`  | `Optional[str]` | Optional alias for the combined return type |

## LrpcStream

| Method             | Returns             | Description                                 |
|--------------------|---------------------|---------------------------------------------|
| `name()`           | `str`               | Stream name                                 |
| `id()`             | `int`               | Stream ID                                   |
| `origin()`         | `LrpcStream.Origin` | `CLIENT` or `SERVER`                        |
| `is_finite()`      | `bool`              | Whether the stream carries a `final` marker |
| `params()`         | `list[LrpcVar]`     | Parameters (see note below)                 |
| `param(name)`      | `LrpcVar`           | Look up a parameter by name                 |
| `param_names()`    | `list[str]`         | Names of all parameters                     |
| `returns()`        | `list[LrpcVar]`     | Return values (server streams only)         |
| `number_params()`  | `int`               | Number of parameters                        |
| `number_returns()` | `int`               | Number of return values                     |

**Stream parameters vs. returns:**
For a _client_ stream, `params` are the message fields; `returns` is empty. For a _server_ stream, `params` is `[start]` (the implicit start/stop boolean) and `returns` are the message fields.
{: .notice--info}

## LrpcVar

Represents a function parameter, return value, or struct field.

| Method                     | Returns | Description                                            |
|----------------------------|---------|--------------------------------------------------------|
| `name()`                   | `str`   | Variable name                                          |
| `base_type()`              | `str`   | Base type string (e.g. `int32_t`, `MyStruct`)          |
| `is_array()`               | `bool`  | Whether this is an array                               |
| `array_size()`             | `int`   | Array length (meaningful only when `is_array()`)       |
| `is_optional()`            | `bool`  | Whether this is an optional                            |
| `is_string()`              | `bool`  | Whether this is any string type (scalar)               |
| `is_auto_string()`         | `bool`  | Whether this is an auto-sized `string`                 |
| `is_fixed_size_string()`   | `bool`  | Whether this is a fixed-size `string_N`                |
| `string_size()`            | `int`   | Fixed string size (only when `is_fixed_size_string()`) |
| `base_type_is_struct()`    | `bool`  | Base type is a user-defined struct                     |
| `base_type_is_enum()`      | `bool`  | Base type is a user-defined enum                       |
| `base_type_is_string()`    | `bool`  | Base type is a string (including inside arrays)        |
| `base_type_is_integral()`  | `bool`  | Base type is an integer type                           |
| `base_type_is_float()`     | `bool`  | Base type is `float` or `double`                       |
| `base_type_is_bool()`      | `bool`  | Base type is `bool`                                    |
| `base_type_is_bytearray()` | `bool`  | Base type is `bytearray`                               |

## LrpcStruct

| Method                 | Returns         | Description                             |
|------------------------|-----------------|-----------------------------------------|
| `name()`               | `str`           | Struct name                             |
| `fields()`             | `list[LrpcVar]` | Struct fields                           |
| `is_external()`        | `bool`          | Whether this is an external struct      |
| `external_file()`      | `Optional[str]` | Header file path for an external struct |
| `external_namespace()` | `Optional[str]` | Namespace of an external struct         |

## LrpcEnum

| Method                 | Returns               | Description                           |
|------------------------|-----------------------|---------------------------------------|
| `name()`               | `str`                 | Enum name                             |
| `fields()`             | `list[LrpcEnumField]` | Enum fields (with resolved IDs)       |
| `field_id(name)`       | `Optional[int]`       | Look up a field value by name         |
| `is_external()`        | `bool`                | Whether this is an external enum      |
| `external_file()`      | `Optional[str]`       | Header file path for an external enum |
| `external_namespace()` | `Optional[str]`       | Namespace of an external enum         |

## LrpcEnumField

| Method   | Returns |
|----------|---------|
| `name()` | `str`   |
| `id()`   | `int`   |

## LrpcConstant

| Method       | Returns                               | Description                                                |
|--------------|---------------------------------------|------------------------------------------------------------|
| `name()`     | `str`                                 | Constant name                                              |
| `value()`    | `Union[int, float, bool, str, bytes]` | Constant value                                             |
| `cpp_type()` | `str`                                 | C++ type used in generated code (e.g. `int32_t`, `string`) |

## Examples

### Iterate services and functions

``` python
from lrpc.utils import load_lrpc_def

lrpc_def = load_lrpc_def("example.lrpc.yaml")

for service in lrpc_def.services():
    print(f"Service: {service.name()} (ID {service.id()})")
    for fn in service.functions():
        params = ", ".join(f"{p.name()}: {p.base_type()}" for p in fn.params())
        returns = ", ".join(f"{r.name()}: {r.base_type()}" for r in fn.returns())
        print(f"  {fn.name()}({params}) -> ({returns})")
```

### Look up a specific function

``` python
fn = lrpc_def.function("math", "add")
if fn:
    for p in fn.params():
        print(f"{p.name()}: {p.base_type()}, array={p.is_array()}, optional={p.is_optional()}")
```

### Read definition settings

``` python
s = lrpc_def.settings()
print(f"namespace : {s.namespace()}")
print(f"rx buffer : {s.rx_buffer_size()}")
print(f"tx buffer : {s.tx_buffer_size()}")
print(f"version   : {s.version()}")
```

### Inspect struct fields

``` python
for struct in lrpc_def.structs():
    print(f"struct {struct.name()}")
    for field in struct.fields():
        kind = "array" if field.is_array() else "optional" if field.is_optional() else "scalar"
        print(f"  {field.name()}: {field.base_type()} ({kind})")
```
