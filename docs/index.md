---
title: LotusRPC 🌼
author_profile: true
toc: true
---

RPC framework for embedded systems based on [ETL](https://github.com/ETLCPP/etl). Generates C++ code for your device with no dynamic memory allocations, no exceptions, no RTTI, etc.

> **_WARNING:_**  This project is work in progress

## Goal and philosophy

The goal of LotusRPC is to create a lightweight, easy to use RPC for small embeddeded systems (microcontrollers) using C++. Lightweight does not mean that it's the smallest, fastest or most efficient library around. In fact, no comparisons are done with other similar frameworks, but is should be fairly small, fast and efficient. LotusRPC does not do any dynamic memory allocation and does not throw exceptions, but it does use inheritance and virtual funtion calls are made. It has a dependency on ETL, but if you're serious about programming an embedded device in C++, you already have that dependency, right? ;-)

LotusRPC does **not** support C and there are no plans to do so.

LotusRPC aims to be easy to use:

* Easy to install as a Python package with pip
* Interface definition in YAML, leveraging existing tools for validation, formatting, viewing, parsing for custom purposes, etc.
* Clear error messages
* CLI tool for code generation. Easy to use from the command line, easy to use in any build system
* CLI tool for client access to the embedded device. Easy to use and install, even for the non-techies in your team

LotusRPC aims to be extensible, although it is not yet as extensible as it could be. It is already possible to extend the Python client code with new transport layers. Serial is supported out of the box, but e.g. Bluetooth and TCP are not. It would be nice to also have the code generation part extensible to allow users to support other languages, but this is not in place yet.

## Features

### Supported data types

* basic types: `(u)intx_t`, `float`, `double`, `bool`

* string
  * Fixed size: e.g., `string_10` for a maximum size of 10 characters (excluding termination character)
  * Automatic size: `string`. For this type the number of bytes that is transferred is determined by how long the actual string is. This can be different for every RPC function call, contrary to the fixed size string. An auto string is represented in the generated code with `etl::string_view`.
* array
  * Array can be any of the other supported types
  * Enabled by using the `count` setting in the definition file with any value larger than 1
* optional
  * Can be used with any type
  * Translated to `etl::optional` in the generated C++ code
  * Enabled by using the `count` setting in the definition file with a value `?`
* custom
  * struct
    * A custom struct can have any number of fields of any type except `string`, even other custom types
    * A custom struct can be used as a function argument or function return type by referencing it with a `@`-prefix
  * enum
    * A custom enum can have any number of fields
    * Translated to an `enum class` in the generated C++ code

### Multiple return values

Multiple return values for a function are supported. In the generated C++ code this feature is translated to a function returning a `std::tuple`

### Interface definition file

The interface definition file is in YAML format. This makes it easy to parse in many languages and use it for any other purpose that you may need. There is a schema for the interface definition file to provide code completion and error checking in editors that support JSON schema.

### Code generation in a namespace

All code is generated in the namespace specified in the interface definition file. If no namespace is specified, all code is generated in the global namespace

### Configuration of receive and transmit buffer size

Receive and transmit buffer sizes can be configured in the interface definition file. If not specified, both take the value of 256 bytes

### Fully configurable service and function IDs

Every LRPC service has an ID with a value between 0 and 254 (ID 255 is reserved for). This means that LRPC supports a maximum of 255 services. Duplicate service IDs are not allowed. The service ID can optionally be specified in the definition file. If it is not specified an ID is generated, starting with 0 for the first service, 1 for the second service, etc. It is possible to specify only some service IDs and let the rest be generated automatically. For example, if a definition contains 4 services, but only the third service has a specified ID of 17, then the resulting service IDs are [0, 1, 17, 18]

The same applies to LRPC functions inside a service.

### Platform independent

LRPC uses Python to generate code and can therefore be used on all platforms that support Python. The generated C++ code is C++11 compatible and can be compiled for any platform with a suitable compiler.

> **DISCLAIMER:** All development is done on Windows. Continuous integration is done with Github Actions on Ubuntu.

## Example definition

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
