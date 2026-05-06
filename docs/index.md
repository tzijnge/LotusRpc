---
title: LotusRPC
author_profile: true
toc: false
---

RPC framework for embedded systems. Generates C++ server code and a Python client from a single YAML definition file. Built on [ETL](https://github.com/ETLCPP/etl) — no dynamic memory allocations, no exceptions, no RTTI.

## How it works

``` mermaid
graph TD
    subgraph EMB["`**Embedded** · Server · C++`"]
        direction LR
        CORE["`**LRPC Core**<br>framing · serialization · dispatch`"]
        SERVICE["`**Service shim classes**<br>one pure-virtual function per RPC call<br>Derive and implement yourself`"]
        SERVER["`**Server shim class**<br>Derive and implement the transport layer yourself`"]
    end

    subgraph PC["`**PC** · Client · Python`"]
        direction LR
        CLI["`**CLI client tool**<br>lrpcc`"]
        CUSTOM["Custom application"]
    end

    DEF["`**Interface Definition**<br>*.lrpc.yaml`"]

    DEF -.- |Runtime interpretation| PC
    DEF -.- |"Code generation (lrpcg)"| EMB

    PC <--> |"Function calls\nover any byte transport"| EMB
    CLI ~~~ |or| CUSTOM
    CORE ~~~ |and| SERVICE
    SERVICE ~~~ |and| SERVER
```

Define your interface once in YAML. LotusRPC generates all serialization, framing and function dispatching code. You wire the server class to your transport layer and your business by simply implementing abstract functions. LotusRPC handles the rest.

[Get started](getting_started.md){: .btn .btn--primary .btn--large} &nbsp; [Reference](reference/definition.md){: .btn .btn--primary .btn--large} &nbsp; [C++ API](cpp_api.md){: .btn .btn--primary .btn--large} &nbsp; [Python API](python-api/client.md){: .btn .btn--primary .btn--large} &nbsp; [Examples](examples.md){: .btn .btn--primary .btn--large}

## Key features

- **Suitable for embedded** — no dynamic memory, no exceptions, no RTTI
- **Transport agnostic** — serial, Bluetooth, TCP — any byte-oriented channel works
- **YAML definitions** — definition files use the `.lrpc.yaml` extension by convention; schema-validated, editor-friendly, easy to parse or extend
- **Code generation** — `lrpcg` produces all C++ server code in one command
- **CLI client** — `lrpcc` lets any team member call remote functions without writing code
- **Streams** — client-to-server and server-to-client data streams, finite or infinite
- **C++11 compatible** — works on any platform with a modern C++ compiler

## Quick example

Define an interface in YAML:

``` yaml
name: example
settings:
  namespace: ex
services:
  - name: math
    functions:
      - name: add
        params:
          - { name: a, type: int32_t }
          - { name: b, type: int32_t }
        returns:
          - { name: result, type: int32_t }
```

Generate code, implement the function, and call it from the command line:

``` bash
lrpcg cpp -d example.lrpc.yaml -o generated/
lrpcc math add 3 7   # prints: result = 10
```

See [Getting started](getting_started.md) for a complete walkthrough.

## Supported data types

| Category  | Types                                                                                    |
|-----------|------------------------------------------------------------------------------------------|
| Integer   | `uint8_t`, `int8_t`, `uint16_t`, `int16_t`, `uint32_t`, `int32_t`, `uint64_t`, `int64_t` |
| Float     | `float`, `double`                                                                        |
| Bool      | `bool`                                                                                   |
| String    | `string` (auto size), `string_N` (fixed size N)                                          |
| Bytearray | `bytearray` — flexible-length byte buffer                                                |
| Array     | Any type with `count: N` (N ≥ 2)                                                         |
| Optional  | Any type with `count: ?`                                                                 |
| Struct    | Composite user-defined type                                                              |
| Enum      | User-defined enumeration, translated to `enum class`                                     |

For details on each type and the C++ mappings, see the [C++ API reference](cpp_api.md) and the [interface definition reference](reference/definition.md).
