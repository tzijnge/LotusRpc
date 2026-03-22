---
title: LotusRPC 🌼
author_profile: true
toc: true
---

RPC framework for embedded systems based on [ETL](https://github.com/ETLCPP/etl). Generates C++ code for your device with no dynamic memory allocations, no exceptions, no RTTI, etc.

> ⚠ **_WARNING:_**  This project is work in progress

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
  * Automatic size: `string`. For this type the number of bytes that is transferred is determined by how long the actual string is. This can be different for every RPC function call, contrary to the fixed size string. An auto string is represented in the generated code with `lrpc::string_view` which is an alias for `etl::string_view`.
* bytearray
This type represents an array of bytes. In Python, a function taking a `bytearray` parameter accepts `bytes`, `bytearray` or `memoryview`. In Python 3.12 any type that implements the `Buffer` protocol (`collections.abc.Buffer`) is accepted. Functions returning a `bytearray` always return a `bytes` object. In C++ `bytearray` translates to `lrpc::bytearray`, see [this section](#type-aliases).

This type was added because in the generated C++ code `bytearray` is more efficient than using a plain array of `uint8_t`. In Python it is convenient to have something that maps to a built-in byte-like type, e.g. for binary blob transfer between client and server.

* array
  * Array can be any of the other supported types
  * Enabled by using the `count` setting in the definition file with any value larger than 1
* optional
  * Can be used with any type
  * Translated to `lrpc::optional` in the generated C++ code
  * Enabled by using the `count` setting in the definition file with a value `?`
* custom
  * struct
    * A custom struct can have any number of fields of any type except `string`, even other custom types
    * A custom struct can be used as a function argument or function return type by referencing it with a `@`-prefix
  * enum
    * A custom enum can have any number of fields
    * Translated to an `enum class` in the generated C++ code

### Type aliases

LotusRPC defines the following type aliases and uses them internally.

* `LRPC_BYTE_TYPE`. Type that LotusRPC uses internally to represent a byte. Defaults to `uint8_t` but can be defined to any other single-byte type,
* `lrpc::bytearray`. Alias for `etl::span<const LRPC_BYTE_TYPE>`
* `lrpc::string_view`. Alias for `etl::string_view`
* `lrpc::span`. Alias for `etl::span`
* `lrpc::array`. Alias for `std::array`
* `lrpc::optional`. Alias for `etl::optional`

### Parameter and return value ownership

In LotusRPC, a remote function call from client to server involves decoding function parameters from the server receive buffer and forwarding them to the user implementation of the remote function. Conversely, a value (or values) returned by the user function is encoded into the server transmit buffer. LotusRPC uses value semantics for these processes as much as possible, but for efficiency there are a few exceptions.

* Strings (fixed size and auto size) use reference semantics. A string function parameter translates to `lrpc::string_view` that views directly into the server receive buffer. This means that the parameter can be used safely inside the function implementation, but the user must make a copy if the string value must be available outside of the function call. A string return value also translates to `lrpc::string_view` and the user must take care that the lifetime of the return value exceeds that of the function it is returned from, at least until the value is copied into the server transmit buffer by LotusRPC. This should be relatively intuitive to an experienced C++ programmer because returning a reference of any kind (`*`, `&`, `string_view`, `span`, etc.) to a local variable leads to undefined behavior.
* Arrays are copied from the server receive buffer to a local `lrpc::array` variable before being passed as a function parameter as `lrpc::span`. The local copy is necessary because an array can hold any other type and the location of the array in the server receive buffer does not necessarily meet the alignment requirements of the contained type. Array type function return values use `lrpc::span`. The semantics for array parameters and returns are the same as for strings.
* Byte arrays are treated the same as strings, but use a different type: `lrpc::bytearray`. Since this type is a view on a range of single-byte values, there is no risk of invalid alignment as with a normal array.
* Struct parameters are copied from the server receive buffer to a local value and then passed by reference (`&`) to the user function. Structs are returned from a function by value. Struct fields are value types, except for strings (`lrpc::string_view`) and byte arrays (`lrpc::bytearray`).

### Multiple return values

Multiple return values for a function are supported. In the generated C++ code this feature is translated to a function returning a `std::tuple`. Because multiple return types can quickly become hard to read in C++ (especially when returning arrays, strings, optionals, etc, that are template types themselves), LotusRpc allows defining a alias for the combined return type with the [`returns_alias`](reference.md#functions) property. This way something complex like `std::tuple<lrpc::array<lrpc::string_view, 5>, uint32_t>` can be aliased to something simple like `LogChunk`.

### Interface definition file

The interface definition file is in YAML format. This makes it easy to parse in many languages and use it for any other purpose that you may need. There is a schema for the interface definition file to provide code completion and error checking in editors that support JSON schema.

### Code generation in a namespace

All code is generated in the namespace specified in the interface definition file. If no namespace is specified, all code is generated in the global namespace

### Configuration of receive and transmit buffer size

Receive and transmit buffer sizes can be configured in the interface definition file. If not specified, both take the value of 256 bytes

### Fully configurable service and function IDs

Every LRPC service has an ID with a value between 0 and 254 (ID 255 is reserved for the [meta service](meta.md)). This means that LRPC supports a maximum of 255 user services. Duplicate service IDs are not allowed. The service ID can optionally be specified in the definition file. If it is not specified an ID is generated, starting with 0 for the first service, 1 for the second service, etc. It is possible to specify only some service IDs and let the rest be generated automatically. For example, if a definition contains 4 services, but only the third service has a specified ID of 17, then the resulting service IDs are [0, 1, 17, 18]

The same applies to LRPC functions inside a service.

### Platform independent

LRPC uses Python to generate code and can therefore be used on all platforms that support Python. The generated C++ code is C++11 compatible and can be compiled for any platform with a suitable compiler.

> **DISCLAIMER:** All development is done on Windows. Continuous integration is done with Github Actions on Ubuntu.

## Example definition

``` yaml
name: example
services:
  - name: battery
    functions:
      - name: get
        params:
          - { name: option, type: "@VoltageScales" }
        returns:
          - { name: voltage, type: double }
enums:
  - name: VoltageScales
    fields:
        name: microvolts
        name: millivolts
        name: volts
```
