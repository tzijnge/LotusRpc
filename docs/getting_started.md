---
title: Getting started
toc: true
toc_icon: rocket
---

## Concepts and terminology

LotusRPC is designed to connect two devices in a [client-server model](https://en.wikipedia.org/wiki/Client%E2%80%93server_model). The server is typically a small embedded system that performs some task. The client can be a PC, phone or another small embedded system.

Being an [RPC](https://en.wikipedia.org/wiki/Remote_procedure_call), communication between client and server is modelled as _function_ calls that originate from the client and execute on the server. Like functions in a programming language, an RPC function call can have any number of arguments and return any number of values.

A device typically handles several distinct responsibilities — for example, a sensor node might manage its hardware configuration, expose measurement data, and control an indicator LED. Each of these responsibilities forms a natural group of related operations. In LotusRPC, such a group is called a _service_. A complete LotusRPC _interface_ describes all the services a device exposes, and each service contains at least one function or stream.

LotusRPC does not include a transport layer. It is transport-agnostic: any platform that can send and receive bytes over any channel can use LotusRPC. Threading and async behavior are similarly out of scope and left to the user.

Apart from function calls, LotusRPC supports data _streams_ — sequences of one-way messages with no return value. Streams can flow from client to server or from server to client, and can be finite or infinite.

The interface a device exposes is described in an _interface definition file_: a YAML file with the `.lrpc.yaml` extension. It lists the services, and for each service the functions and streams it contains, along with their parameter and return types. This file is the single source of truth that both the C++ code generator and the Python client use — keeping server and client automatically in sync.

## What LotusRPC provides

LotusRPC is a Python package with two main components:

1. **Code generator** — takes an interface definition and generates the C++ server code that runs on the embedded device.
2. **Python client** — a Python library and CLI tool for communicating with a running server from a PC or host system.

## Installation

Install LotusRPC from [PyPI](https://pypi.org/project/lotusrpc/) with:

``` bash
pip install lotusrpc
```

This installs two command-line tools:

- [**lrpcg**](tools/lrpcg.md) — the code generator
- [**lrpcc**](tools/lrpcc.md) — the CLI client for talking to a running server

## Write an interface definition

A LotusRPC interface definition file describes services, functions, streams, structs, enums and constants in YAML. LotusRPC provides a [JSON schema](reference/schema.md) so editors with schema support offer code completion and inline validation.

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

Save this as `example.lrpc.yaml`. By convention, LotusRPC definition files use the `.lrpc.yaml` extension — this convention is followed throughout the documentation. The full reference for all definition options is in the [interface definition reference](reference/definition.md).

## Generate code

Run `lrpcg` with the `cpp` subcommand and point it at your definition file:

``` bash
lrpcg cpp -d example.lrpc.yaml -o generated/
```

This creates a set of header files in _generated/example/_. The most important ones are:

| File            | Purpose                                    |
|-----------------|--------------------------------------------|
| `example.hpp`   | Top-level include — pulls in everything    |
| `math_shim.hpp` | Abstract base class for the `math` service |

**Tip:** Since code generation is a single shell command it integrates naturally into any build system. See [the CMake snippet below](#cmake-integration).
{: .notice--info}

## Implement the server (C++)

### Implement a service

Include _example.hpp_ (or _math\_shim.hpp_) and derive your own class from `ex::math_shim`. The shim declares one pure virtual function per RPC function — implement them with your business logic:

``` cpp
#include "example/example.hpp"

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

Use `add_custom_command` to run `lrpcg` as part of the build. Listing the definition file in `DEPENDS` ensures the headers are regenerated whenever it changes. Adding the generated header to the `add_executable` sources wires the dependency into the build graph automatically.

``` cmake
set(CMAKE_CXX_STANDARD 11)

set(LRPC_DEF ${CMAKE_CURRENT_SOURCE_DIR}/example.lrpc.yaml)
set(LRPC_OUT ${CMAKE_CURRENT_SOURCE_DIR}/generated)

add_custom_command(
    OUTPUT  ${LRPC_OUT}/example/example.hpp
    COMMAND lrpcg cpp -d ${LRPC_DEF} -o ${LRPC_OUT}
    DEPENDS ${LRPC_DEF}
)

add_executable(MyApp main.cpp ${LRPC_OUT}/example/example.hpp)
target_include_directories(MyApp PRIVATE ${LRPC_OUT})
```

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

response = client.communicate_single("math", "add", a=3, b=7)
print(response.payload["result"])   # prints: 10
```

`communicate_single` is a convenience wrapper around `communicate` that returns the first response directly. Use `communicate` when receiving stream response messages — it is a generator that yields one response per message received from the server.

For the full Python client API — streams, error responses, `encode`/`decode`, version checking — see the [Python client API reference](python-api/client.md).

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

### Example

Extend the `math` service from earlier with a finite server stream:

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
    streams:
      - name: results
        origin: server
        finite: true
        params:
          - { name: value, type: int32_t }
```

Receive all messages from the stream using `communicate`:

``` python
# print each value returned from the server
for response in client.communicate("math", "results"):
    print(response.payload["value"])
```

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

The definition file used by the client does not match the one used to generate the server code. Regenerate the server code with `lrpcg cpp`, rebuild and re-flash the firmware, then retry. For a full explanation of what gets compared and what the warning means, see [Version mismatch behavior](advanced/meta.md#version-mismatch-behavior).

### "Unknown service" or "Unknown function" errors in the error stream

Same root cause as a version mismatch — the compiled server does not know the service or function the client is calling. Regenerate and rebuild. See [Calling an unknown function or service](advanced/meta.md#calling-an-unknown-function-or-service) for details on how the server responds.

### Messages are truncated or never sent

The encoded message exceeds the configured buffer size. Increase `tx_buffer_size` (server → client) or `rx_buffer_size` (client → server) in the [settings](reference/settings.md#rx_buffer_size--tx_buffer_size) section of your definition, then regenerate.

### Code generation fails with a validation error

The definition file contains an error that the schema validator caught. Run `lrpcg schema -o .` to export the schema, then open your definition in an editor with YAML schema support (see [Interface definition schema](reference/schema.md)) for inline highlighting of the problem.
