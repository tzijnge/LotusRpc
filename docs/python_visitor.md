---
title: Python visitor API
toc: true
toc_icon: code-branch
---

**Audience:** This page is for Python developers who need to inspect or transform a LotusRPC interface definition programmatically.
{: .notice--info}

## Overview

LotusRPC parses the definition file into an `LrpcDef` object and exposes its structure through the visitor pattern. Implement a custom visitor to walk every element of the definition — services, functions, streams, structs, enums, constants — without managing traversal logic yourself.

Common use cases include generating code or documentation, extracting information, and enforcing custom naming conventions.

## Loading a definition

Use `load_lrpc_def` to parse a definition file:

``` python
from lrpc.utils import load_lrpc_def

lrpc_def = load_lrpc_def("example.lrpc.yaml")   # path, YAML string, or file object
```

For definitions that use [overlays](reference_overlays.md), use `DefinitionLoader`:

``` python
from lrpc.utils import DefinitionLoader

loader = DefinitionLoader("base.lrpc.yaml")
loader.add_overlay("overlay.lrpc.yaml")
lrpc_def = loader.lrpc_def()
```

## Running a visitor

Pass a visitor instance to `LrpcDef.accept()`:

``` python
lrpc_def.accept(visitor)
```

By default, `accept` also traverses the built-in [meta service](meta.md). To skip it:

``` python
lrpc_def.accept(visitor, visit_meta_service=False)
```

## LrpcVisitor

Subclass `LrpcVisitor` and override the methods you need. Every method has a default no-op implementation, so you only override what you care about:

``` python
from lrpc.visitors import LrpcVisitor

class MyVisitor(LrpcVisitor):
    def visit_lrpc_service(self, service):
        print(f"Service: {service.name()}")

    def visit_lrpc_function(self, function):
        print(f"  function: {function.name()}")
```

### Traversal order

`accept` calls visit methods in this fixed order:

1. `visit_lrpc_def(lrpc_def)` — before anything is visited
2. `visit_rpc_settings(settings)`
3. _(if constants exist)_ `visit_lrpc_constants()`, once per constant: `visit_lrpc_constant(c)`, then `visit_lrpc_constants_end()`
4. For each enum: `visit_lrpc_enum(enum)` → per field: `visit_lrpc_enum_field(enum, field)` → `visit_lrpc_enum_end(enum)`
5. For each struct: `visit_lrpc_struct(struct)` → per field: `visit_lrpc_struct_field(struct, field)` → `visit_lrpc_struct_end()`
6. For each service (then meta service, unless skipped):
   - `visit_lrpc_service(service)`
   - For each function: `visit_lrpc_function(fn)` → per return: `visit_lrpc_function_return(ret)` → `visit_lrpc_function_return_end()` → per param: `visit_lrpc_function_param(p)` → `visit_lrpc_function_param_end()` → `visit_lrpc_function_end()`
   - For each stream: `visit_lrpc_stream(stream)` → per param: `visit_lrpc_stream_param(p)` → `visit_lrpc_stream_param_end()` → per return: `visit_lrpc_stream_return(r)` → `visit_lrpc_stream_return_end()` → `visit_lrpc_stream_end()`
   - `visit_lrpc_service_end()`
7. `visit_lrpc_user_settings(user_settings)`
8. `visit_lrpc_def_end()` — after all elements are visited

**Structs, enums, and constants are always visited before the first service.** Functions and streams within a service are visited in definition order.

### Visit method reference

| Method | Arguments | Called when |
|--------|-----------|-------------|
| `visit_lrpc_def` | `lrpc_def: LrpcDef` | Before traversal starts |
| `visit_lrpc_def_end` | — | After traversal ends |
| `visit_rpc_settings` | `settings: RpcSettings` | Once, early in traversal |
| `visit_lrpc_constants` | — | Before the first constant (only if constants exist) |
| `visit_lrpc_constants_end` | — | After the last constant |
| `visit_lrpc_constant` | `constant: LrpcConstant` | Once per constant |
| `visit_lrpc_enum` | `enum: LrpcEnum` | Before each enum |
| `visit_lrpc_enum_field` | `enum: LrpcEnum, field: LrpcEnumField` | Once per enum field |
| `visit_lrpc_enum_end` | `enum: LrpcEnum` | After each enum |
| `visit_lrpc_struct` | `struct: LrpcStruct` | Before each struct |
| `visit_lrpc_struct_field` | `struct: LrpcStruct, field: LrpcVar` | Once per struct field |
| `visit_lrpc_struct_end` | — | After each struct |
| `visit_lrpc_service` | `service: LrpcService` | Before each service |
| `visit_lrpc_service_end` | — | After each service |
| `visit_lrpc_function` | `function: LrpcFun` | Before each function |
| `visit_lrpc_function_return` | `ret: LrpcVar` | Once per function return value |
| `visit_lrpc_function_return_end` | — | After the last function return value |
| `visit_lrpc_function_param` | `param: LrpcVar` | Once per function parameter |
| `visit_lrpc_function_param_end` | — | After the last function parameter |
| `visit_lrpc_function_end` | — | After each function |
| `visit_lrpc_stream` | `stream: LrpcStream` | Before each stream |
| `visit_lrpc_stream_param` | `param: LrpcVar` | Once per stream parameter |
| `visit_lrpc_stream_param_end` | — | After stream parameters |
| `visit_lrpc_stream_return` | `ret: LrpcVar` | Once per stream return value (server streams only) |
| `visit_lrpc_stream_return_end` | — | After stream return values |
| `visit_lrpc_stream_end` | — | After each stream |
| `visit_lrpc_user_settings` | `user_settings` | Once for all user settings |

