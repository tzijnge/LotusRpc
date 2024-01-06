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

## Fully configurable service IDs
Every LRPC service has an ID with a value between 0 and 255. This means that LRPC supports a maximum of 256 services. Duplicate service IDs are not allowed. The service ID can optionally be specified in the definition file. If it is not specified an ID is generated, starting with 0 for the first service, 1 for the second service, etc. It is possible to specify only some service IDs and let the rest be generated automatically. For example, if a definition contains 4 services, but only the third service has a specified ID of 17, then the resulting service IDs are [0, 1, 17, 18]

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