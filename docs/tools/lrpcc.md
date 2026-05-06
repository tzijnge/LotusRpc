---
title: lrpcc
toc: true
toc_icon: tools
---

`lrpcc` is the LotusRPC client tool. A common use case of LotusRPC is to control a device running a LotusRPC server from a PC. This means the user must implement a LotusRPC client on the PC. `lrpcc` makes this very easy by constructing a client at runtime from the definition file and presenting it as a CLI tool. `lrpcc` is installed as a command line tool with LotusRPC and can be called from any location.

Example: Given a LotusRPC definition with a function **add** inside the service **math**, taking two integers and returning one integer, the function can be called from the PC with the following command

``` bash
lrpcc math add 3 7
```

and the result will be printed to the console.

In order to work, `lrpcc` needs the following information

* Location of the LotusRPC definition file
* Information about the transport layer between PC and device

Since the command line arguments for `lrpcc` are reserved for the communication with the device, this information must be supplied by the user in the form of a configuration file with name _lrpcc.config.yaml_. `lrpcc` looks for this file in the current working directory and all subdirectories recursively and uses the first one it encounters. This means that you can put the `lrpcc` configuration file anywhere in your project structure and call `lrpcc` from your project root. Alternatively, you can have various different configurations and possibly different LotusRPC definitions in various subdirectories of your project. You can use any of them by simply navigating to the directory and call `lrpcc` from there.

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

The field `definition_from_server` is optional with allowed values `never` (default), `always` and `once`. Here's what these values mean:

* `never`: `lrpcc` will not retrieve an embedded definition from the server. Definition must be specified in `definition_url`
* `always`: `lrpcc` will always retrieve the embedded definition from the server. Field `definition_url` is ignored
* `once`: `lrpcc` will look for a definition file in the location specified by `definition_url`. If it is not found, it retrieves the embedded definition from the server and saves it in the location specified by `definition_url`. This option can be convenient when it takes a long time to retrieve the definition from the server, but must not be used in combination with the [definition hash](../advanced/meta.md#version) and `check_server_version=true`. This is because the file hash of the definition retrieved from the server will be different from the hash computed during generation of the server code, even if the content is logically the same.

The field `definition_url` is required when `definition_from_server` is `once` or `never`. It is the path of the LotusRPC definition file and can be relative to _lrpcc.config.yaml_ or an absolute path.

The fields `transport_type` and `transport_params` are required. The subfields of `transport_params` are passed as keyword arguments to the transport class. `lrpcc` uses [pyserial](https://www.pyserial.com/docs/) for serial communication, so the `transport_params` can be any of the constructor parameters of the [serial.Serial](https://www.pyserial.com/docs/api-reference#serialserial-constructor) class.

`lrpcc` currently only supports the serial transport type, but it's easy to write your own transport. See [Extending LotusRPC](../advanced/extending-lrpc.md).

## Sending parameters with LRPCC

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

Hex digits are validated according to the Python [`bytes.fromhex`](https://docs.python.org/3/library/stdtypes.html#bytes.fromhex) rules.

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
