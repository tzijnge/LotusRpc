---
title: Tools
toc: true
---

## LRPCG

Basic usage: `lrpcg cpp -d example.lrpc.yaml -o output-dir`

For more info type `lrpcg --help`

### C++ server side code generation

The `cpp` command generates all C++ files needed for the RPC server.

`lrpcg cpp -d example.lrpc.yaml -o output-dir`

For more info type `lrpcg cpp --help`

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

> lrpcc math add 3 7

and the result will printed to the console.

In order to work, `lrpcc` needs the following information

* Location of the LRPC definition file
* Information about the transport layer between PC and device

Since the command line arguments for `lrpcc` are reserved for the communication with the device, this information must be supplied by the user in the form of a configuration file with name _lrpcc.config.yaml_. `lrpcc` looks for this file in the current working directory and all subdirectories recursively and uses the first one it encounters. This means that you can put the `lrpcc` configuration file anywhere in your project structure and call `lrpcc` from your project root. Alternatively, you can have various different configurations and possibly different LRPC definitions in various subdirectories of your project. You can use any of them by simply navigating to the directory and call `lrpcc` from there.

`lrpcc` constructs a command line application with [Click](https://palletsprojects.com/p/click/). This means that you can easily retrieve help about all available commands by just adding the `--help` flag.

If the file _lrpcc.config.yaml_ is not found, `lrpcc` uses the file specified in the **LRPCC_CONFIG** environment variable.

Here is an example _lrpcc.config.yaml_ file

``` yaml
definition_url: '../example.lrpc.yaml'
transport_type: serial
transport_params:
  port: COM30
  baudrate: 16384
  timeout: 2
log_level: INFO
```

The field `log_level` is optional. If used, it should contain a [standard Python log level](https://docs.python.org/3/howto/logging.html#logging-levels)

The fields `definition_url`, `transport_type` and `transport_params` are required. `definition_url` is the path of the LRPC definition file and can be relative to _lrpcc.config.yaml_ or an absolute path. The subfields of `transport_params` are passed as keyword arguments to the transport class. `lrpcc` uses [pyserial](https://pythonhosted.org/pyserial/) for serial communication, so the `transport_params` can be any of the constructor parameters of the [serial.Serial](https://pythonhosted.org/pyserial/pyserial_api.html#serial.Serial) class.

`lrpcc` currently only supports the serial transport type, but it's easy to write your own transport. See [Extending LRPC](extending_lrpc.md).

### Sending parameters with LRPCC

Sending function parameters with LRPC is easy, just add every parameter on the command line. Here's a cheat sheet:

``` cheat sheet
int:          lrpcc s f0 123
float/double: lrpcc s f1 123.456
signed int:   lrpcc s f2 -123
string:       lrpcc s f3 my_string
string        lrpcc s f3 "my string with spaces"
bool:         lrpcc s f4 false
bool:         lrpcc s f4 1
bool:         lrpcc s f4 yes
enum:         lrpcc s f5 MONDAY
optional:     lrpcc s f6 _
optional:     lrpcc s f6 my_string
array of 4:   lrpcc s f7 1 2 3 4
```

Parameters that have an optional value can be entered the same as the underlying type. If the optional does not have a value use a single underscore

Struct parameters are not supported.