**Stream parameters vs. returns:**
For a _client_ stream the `params` are the message fields; `returns` is empty. For a _server_ stream, `params` is `[start]` (the implicit start/stop boolean) and `returns` are the message fields. The visitor calls `visit_lrpc_stream_param` for `params` and `visit_lrpc_stream_return` for `returns` in both cases.
{: .notice--info}

## Domain objects

The arguments passed to visit methods expose the following key attributes.

### LrpcDef

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Definition name |
| `services()` | `list[LrpcService]` | User services (excluding meta) |
| `structs()` | `list[LrpcStruct]` | All structs |
| `enums()` | `list[LrpcEnum]` | All enums |
| `constants()` | `list[LrpcConstant]` | All constants |
| `settings()` | `RpcSettings` | Definition settings |
| `definition_hash()` | `str \| None` | SHA3-256 hash of the definition |
| `constant(name)` | value | Value of a named constant |

### LrpcService

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Service name |
| `id()` | `int` | Service ID (0–254) |
| `functions()` | `list[LrpcFun]` | Functions in this service |
| `streams()` | `list[LrpcStream]` | Streams in this service |

### LrpcFun

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Function name |
| `id()` | `int` | Function ID |
| `params()` | `list[LrpcVar]` | Parameters |
| `returns()` | `list[LrpcVar]` | Return values |
| `returns_alias()` | `str \| None` | Optional alias for the return struct |

### LrpcStream

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Stream name |
| `id()` | `int` | Stream ID |
| `origin()` | `LrpcStream.Origin` | `CLIENT` or `SERVER` |
| `is_finite()` | `bool` | Whether the stream carries a `final` marker |
| `params()` | `list[LrpcVar]` | Message fields (client stream) or `[start]` (server stream) |
| `returns()` | `list[LrpcVar]` | Message fields (server stream) or empty (client stream) |

### LrpcVar

Represents a function parameter, return value, or struct field.

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Variable name |
| `base_type()` | `str` | Base type string (e.g. `int32_t`, `MyStruct`) |
| `is_array()` | `bool` | Whether this is an array |
| `array_size()` | `int` | Array length (meaningful only when `is_array()`) |
| `is_optional()` | `bool` | Whether this is an optional |
| `base_type_is_struct()` | `bool` | Base type is a struct |
| `base_type_is_enum()` | `bool` | Base type is an enum |
| `base_type_is_string()` | `bool` | Base type is a string |
| `base_type_is_integral()` | `bool` | Base type is an integer type |
| `base_type_is_float()` | `bool` | Base type is `float` or `double` |
| `base_type_is_bool()` | `bool` | Base type is `bool` |
| `base_type_is_bytearray()` | `bool` | Base type is `bytearray` |

### LrpcStruct

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Struct name |
| `fields()` | `list[LrpcVar]` | Struct fields |
| `is_external()` | `bool` | Whether this is an external struct |
| `external_file()` | `str \| None` | Header file path for an external struct |
| `external_namespace()` | `str \| None` | Namespace of an external struct |

### LrpcEnum

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Enum name |
| `fields()` | `list[LrpcEnumField]` | Enum fields (with resolved IDs) |
| `is_external()` | `bool` | Whether this is an external enum |
| `external_file()` | `str \| None` | Header file path for an external enum |
| `external_namespace()` | `str \| None` | Namespace of an external enum |

### LrpcEnumField

| Method | Returns |
|--------|---------|
| `name()` | `str` |
| `id()` | `int` |

### LrpcConstant

| Method | Returns | Description |
|--------|---------|-------------|
| `name()` | `str` | Constant name |
| `value()` | `int \| float \| bool \| str \| bytes` | Constant value |
| `cpp_type()` | `str` | The C++ type used in generated code (e.g. `int32_t`, `string`) |

## Example

The visitor below prints a summary of every service, function, and stream in the definition:

``` python
from lrpc.visitors import LrpcVisitor
from lrpc.utils import load_lrpc_def
from lrpc.core import LrpcStream

class DefinitionSummary(LrpcVisitor):
    def visit_lrpc_service(self, service):
        print(f"Service: {service.name()} (ID {service.id()})")

    def visit_lrpc_function(self, function):
        params = ", ".join(f"{p.name()}: {p.base_type()}" for p in function.params())
        returns = ", ".join(f"{r.name()}: {r.base_type()}" for r in function.returns())
        print(f"  fn  {function.name()}({params}) -> ({returns})")

    def visit_lrpc_stream(self, stream):
        direction = "client→server" if stream.origin() == LrpcStream.Origin.CLIENT else "server→client"
        finite = ", finite" if stream.is_finite() else ""
        print(f"  str {stream.name()} [{direction}{finite}]")

lrpc_def = load_lrpc_def("example.lrpc.yaml")
lrpc_def.accept(DefinitionSummary(), visit_meta_service=False)
```

Output for the `example.lrpc.yaml` from [Getting started](getting_started.md#write-an-interface-definition):

``` text
Service: math (ID 0)
  fn  add(a: int32_t, b: int32_t) -> (result: int32_t)
```
