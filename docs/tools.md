---
title: Tools
toc: true
toc_icon: tools
---

## LRPCG

Basic usage: `lrpcg cpp -d example.lrpc.yaml -o output-dir`

For more info type `lrpcg --help`

### C++ server side code generation

The `cpp` command generates all C++ files needed for the RPC server.

`lrpcg cpp -d example.lrpc.yaml -o output-dir`

Definition overlays can be specified with one or more `-ov` options. A single overlay may contain multiple [YAML documents](https://yaml.org/spec/1.2.2/#91-documents). For more information about definition overlays see [Definition overlays](reference_overlays).

For more info type `lrpcg cpp --help`

### Overlay merge

Basic usage: `lrpcg merge -d base.lrpc.yaml -ov overlay1.lrpc.yaml -ov overlay2.lrpc.yaml -o result.lrpc.yaml`

The `merge` command merges the specified overlay files into the base definition and saves the result to a new file. See the [cpp command](#c-server-side-code-generation) for details about the overlay files.

For more info type `lrpcg merge --help`

### C++ server core code generation

The `cppcore` command generates only the core files of the RPC server. These files are static and do not depend on the definition file. In some cases it may be beneficial to generate them separately from the rest of the RPC server.

`lrpcg cppcore -o output-dir`

For more info type `lrpcg cppcore --help`

### Schema export

The `schema` command exports the [LotusRPC definition schema](schema.md) to the specified directory.

`lrpcg schema -o output-dir`

For more info type `lrpcg schema --help`

### PlantUML diagram

The `puml` command transforms your LotusRPC definition file into a PlantUML diagram. The output of this command is a _.puml_ file that can be rendered to an image with PlantUML. This can be useful for documentation purposes

`lrpcg puml -o output-dir`

For more info type `lrpcg puml --help`

## LRPCC

`lrpcc` is the LRPC client tool. A common use case of LRPC is to control a device running an LRPC server from a PC. This means the user must implement an LRPC client on the PC. `lrpcc` makes this very easy by constructing a client at runtime from the definition file and present itself as a CLI tool. `lrpcc` is installed as a command line tool with LRPC and can be called from any location.

Example: Given an LRPC definition with a function **add** inside the service **math**, taking two integers and returning one integer, the function can be called from the PC with the following command

``` bash
lrpcc math add 3 7
```

and the result will be printed to the console.

In order to work, `lrpcc` needs the following information

* Location of the LRPC definition file
* Information about the transport layer between PC and device

Since the command line arguments for `lrpcc` are reserved for the communication with the device, this information must be supplied by the user in the form of a configuration file with name _lrpcc.config.yaml_. `lrpcc` looks for this file in the current working directory and all subdirectories recursively and uses the first one it encounters. This means that you can put the `lrpcc` configuration file anywhere in your project structure and call `lrpcc` from your project root. Alternatively, you can have various different configurations and possibly different LRPC definitions in various subdirectories of your project. You can use any of them by simply navigating to the directory and call `lrpcc` from there.

`lrpcc` constructs a command line application with [Click](https://palletsprojects.com/p/click/). This means that you can easily retrieve help about all available commands by just adding the `--help` flag.

If the file _lrpcc.config.yaml_ is not found, `lrpcc` uses the file specified in the **LRPCC_CONFIG** environment variable.

Here is an example _lrpcc.config.yaml_ file

``` yaml
definition_url: '../example.lrpc.yaml'
definition_from_server: once
transport_type: serial
transport_params:
  port: COM30
  baudrate: 16384
  timeout: 2
log_level: INFO
check_server_version: true
```

The field `log_level` is optional with a default value of `INFO`. If used, it should contain a [standard Python log level](https://docs.python.org/3/howto/logging.html#logging-levels)

The field `check_server_version` is optional with a default value of `true`. It determines whether or not to perform a server version check. If there is any detectable mismatch between the server and the client a warning message will be printed (if the `log_level` is `WARNING` or lower). This can help detect issues early, but it also incurs additional communication between client and server that may not fit the application.

The field `definition_from_server` is optional with allowed values `never` (default), `always` and `once`. Here's what these value mean:

* `never`: `lrpcc` will not retrieve an embedded definition from the server. Definition must be specified in `definition_url`
* `always`: `lrpcc` will always retrieve the embedded definition from the server. Field `definition_url` is ignored
* `once`: `lrpcc` will look for a definition file in the location specified by `definition_url`. If it is not found, it retrieves the embedded definition from the server and saves it in the location specified by `definition_url`. This option can be convenient when it takes long to retrieve the definition from the server, but must not be used in combination with the [definition hash](meta#version) and `check_server_version=true`. This is because the file hash of the definition retrieved from the server will be different from the hash computed during generation of the server code, even if the content is logically the same.

The field `definition_url` is required when `definition_from_server` is `once` or `never`. It is the path of the LRPC definition file and can be relative to _lrpcc.config.yaml_ or an absolute path.

The fields `transport_type` and `transport_params` are required. The subfields of `transport_params` are passed as keyword arguments to the transport class. `lrpcc` uses [pyserial](https://pythonhosted.org/pyserial/) for serial communication, so the `transport_params` can be any of the constructor parameters of the [serial.Serial](https://pythonhosted.org/pyserial/pyserial_api.html#serial.Serial) class.

`lrpcc` currently only supports the serial transport type, but it's easy to write your own transport. See [Extending LRPC](extending_lrpc).

### Sending parameters with LRPCC

Each positional parameter on the command line maps to a function parameter in definition order. Here is a cheat sheet covering all types:

``` bash
lrpcc s fn 123                       # integer
lrpcc s fn 123.456                   # float / double
lrpcc s fn -- -123                   # negative number (see note below)
lrpcc s fn my_string                 # string
lrpcc s fn "my string with spaces"   # string with spaces
lrpcc s fn false                     # bool
lrpcc s fn 1                         # bool
lrpcc s fn yes                       # bool
lrpcc s fn MONDAY                    # enum — must be a valid field name
lrpcc s fn "01AABB"                  # bytearray
lrpcc s fn _                         # optional — absent (no value)
lrpcc s fn my_string                 # optional — present (same syntax as the underlying type)
lrpcc s fn 1 2 3 4                   # array with count: 4
lrpcc s fn "{a: 1, b: hello}"        # struct as YAML (see below)
```

**Negative numbers** — the shell and Click both try to interpret leading `-` as a flag name. Place `--` before the value to stop option parsing:

``` bash
lrpcc s fn -- -42
lrpcc s fn -- -1.5
```

**Booleans** — the following values are accepted (all case-insensitive):

| True                     | False                     |
|--------------------------|---------------------------|
| `true`, `1`, `yes`, `on` | `false`, `0`, `no`, `off` |

**Bytearrays** — pass an even number of hex digits, optionally separated by whitespace. Case-insensitive. An empty string (`""`) sends a zero-length bytearray. Maximum 255 bytes.

``` bash
lrpcc s fn "01AABB"      # three bytes
lrpcc s fn "01 aa bb"    # same — spaces and lowercase are fine
lrpcc s fn ""            # empty bytearray (0 bytes)
```

Hex digits are validated according to the Python [`bytes.fromhex`](https://docs.python.org/3/library/stdtypes.html#bytearray.fromhex) rules.

**Optionals** — use `_` for an absent value. If the underlying string value itself starts and ends with underscores (i.e. consists entirely of underscores), prepend one extra `_` to escape it:

``` bash
lrpcc s fn _             # absent
lrpcc s fn hello         # present, value is "hello"
lrpcc s fn __            # present, value is "_"
lrpcc s fn ___           # present, value is "__"
lrpcc s fn _abc          # present, value is "_abc" (no escaping needed — mixed chars)
```

**Arrays** — pass exactly as many values as the `count` in the definition. Too few or too many is an error.

``` bash
lrpcc s fn 10 20 30      # array with count: 3
```

**Structs** — pass as a YAML flow mapping. Field names and order must match the definition. Quote the whole argument to prevent shell word splitting:

``` bash
lrpcc s fn "{x: 1, y: 2}"
lrpcc s fn "{name: hello, value: 42}"
lrpcc s fn "{label: 'two words', count: 5}"   # quote field values that contain spaces
```

**Streams** — streaming commands have extra flags not present on regular functions:

``` bash
# Server stream: --start (default) begins the stream, --stop ends it
lrpcc s my_server_stream --start
lrpcc s my_server_stream --stop

# Finite client stream: --final marks the last message
lrpcc s my_client_stream data_value
lrpcc s my_client_stream last_value --final
```
