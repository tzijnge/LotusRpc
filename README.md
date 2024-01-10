![example workflow](https://github.com/tzijnge/LotusRpc/actions/workflows/cmake.yml/badge.svg)

# LotusRpc
RPC framework for embedded systems based on [ETL](https://github.com/ETLCPP/etl). Generates C++ code with no dynamic memory allocations, no exceptions, no RTTI, etc. 

# Features
## Supported data types
- `uint8_t`
- `uint16_t`
- `uint32_t`
- `uint64_t`
- `int8_t`
- `int16_t`
- `int32_t`
- `int64_t`
- `float`
- `double`
- `bool`
- string
  - Fixed size: e.g., `string_10` for a maximum size of 10 characters (excluding termination character)
  - Automatic size: `string_auto`. For this type the number of bytes that is transferred is determined by how long the actual string is. This can be different for every RPC function call, contrary to the fixed size string. To avoid dynamic memory allocation there is still a maximum size for any single `string_auto`. The maximum is 255 by default but can be overridden with the `max_auto_string_size` setting in the definition file. A string longer than the maximum  will be truncated. At most one parameter and one return value per function can have this type.
- array
  - Array can be of any type except `string_auto`
  - Enabled by using the `count` setting in the definition file with any value larger than 1
- optional
  - Can be used with any type
  - Translated to `etl::optional` in the generated C++ code
  - Enabled by using the `count` setting in the definition file with a value `?`
- custom
  - struct
    - A custom struct can have any number of fields of any type except `string_auto`, even other custom types
    - A custom struct can be used as a function argument or function return type by referencing it with a `@`-prefix
  - enum
    - A custom enum can have any number of fields
    - Translated to an `enum class` in the generated C++ code

## Multiple return values
Multiple return values for a function are supported. In the generated C++ code this feature is translated to a function returning a `std::tuple`

## Interface definition file
The interface definition file is in YAML format. This makes it easy to parse in many languages and use it for any other purpose that you may need. There is a schema for the interface definition file to provide code completion and error checking in editors that support JSON schema.

### Using the schema in VS Code
* Install the [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension
* In the global or local settings.json, add the following entry: `"yaml.schemas": { "/path/to/LotusRpc/generator/lotusrpc-schema.json": "*.lrpc.yaml"}`
* Now every file with `.lrpc.yaml` extension will get code completion and validation in VS Code

## Code generation in a namespace
All code is generated in the namespace specified in the interface definition file. If no namespace is specified, all code is generated in the global namespace

## Configuration of receive and transmit buffer size
Receive and transmit buffer sizes can be configured in the interface definition file. If not specified, both take the value of 256 bytes

## Fully configurable service and function IDs
Every LRPC service has an ID with a value between 0 and 255. This means that LRPC supports a maximum of 256 services. Duplicate service IDs are not allowed. The service ID can optionally be specified in the definition file. If it is not specified an ID is generated, starting with 0 for the first service, 1 for the second service, etc. It is possible to specify only some service IDs and let the rest be generated automatically. For example, if a definition contains 4 services, but only the third service has a specified ID of 17, then the resulting service IDs are [0, 1, 17, 18]

The same applies to LRPC functions inside a service.

# Example
## Interface definition file
File name: example.lrpc.yaml
``` yaml
namespace: "ex"
rx_buffer_size: 200
tx_buffer_size: 300
services:
  - name: "battery"
    id: 0
    functions:
      - name: "get"
        id: 0
        params:
          - name: "option"
            type: "@VoltageScales"
        returns:
          - name: "voltage"
            type: double
enums:
  - name: "VoltageScales"
    fields:
      - id: 1
        name: "microvolts"
      - id: 55
        name: "millivolts"
      - id: 59
        name: "volts"
```

## Python dependencies
- [code-generation](https://pypi.org/project/code-generation/): `pip install code-generation`
- [click](https://pypi.org/project/click/): `pip install click`

## Generate code
Basic usage: `python lotusrpc.py example.lrpc.yaml -o output-dir`
For more info type `python lotusrpc.py --help`

## Use code in your project (server side)
Include the file `<out-dir>/example/battery_ServiceShim.hpp` in your project. Derive you own service class from `ex::batteryServiceShim` and implement all pure virtual functions. These are the remote procedures that are called when issuing a function call on the client. Implement these functions as desired.

Include the file `<out-dir>/example/example.hpp` in your project. This file gives access to the LRPC server class called `ex::example`. Instantiate your service class(es) and register them to the server with `ex::example::registerService`. Feed incoming bytes to the server by calling the `ex::example::decode` function. You are responsible for making sure this data is correct.

# Reference
The LRPC definition is written in YAML and therefore benefits from all the features and tooling that are available for YAML. Think about editor support, easy parsing in various programming languages. The fact that there is a schema available, makes it possible to have code completion and documentation in supporting editors.

The LRPC definition file has two required properties:
- [name](#name)
- [services](#services)

and the following optional properties:

- namespace
- rx_buffer_size
- tx_buffer_size
- structs
- enums
- constants

| Required  | Optional |
| --------- |--------- |
| name      | structs  |
| services  | enums    |
|           | constants|
|           | rx_buffer_size |
|           | tx_buffer_size |
|           | namespace |

At the top level it is also allowed to use additional properties. These properties are ignored by the LRPC tool, but may be useful creating anchors or for any other purpose that you may have. Remember that it's very easy to parse the definition file, so everyone is free to extend the functionality of LRPC.

## Name
This is the name of the RPC engine. It is used in generated files and directories, as well as generated code. Therefore, the name must be a [valid C++ identifier](https://en.cppreference.com/w/cpp/language/identifiers)

## Services
A single RPC engine can contain up to 256 different services. A service can be considered a group of related functions. In the generated code a service with functions corresponds to a class with methods. A RPC engine must have at least one service.

A service has the following properties
| Required  | Optional |
| --------- |--------- |
| name      | id       |
| functions |          |

`name` is the name of the service. It must be a valid C++ identifier.

### Service ID
Every LRPC service has an identifier that is needed for proper transfer of information between two endpoints. If the service identifier is not specified, LRPC will generate one. When starting out with a fresh RPC, it's usually not necessary to specify service IDs. Later on it may be useful to explicitly specify a service ID for backwards compatibility.
> **_NOTE:_**  The most efficient code is generated when service IDs are contiguous and start at 0. This is the default when no IDs are specified

### Functions
A single LRPC service can contain up to 256 functions (but at least 1). A function can have any number of arguments and return values.

A function has the following properties:
| Required  | Optional |
| --------- |--------- |
| name      | id       |
|           | params   |
|           | returns  |

`name` is the name of the function. It must be a valid C++ identifier. `id` is the function identifier, similar to the [service ID](#service-id). `params` is a list of parameters and `returns` is a list of return values.