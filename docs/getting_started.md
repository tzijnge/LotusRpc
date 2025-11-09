---
title: Getting started
toc: true
---

## Concepts and terminology

LotusRPC is designed to connect two devices in a [client-server model](https://en.wikipedia.org/wiki/Client%E2%80%93server_model). The server is typically a small embedded system that performs some task. The client can be a PC, phone or another small embedded system that is interested in information or a service that the server provides.
Being an [RPC](https://en.wikipedia.org/wiki/Remote_procedure_call), the communication between the client and the server is modeled as _function_ calls originating from the client and executed on the server. Like function calls in a programming language, a function call in LotusRPC can have any number of arguments and return any number of values. The number of function parameters and return values depends on the definition of the function.
A device may be capable of doing several logically or functionally unrelated tasks. In LotusRPC, a group of related tasks is called a _service_. A LotusRPC _interface_ consists of at least one service and each service consists of at least one function.
LotusRPC provides a number of basic data types that are very similar (or map very wel to) types in languages such as C++, Python and many other languages. Additionally it is possible to define custom enumerations and compose new types from other types.
Apart from function calls, LotusRPC also supports data streams from client to server or from server to client. A data stream is modelled as a sequence of function calls without a return value (not even void). In other words, it is a fire and forget function call in which the data is transferred from one side to the other as function arguments.
A LotusRPC interface is described in an interface definition file. LotusRPC itself is a Python package that generates server and client side code from the definition file.
LotusRPC does not include a transport layer to deliver data over a certain communication channel. It is outside the scope of LotusRPC because it is too diverse and would be to complex to maintain any relevant form of support. Instead LotusRPC is a generic and platform independent way of transforming function calls into a set of bytes and vice versa. Therefore any platform that can send and receive bytes over any communication channel can use LotusRPC.
With a similar reasoning, LotusRPC does not support threading or async behavior. If desired, it is left to the user to integrate LotusRPC in a threaded environment

## Installation

Install LotusRPC from [PyPI](https://pypi.org/project/lotusrpc/) with ```pip install lotusrpc```. This makes **lrpcg**, the LotusRPC generator tool available in your Python installation. If Python is added to the path, you can use the generator tool by simply typing `lrpcg` in a terminal. Command line help is provided to get started.

## Write interface definition

A LotusRPC interface definition file is a hierarchical description of an interface. At the top level it consists of a services, structs, enums and constants. Each service consists of functions and streams. Each function contains parameters and return values. Each stream contains only parameters, no matter the direction of the stream.
LotusRPC uses the YAML file format to describe an interface. This may not be the most compact or readable at first glance, but it will quickly become familiar and this approach has many advantages. First of all for the development of LotusRPC, but also for its users. Think of

* Syntax highlighting
* Code completion and error checking (LotusRPC provides a schema)
* Section folding
* Easy parsing in other tooling or languages for whatever purpose you can come up with

## Generate code

To generate server side C++ code from an interface definition file, run `lrpcg` with the _cpp_ command and provide the path to the definition file. LotusRPC will make sure there are no syntactic and semantic errors in the definition and generate the code. It can be as simple as:
```lrpcg cpp -f my_definition.yaml```
Since code generation is just a command on the terminal, it should be easy to integrate in any existing build system.

### CMake

To generate code in CMake as a pre-build step you can use the following snippet

``` cmake
set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated)
set(LRPC_DEF ${CMAKE_CURRENT_SOURCE_DIR}/my_interface.lrpc.yaml)

add_custom_command(OUTPUT my_interface.hpp
                COMMENT "Generate LRPC files"
                DEPENDS ${LRPC_DEF}
                COMMAND lrpcg cpp -d ${LRPC_DEF} -o ${LRPC_OUT_DIR} -w)

set_directory_properties(PROPERTIES ADDITIONAL_CLEAN_FILES ${LRCP_OUT_DIR})

add_executable(MyApp main.cpp ${LRCP_OUT_DIR}/my_interface.hpp)

target_include_directories(MyApp PRIVATE ${LRPC_OUT_DIR})
```

In this example, _my_interface_ is added as a source file to the application. Since this file is generated with **lrpcg** and does not exist initially, we need a custom command to tell CMake how to create it. Since the custom command depends on the interface definition file, the code will be regenerated automatically if a modification to the interface is made.
Not that **lrpcg** generates many more files than just _my_interface.hpp_, but since they are all header files, they don't have to be added explicitly to the executable.

## Use RPC (server side)

Include the file `<out-dir>/example/battery_ServiceShim.hpp` in your project. Derive you own service class from `ex::batteryServiceShim` and implement all pure virtual functions. These are the remote procedures that are called when issuing a function call on the client. Implement these functions as desired.

Include the file `<out-dir>/example/example.hpp` in your project. This file gives access to the LRPC server class called `ex::example`. Instantiate your service class(es) and register them to the server with `ex::example::registerService`. Feed incoming bytes to the server by calling the `ex::example::decode` function. You are responsible for making sure this data is correct.

### Using streams

Streams are LotusRpc's way of sending many messages in one direction with as little latency as possible. This means that, other than with normal function calls, there is no response to a message.

LotusRpc has two main types of streams. A stream originating from the server and a stream originating from the client. In both cases the client is considered the master in the system; it determines when to start and stop a stream. LotusRpc also makes distinction between finite streams and infinite streams. All cases are covered below with a sequence diagram.

In the case of a client to server stream, the client just starts sending messages and the server will have to handle them. The client can stop sending at any time. Alternatively, the server can send a `requestStop` message to the client to indicate that it does not want to receive any more data. This message is optional and it is left up to the client application what to do with this message. I.e., LotusRpc only provides the infrastructure, but does not enforce any particular behavior.

``` mermaid
sequenceDiagram
    title: Basic client stream

    Client ->> Server: message 1
    Client ->> Server: message 2
    Client ->> Server: message n
    Server ->> Client: requestStop
```

In case of a server to client stream, the client starts the stream by sending the `start` command. It can stop the stream at any time by sending the `stop` command. Again, LotusRpc provides the infrastructure for starting and stopping a stream, but is left up to the server and client applications how to handle these commands. LotusRpc does not enforce actual starting and stopping. In fact, the server could start sending stream data without even receiving a `start` command.

``` mermaid
sequenceDiagram
    title: Basic server stream

    Client ->> Server: start
    Server ->> Client: message 1
    Note over Server, Client: ...
    Server ->> Client: message n
    Client ->> Server: stop
```

Both stream variants can be finite or infinite (default). In case of a finite stream, the stream message gets an additional boolean parameter called `final` to indicate if a message is the last one in the stream (`final` is true) or not (`final` is false). This allows the receiving side to take appropriate action upon receiving the last message in the stream.

``` mermaid
sequenceDiagram
    title: Finite client stream

    Client ->> Server: message 1 [final=false]
    Client ->> Server: message 2 [final=false]
    Client ->> Server: message 3 [final=true]
```

``` mermaid
sequenceDiagram
    title: Finite server stream

    Client ->> Server: start
    Server ->> Client: message 1 [final=false]
    Note over Server, Client: ...
    Server ->> Client: message n [final=true]
```

## Use RPC (client side)

### lrpcc

On a client that runs Python it is very easy to communicate with a server. LotusRPC includes the **lrpcc** tool for this, the LotusRPC CLI. Like **lrpcg**, this tool is available in your Python installation after installing LotusRPC. The **lrpcc** tool does not require any code generation, just the interface definition file and a suitable transport implementation. Because command line arguments are reserved for communication with the server, these have to be provided in a configuration file (**lrpcc** will help you create one if it's not there). With the configuration file in place you can just type `lrpcc --help` to get a list of services in the interface. Suppose there is a _math_ service in the interface, just type `lrpcc math --help` to get a list of functions in the service. Suppose there is a function _add_ in the _math_ service, just type `lrpcc math add --help` to get more info about the usage of this function. Type `lrpcc math add 5 7` to call the _add_ function on the server. If the server knows how to add two numbers, the number 12 is then printed to the screen.

### Custom client code

To communicate with a server from custom Python code, use the following approach.

* Create an `lrpc.client.LrpcClient` object.
* Call the `communicate` method on the client. It takes the service name and the function/stream name as arguments. It also takes the function/stream parameters as keyword arguments. `communicate` is a generator that yields for every response from the server. For functions this is always exactly once, but for streams it may be 0 or more times.

Here's an example that prints the value 13

``` Python
from lrpc.client import LrpcClient
from lrpc.utils import load_lrpc_def_from_url
import serial

lrpc_def = load_lrpc_def_from_url(def_url, warnings_as_errors=True)
transport = serial.Serial()

client = LrpcClient(lrpc_def, transport)

for response in client.communicate("math_service", "add", v1=10, v2=3):
    print(response["sum"])
```
