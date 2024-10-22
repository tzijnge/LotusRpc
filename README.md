![Automated build](https://github.com/tzijnge/LotusRpc/actions/workflows/cmake.yml/badge.svg)

[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=tzijnge_LotusRpc&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=tzijnge_LotusRpc)

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=tzijnge_LotusRpc)](https://sonarcloud.io/summary/new_code?id=tzijnge_LotusRpc)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# LotusRpc
RPC framework for embedded systems based on [ETL](https://github.com/ETLCPP/etl). Generates C++ code with no dynamic memory allocations, no exceptions, no RTTI, etc. 

> **_WARNING:_**  This project is work in progress

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
  - Automatic size: `string`. For this type the number of bytes that is transferred is determined by how long the actual string is. This can be different for every RPC function call, contrary to the fixed size string.
- array
  - Array can be of any type except `string`
  - Enabled by using the `count` setting in the definition file with any value larger than 1
- optional
  - Can be used with any type
  - Translated to `etl::optional` in the generated C++ code
  - Enabled by using the `count` setting in the definition file with a value `?`
- custom
  - struct
    - A custom struct can have any number of fields of any type except `string`, even other custom types
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
Every LRPC service has an ID with a value between 0 and 254 (ID 255 is reserved for). This means that LRPC supports a maximum of 255 services. Duplicate service IDs are not allowed. The service ID can optionally be specified in the definition file. If it is not specified an ID is generated, starting with 0 for the first service, 1 for the second service, etc. It is possible to specify only some service IDs and let the rest be generated automatically. For example, if a definition contains 4 services, but only the third service has a specified ID of 17, then the resulting service IDs are [0, 1, 17, 18]

The same applies to LRPC functions inside a service.

## Platform independent
LRPC uses Python to generate code and can therefore be used on all platforms that support Python. The generated C++ code is C++11 compatible and can be compiled for any platform with a suitable compiler.

> **DISCLAIMER:** All development is done on Windows. Continuous integration is done with Github Actions on Ubuntu.

# Tools
## Lrpcc
`lrpcc` is the LRPC client tool. A common use case of LRPC is to control a device running an LRPC server from a PC. This means the user must implement an LRPC client on the PC. `lrpcc` makes this very easy by constructing a client at runtime from the definition file and present itself as a CLI tool. `lrpcc` is installed as a command line tool with LRPC and can be called from any location.

Example: Given an LRPC definition with a function **add** inside the service **math**, taking two integers and returning one integer, the function can be called from the PC with the following command

> lrpcc math add 3 7

and the result will printed to the console.

In order to work, `lrpcc` needs the following information
* Location of the LRPC definition file
* Information about the transport layer between PC and device

Since the command line arguments for `lrpcc` are reserved for the communication with the device, this information must be supplied by the user in the form of a configuration file with name *lrpcc.config.yaml*. `lrpcc` looks for this file in the current working directory and all subdirectories recursively and uses the first one it encounters. This means that you can put the `lrpcc` configuration file anywhere in your project structure and call `lrpcc` from your project root. Alternatively, you can have various different configurations and possibly different LRPC definitions in various subdirectories of your project. You can use any of them by simply navigating to the directory and call `lrpcc` from there.

`lrpcc` constructs a command line application with [Click](https://palletsprojects.com/p/click/). This means that you can easily retrieve help about all available commands by just adding the `--help` flag.

If the file *lrpcc.config.yaml* is not found, `lrpcc` uses the file specified in the **LRPCC_CONFIG** environment variable.

Here is an example *lrpcc.config.yaml* file
``` yaml
definition_url: '../example.lrpc.yaml'
transport_type: 'serial'
transport_params:
  port: 'COM30'
  baudrate: 16384
  timeout: 2
```

The fields `definition_url`, `transport_type` and `transport_params` are required. `definition_url` is the path of the LRPC definition file and can be relative to *lrpcc.config.yaml* or an absolute path. The subfields of `transport_params` are passed as keyword arguments to the transport class. `lrpcc` uses [pyserial](https://pythonhosted.org/pyserial/) for serial communication, so the `transport_params` can be any of the constructor parameters of the [serial.Serial](https://pythonhosted.org/pyserial/pyserial_api.html#serial.Serial) class. `lrpcc` currently only supports the serial transport type.

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

The LRPC definition file has the following properties:

| Required  | Optional |
| --------- |--------- |
| [name](#name)          | structs        |
| [services](#services)  | enums          |
|                        | constants      |
|                        | rx_buffer_size |
|                        | tx_buffer_size |
|                        | namespace      |

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

`name` is the name of the function. It must be a valid C++ identifier. `id` is the function identifier, similar to the [service ID](#service-id). `params` is a list of parameters and `returns` is a list of return values. Every item in `params` and `returns` is a [LrpcType](#lrpctype).

## Structs
LRPC supports defining custom aggregate data types in the `structs` property. `structs` contains a list of custom struct definitions, where every item has the following properties:
| Required  | Optional |
| --------- |--------- |
| name      |          |
| fields    |          |

`name` is the name of the struct. It must be a valid C++ identifier. `fields` is a list of data members, every member being a [LrpcType](#lrpctype). Custom structs can be referenced inside the LRPC definition file by prepending the name with the `@` sign.

## Enums
LRPC supports defining custom enum types in the `enums` property. `enums` contains a list of custom enum definitions, where every item has the following properties:
| Required  | Optional |
| --------- |--------- |
| name      | external           |
| fields    | external_namespace |

`name` is the name of the enum. It must be a valid C++ identifier. `fields` is a list of enum fields, every field having a required `name` property and an optional `id` property. `name` is the enum label and `id` is the value of the label. `fields` can also simply be a list of strings, every string being the name of a field. The field IDs are determined automatically in that case. This allows for shorter notation in case the specific value of the IDs is not important.

It is possible to use an enum in LRPC that already exists in your codebase. In this case, the `external` property must be used to specify the file that contains the definition of the enum. If the external enum lives inside a namespace, that namespace must be specified with the `external_namespace` property. LRPC does not generate any functional code for external enums, but it does generate some checks to verify that the external enum corresponds to the LRPC definition file. LRPC also creates an alias for the external type (unless code is generated in the global namespace and the external enum lives in the global namespace). The alias is used internally in code generated by LRPC

Example:
``` yaml
...
enums:
  # short notation
  - { name: "MyEnum", fields: [V0, V1, V2, V3]}
  # short notation, external enum in namespace
  - { name: "MyEnum2", fields: [V0, V1, V2, V3], external: ext_files/MyEnum2.hpp, external_namespace: "a::b::c"}
  # full notation, external enum in global namespace
  - name: "MyEnum3"
    external: ext_files/MyEnum3.hpp
    fields:
      - {name: V0} # id omitted, defaults to 0
      - {name: V1} # id omitted, defaults to 1
      - {name: V55, id: 55}
      - {name: V200, id: 200 }
      - {name: V201} # id omitted, defaults to 201
...
```

## LrpcType
The LRPC definition file uses LrpcType to describe function arguments, function return values and struct fields.

A LrpcType has the following properties:
| Required  | Optional |
| --------- |--------- |
| name      | count    |
| type      |          |

`name` is the name of the LrpcType.

### LrpcType.type
See section [data types](#supported-data-types)

### LrpcType.count
Specifying `count` as a number (at least 2) turns the LRPC type into an array of that size. Specifying `count` as `?` turns the LRPC type into an optional. If `count` is omitted, the type specified by `type` is used without any modifications
