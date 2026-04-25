---
title: LotusRPC
author_profile: true
toc: false
---

RPC framework for embedded systems. Generates C++ server code and a Python client from a single YAML definition file. Built on [ETL](https://github.com/ETLCPP/etl) — no dynamic memory allocations, no exceptions, no RTTI.

## How it works

``` mermaid
graph TD
    DEF["example.lrpc.yaml\nYAML interface definition"]
    LRPCG("lrpcg cpp")

    subgraph GEN["Generated C++"]
        SRV_GEN["Server class\nframing · serialization · dispatch"]
        SHIM_GEN["Service shim\none pure-virtual function per RPC call"]
    end

    subgraph IMPL["Your implementation — two classes"]
        MY_SRV["MyServer\nlrpcTransmit → UART · SPI · TCP · …"]
        MY_SVC["MyService\nadd() · get_temperature() · …"]
    end

    TRANSPORT("Transport\nserial · Bluetooth · TCP · …")

    subgraph CLIENT["Client — PC · Python"]
        CLI["lrpcc\nCLI tool, no code needed"]
        LIB["LrpcClient\ncustom Python code"]
    end

    DEF -->|"lrpcg cpp -d"| LRPCG
    LRPCG --> GEN
    DEF -.->|also used by| CLIENT
    SRV_GEN -->|"inherit"| MY_SRV
    SHIM_GEN -->|"inherit + implement"| MY_SVC
    MY_SRV <-->|"lrpcReceive / lrpcTransmit"| TRANSPORT
    TRANSPORT <-->|"function calls + responses"| CLIENT
```

Define your interface once in YAML. LotusRPC generates everything else: the C++ server class, all serialization and framing code, and the service shim with one pure-virtual function per RPC call. You write two classes: wire `lrpcTransmit` to your hardware, and implement your business logic in the service shim. LotusRPC handles the rest.

[Get started](getting_started.md){: .btn .btn--primary .btn--large} &nbsp; [Reference](reference.md){: .btn .btn--primary .btn--large} &nbsp; [C++ API](cpp_api.md){: .btn .btn--primary .btn--large} &nbsp; [Python API](python_client.md){: .btn .btn--primary .btn--large} &nbsp; [Examples](examples.md){: .btn .btn--primary .btn--large}

## Key features

- **No dynamic memory** — stack-only, no heap, no exceptions, no RTTI
- **Transport agnostic** — serial, Bluetooth, TCP — any byte-oriented channel works
- **YAML definitions** — schema-validated, editor-friendly, easy to parse or extend
- **Code generation** — `lrpcg` produces all C++ server and client code in one command
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

For details on each type and the C++ mappings, see the [C++ API reference](cpp_api.md) and the [interface definition reference](reference.md).
