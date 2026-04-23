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

- [**lrpcg**](tools#lrpcg) — the code generator
- [**lrpcc**](tools#lrpcc) — the CLI client for talking to a running server

## Write an interface definition

A LotusRPC interface definition file describes services, functions, streams, structs, enums and constants in YAML. LotusRPC provides a [JSON schema](schema) so editors with schema support offer code completion and inline validation.

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

Save this as `example.lrpc.yaml`. The full reference for all definition options is in the [interface definition reference](reference).

## Generate code

Run `lrpcg` with the `cpp` subcommand and point it at your definition file:

``` bash
lrpcg cpp -d example.lrpc.yaml -o generated/
```

This creates a set of header files in `generated/example/`. The most important ones are:

| File             | Purpose                                    |
|------------------|--------------------------------------------|
| `example.hpp`    | Top-level include — pulls in everything    |
| `math_shim.hpp`  | Abstract base class for the `math` service |

**Tip:** Since code generation is a single shell command it integrates naturally into any build system. See [the CMake snippet below](#cmake-integration).
{: .notice--info}

## Implement the server (C++)

### Implement a service

Include `math_shim.hpp` and derive your own class from `ex::math_shim`. The shim declares one pure virtual function per RPC function — implement them with your business logic:

``` cpp
#include "example/math_shim.hpp"

class MathService : public ex::math_shim {
protected:
    int32_t add(int32_t a, int32_t b) override {
        return a + b;
    }
};
```

### Instantiate the server

Include `example.hpp` and derive from the generated server class `ex::example`. You must implement `lrpcTransmit`, the pure virtual method that LotusRPC calls whenever it has bytes to send back to the client. Wire it to your hardware's transmit routine:

``` cpp
#include "example/example.hpp"

class MyServer : public ex::example {
    void lrpcTransmit(lrpc::span<const uint8_t> bytes) override {
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
void on_byte_received(uint8_t byte) {
    server.lrpcReceive(byte);
}
```

### CMake integration

To generate code as a pre-build step in CMake:

``` cmake
set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated)
set(LRPC_DEF ${CMAKE_CURRENT_SOURCE_DIR}/example.lrpc.yaml)

add_custom_command(OUTPUT ${LRPC_OUT_DIR}/example/example.hpp
                COMMENT "Generate LRPC files"
                DEPENDS ${LRPC_DEF}
                COMMAND lrpcg cpp -d ${LRPC_DEF} -o ${LRPC_OUT_DIR})

add_executable(MyApp main.cpp ${LRPC_OUT_DIR}/example/example.hpp)
target_include_directories(MyApp PRIVATE ${LRPC_OUT_DIR})
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

for response in client.communicate("math", "add", a=3, b=7):
    print(response["result"])   # prints: 10
```

`communicate` is a generator. For regular functions it yields exactly once; for streams it yields zero or more times.

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
