---
title: Getting started
toc: true
toc_icon: rocket
---

## Concepts and terminology

LotusRPC is designed to connect two devices in a [client-server model](https://en.wikipedia.org/wiki/Client%E2%80%93server_model). The server is typically a small embedded system that performs some task. The client can be a PC, phone or another small embedded system.

Being an [RPC](https://en.wikipedia.org/wiki/Remote_procedure_call), communication between client and server is modelled as _function_ calls that originate from the client and execute on the server. Like functions in a programming language, an RPC function call can have any number of arguments and return any number of values.

A device may perform several logically unrelated tasks. In LotusRPC, a group of related functions is called a _service_. A LotusRPC _interface_ consists of at least one service, and each service consists of at least one function or stream.

LotusRPC does not include a transport layer. It is transport-agnostic: any platform that can send and receive bytes over any channel can use LotusRPC. Threading and async behavior are similarly out of scope and left to the user.

Apart from function calls, LotusRPC supports data _streams_ — sequences of one-way messages with no return value. Streams can flow from client to server or from server to client, and can be finite or infinite.

## Installation

Install LotusRPC from [PyPI](https://pypi.org/project/lotusrpc/) with:

``` bash
pip install lotusrpc
```

This installs two command-line tools:

- [**lrpcg**](tools_lrpcg.md) — the code generator
- [**lrpcc**](tools_lrpcc.md) — the CLI client for talking to a running server

## Write an interface definition

A LotusRPC interface definition file describes services, functions, streams, structs, enums and constants in YAML. LotusRPC provides a [JSON schema](reference_schema.md) so editors with schema support offer code completion and inline validation.

Here is a minimal example:

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

Save this as `example.lrpc.yaml`. By convention, LotusRPC definition files use the `.lrpc.yaml` extension — this convention is followed throughout the documentation. The full reference for all definition options is in the [interface definition reference](reference_definition.md).

## Generate code

Run `lrpcg` with the `cpp` subcommand and point it at your definition file:

``` bash
lrpcg cpp -d example.lrpc.yaml -o generated/
```

This creates a set of header files in `generated/example/`. The most important ones are:

| File            | Purpose                                    |
|-----------------|--------------------------------------------|
| `example.hpp`   | Top-level include — pulls in everything    |
| `math_shim.hpp` | Abstract base class for the `math` service |

**Tip:** Since code generation is a single shell command it integrates naturally into any build system. See [the CMake snippet below](#cmake-integration).
{: .notice--info}

## Implement the server (C++)

### Implement a service

Include `math_shim.hpp` and derive your own class from `ex::math_shim`. The shim declares one pure virtual function per RPC function — implement them with your business logic:

``` cpp
#include "example/math_shim.hpp"

class MathService : public ex::math_shim
{
protected:
    int32_t add(int32_t a, int32_t b) override
    {
        return a + b;
    }
};
```

### Instantiate the server

Include `example.hpp` and derive from the generated server class `ex::example`. You must implement `lrpcTransmit`, the pure virtual method that LotusRPC calls whenever it has bytes to send back to the client. Wire it to your hardware's transmit routine:

``` cpp
#include "example/example.hpp"

class MyServer : public ex::example
{
    void lrpcTransmit(lrpc::span<const uint8_t> bytes) override
    {
        // Write bytes to your UART / SPI / socket / ...
        uart_write(bytes.data(), bytes.size());
    }
};
```

### Connect everything

Register your service(s) and feed incoming bytes to the server. LotusRPC handles framing — call `lrpcReceive` with each byte as it arrives, or pass a whole span at once:

``` cpp
MathService math;
MyServer server;
server.registerService(math);

// In your receive interrupt or polling loop:
void on_byte_received(uint8_t byte)
{
    server.lrpcReceive(byte);
}
```

### CMake integration

The pattern below wraps the generated headers and ETL in a single INTERFACE library. Any target that calls `target_link_libraries(... lrpc_example)` automatically gets code generation as a build dependency, the generated include paths, and the ETL headers — one line instead of repeating the setup per target.

``` cmake
cmake_minimum_required(VERSION 3.14)
project(MyApp)

# ── Fetch ETL (header-only, LotusRPC's only C++ dependency) ──────────────────
include(FetchContent)
FetchContent_Declare(etl
    GIT_REPOSITORY https://github.com/ETLCPP/etl
    GIT_TAG        20.45.0
)
FetchContent_MakeAvailable(etl)

# ── Code generation ───────────────────────────────────────────────────────────
set(LRPC_GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/generated)
set(LRPC_DEF       ${CMAKE_CURRENT_SOURCE_DIR}/example.lrpc.yaml)

# Core files: static, not definition-specific — only re-runs when missing
add_custom_command(
    OUTPUT  ${LRPC_GENERATED}/lrpccore/Server.hpp
    COMMAND lrpcg cppcore -o ${LRPC_GENERATED}
    COMMENT "Generate LotusRPC core files"
)

# Interface files: re-runs automatically when the definition changes
add_custom_command(
    OUTPUT  ${LRPC_GENERATED}/example/example.hpp
    COMMAND lrpcg cpp -d ${LRPC_DEF} -o ${LRPC_GENERATED}
    DEPENDS ${LRPC_DEF}
    COMMENT "Generate LotusRPC interface files"
)

# Named target that gates on both generated outputs
add_custom_target(lrpc_generate_example
    DEPENDS
        ${LRPC_GENERATED}/lrpccore/Server.hpp
        ${LRPC_GENERATED}/example/example.hpp
)

# ── INTERFACE library ─────────────────────────────────────────────────────────
# Bundles generation dependency + include paths so any target that links
# lrpc_example picks up everything with a single target_link_libraries call.
add_library(lrpc_example INTERFACE)
add_dependencies(lrpc_example lrpc_generate_example)
target_include_directories(lrpc_example INTERFACE
    ${LRPC_GENERATED}
    ${etl_SOURCE_DIR}/include
)

# ── Targets ───────────────────────────────────────────────────────────────────
add_executable(MyApp main.cpp)
target_link_libraries(MyApp PRIVATE lrpc_example)
target_compile_features(MyApp PRIVATE cxx_std_11)

# A second target (host-side unit tests, another firmware variant, …) gets
# the same generated headers and ETL paths for free:
# add_executable(MyAppTests tests/math_service_test.cpp)
# target_link_libraries(MyAppTests PRIVATE lrpc_example gtest_main)
```

**Tip:** Commit the `generated/` folder to source control if you want the generated headers available without running `lrpcg` (e.g. on CI machines without Python installed).
{: .notice--info}

## Use the client

### lrpcc (CLI)

On a PC with Python, use **lrpcc** to talk to the server without writing any code. Create an `lrpcc.config.yaml` in your project:

``` yaml
definition_url: 'example.lrpc.yaml'
transport_type: serial
transport_params:
  port: COM3
  baudrate: 115200
  timeout: 2
```

Then call functions directly from the terminal:

``` bash
lrpcc math add 3 7   # prints: result = 10
```

Run `lrpcc --help` for a full list of available services and functions.

### Custom Python client

To communicate from your own Python code, create an `LrpcClient` and call `communicate`:

``` python
from lrpc.client import LrpcClient
from lrpc.utils import load_lrpc_def
import serial

lrpc_def = load_lrpc_def("example.lrpc.yaml")
transport = serial.Serial(port="COM3", baudrate=115200, timeout=2)

client = LrpcClient(lrpc_def, transport)

for response in client.communicate("math", "add", a=3, b=7):
    print(response.payload["result"])   # prints: 10
```

`communicate` is a generator. For regular functions it yields exactly once; for streams it yields zero or more times.

For the full Python client API — streams, error responses, `encode`/`decode`, version checking — see the [Python client API reference](py_api_client.md).

## Streams

Streams are LotusRPC's way of sending many messages in one direction with minimal latency — unlike regular functions, there is no response to each message.

LotusRPC has two stream directions (always initiated by the client) and two stream modes (finite or infinite):

**Client stream** — client sends data, server receives it. The server can optionally send a `requestStop` message.

``` mermaid
sequenceDiagram
    Client ->> Server: message 1
    Client ->> Server: message 2
    Client ->> Server: message n
    Server ->> Client: requestStop (optional)
```

**Server stream** — client starts the stream; server sends data back; client stops the stream when done.

``` mermaid
sequenceDiagram
    Client ->> Server: start
    Server ->> Client: message 1
    Note over Server, Client: ...
    Server ->> Client: message n
    Client ->> Server: stop
```

**Finite streams** add an implicit `final` boolean to every message so the receiving side knows when the last message has arrived:

``` mermaid
sequenceDiagram
    Client ->> Server: message 1 [final=false]
    Client ->> Server: message 2 [final=false]
    Client ->> Server: message 3 [final=true]
```

For details on the generated C++ API for streams, see the [C++ API reference](cpp_api.md#streams).

## Troubleshooting

### `lrpcg` or `lrpcc` not found after install

pip installs command-line tools into a directory that may not be on your `PATH`. On Linux/macOS check `~/.local/bin`; on Windows check the `Scripts` folder inside your Python installation or virtual environment. Add the relevant directory to your `PATH` and retry.

### Server does not respond

Check `lrpcc.config.yaml`:

- **Port name** — on Windows use `COM3` style; on Linux `/dev/ttyUSB0` or similar.
- **Baudrate** — must match the baudrate configured on the device.
- **Timeout** — increase it if the device is slow to respond.

Also verify that the device is powered, the firmware is running, and `registerService` has been called before the main loop starts.

### lrpcc reports a version mismatch warning

The definition file used by the client does not match the one used to generate the server code. Regenerate the server code with `lrpcg cpp`, rebuild and re-flash the firmware, then retry. For a full explanation of what gets compared and what the warning means, see [Version mismatch behavior](adv_meta.md#version-mismatch-behavior).

### "Unknown service" or "Unknown function" errors in the error stream

Same root cause as a version mismatch — the compiled server does not know the service or function the client is calling. Regenerate and rebuild. See [Calling an unknown function or service](adv_meta.md#calling-an-unknown-function-or-service) for details on how the server responds.

### Messages are truncated or never sent

The encoded message exceeds the configured buffer size. Increase `tx_buffer_size` (server → client) or `rx_buffer_size` (client → server) in the [settings](reference_settings.md#rx_buffer_size--tx_buffer_size) section of your definition, then regenerate.

### Code generation fails with a validation error

The definition file contains an error that the schema validator caught. Run `lrpcg schema -o .` to export the schema, then open your definition in an editor with YAML schema support (see [Interface definition schema](reference_schema.md)) for inline highlighting of the problem.
