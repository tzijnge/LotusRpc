![example workflow](https://github.com/tzijnge/LotusRpc/actions/workflows/cmake.yml/badge.svg)

# LotusRpc
RPC framework for embedded systems based on [ETL](https://github.com/ETLCPP/etl)

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

### Example
``` yaml
namespace: "ns"
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