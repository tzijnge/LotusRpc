---
title: Tools
toc: true
---

## LRPCG
Basic usage: `lrpcg example.lrpc.yaml -o output-dir`

For more info type `lrpg --help`


## LRPCC
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