# LotusRPC 🌼

![Automated build](https://github.com/tzijnge/LotusRpc/actions/workflows/cmake.yml/badge.svg)

[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=tzijnge_LotusRpc&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=tzijnge_LotusRpc)

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=tzijnge_LotusRpc)](https://sonarcloud.io/summary/new_code?id=tzijnge_LotusRpc)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **_WARNING:_**  This project is work in progress

LotusRPC is an RPC framework for embedded systems based on [ETL](https://github.com/ETLCPP/etl). It generates C++ code with no dynamic memory allocations, no exceptions, no RTTI, etc. Code generator and client side CLI application in a simple Python package.

## Installation

Install from [PyPI](https://pypi.org/project/lotusrpc/) with ```pip install lotusrpc```

## Basic usage

Installing the Python package installs the `lrpcg` tool on your system. This is the LotusRPC generator. It also installs the `lrpcc` tool on your system. This is the LotusRpc CLI client.

Your RPC interface is specified in a YAML file

File name: _example.lrpc.yaml_

``` yaml
services:
  - name: battery
    functions:
      - name: get
        params:
          - name: option
            type: "@VoltageScales"
        returns:
          - name: voltage
            type: double
enums:
  - name: VoltageScales
    fields:
        name: microvolts
        name: millivolts
        name: volts
```

Generate server side code by simply running this command

```lrpcg cpp -d example.lrpc.yaml -o output-dir```

Give the generated code a meaningful implementation and hook it up to a transport layer. Flash your embedded device. Then use `lrpcc` to communicate with your device and print the result to the console

```lrpcc battery get microvolts```

## Documentation

Please find more detailed information on the [LotusRPC documentation pages](https://tzijnge.github.io/LotusRpc/)
