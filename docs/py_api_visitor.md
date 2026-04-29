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

Use `load_lrpc_def` to load a definition file:

``` python
from lrpc.utils import load_lrpc_def

lrpc_def = load_lrpc_def("example.lrpc.yaml")   # path, YAML string, or file object
```

For more information on loading a definition file see [Python API — Client](py_api_client.md#loading-a-definition)

## Running a visitor

Pass a visitor instance to `LrpcDef.accept()`:

``` python
lrpc_def.accept(visitor)
```

By default, `accept` also traverses the built-in [meta service](adv_meta.md). To skip it:

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

### Visit method reference

The table is ordered by traversal sequence — `accept` calls methods top to bottom. Structs, enums, and constants are always visited before the first service. Functions and streams within a service are visited in definition order.

| Method                           | Arguments                              | Called when                                         |
|----------------------------------|----------------------------------------|-----------------------------------------------------|
| `visit_lrpc_def`                 | `lrpc_def: LrpcDef`                    | Before traversal starts                             |
| `visit_rpc_settings`             | `settings: RpcSettings`                | Once, after `visit_lrpc_def`                        |
| `visit_lrpc_constants`           | —                                      | Before the first constant (only if constants exist) |
| `visit_lrpc_constant`            | `constant: LrpcConstant`               | Once per constant                                   |
| `visit_lrpc_constants_end`       | —                                      | After the last constant                             |
| `visit_lrpc_enum`                | `enum: LrpcEnum`                       | Before each enum                                    |
| `visit_lrpc_enum_field`          | `enum: LrpcEnum, field: LrpcEnumField` | Once per enum field                                 |
| `visit_lrpc_enum_end`            | `enum: LrpcEnum`                       | After each enum                                     |
| `visit_lrpc_struct`              | `struct: LrpcStruct`                   | Before each struct                                  |
| `visit_lrpc_struct_field`        | `struct: LrpcStruct, field: LrpcVar`   | Once per struct field                               |
| `visit_lrpc_struct_end`          | —                                      | After each struct                                   |
| `visit_lrpc_service`             | `service: LrpcService`                 | Before each service                                 |
| `visit_lrpc_function`            | `function: LrpcFun`                    | Before each function                                |
| `visit_lrpc_function_return`     | `ret: LrpcVar`                         | Once per function return value                      |
| `visit_lrpc_function_return_end` | —                                      | After the last function return value                |
| `visit_lrpc_function_param`      | `param: LrpcVar`                       | Once per function parameter                         |
| `visit_lrpc_function_param_end`  | —                                      | After the last function parameter                   |
| `visit_lrpc_function_end`        | —                                      | After each function                                 |
| `visit_lrpc_stream`              | `stream: LrpcStream`                   | Before each stream                                  |
| `visit_lrpc_stream_param`        | `param: LrpcVar`                       | Once per stream parameter                           |
| `visit_lrpc_stream_param_end`    | —                                      | After stream parameters                             |
| `visit_lrpc_stream_return`       | `ret: LrpcVar`                         | Once per stream return value (server streams only)  |
| `visit_lrpc_stream_return_end`   | —                                      | After stream return values                          |
| `visit_lrpc_stream_end`          | —                                      | After each stream                                   |
| `visit_lrpc_service_end`         | —                                      | After each service                                  |
| `visit_lrpc_user_settings`       | `user_settings`                        | Once for all user settings                          |
| `visit_lrpc_def_end`             | —                                      | After traversal ends                                |

**Stream parameters vs. returns:**
For a _client_ stream the `params` are the message fields; `returns` is empty. For a _server_ stream, `params` is `[start]` (the implicit start/stop boolean) and `returns` are the message fields. The visitor calls `visit_lrpc_stream_param` for `params` and `visit_lrpc_stream_return` for `returns` in both cases.
{: .notice--info}

The types passed as arguments to visit methods are documented in the [Python definition model](py_api_definition.md) reference.

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
