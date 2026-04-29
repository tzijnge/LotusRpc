---
title: Settings reference
toc: true
toc_icon: sliders-h
---

## Settings

LotusRPC allows some level of customization through the optional `settings` section in the definition file.

| Property               | Type/value      | Default            |
|------------------------|-----------------|--------------------|
| rx_buffer_size         | At least 3      | 256                |
| tx_buffer_size         | At least 3      | 256                |
| namespace              | String          | (global namespace) |
| version                | String          | (empty)            |
| definition_hash_length | 0 to 64         | 64                 |
| embed_definition       | Boolean         | false              |
| byte_type              | See table below | uint8_t            |

### rx_buffer_size / tx_buffer_size

Define the receive and transmit buffer sizes in bytes for the generated C++ server code.

### namespace

The C++ namespace to generate server code in. By default, code is generated in the global namespace.

### version

A user-defined version string for the definition. When specified, LotusRPC uses it to detect mismatches between client and server (via the [version](meta.md#version) function in the meta service).

### definition_hash_length

By default, `lrpcg` computes a sha3-256 hash of the definition file during code generation. The resulting 64-character string is embedded in the server and used to detect client/server mismatches via the [version](meta.md#version) function. Set `definition_hash_length` to truncate the hash to any length from 0 to 64.

### embed_definition

When set to `true`, `lrpcg` compresses the definition file and embeds it in the generated C++ code as a constant `uint8_t` array. Defaults to `false`.

The embedded definition can be retrieved by the client in two ways:

- Call the [from_server](python_client.md#from_server) factory method of the `LrpcClient` class
- Set `definition_from_server` to `always` or `once` in the [lrpcc](tools.md#lrpcc) config file

### byte_type

Controls the element type that LotusRPC uses internally for `lrpc::bytearray`. See [Protocol internals — Bytearray](binary.md#bytearray) for encoding details.

| Byte type       | Remark                                            |
|-----------------|---------------------------------------------------|
| `uint8_t`       | Default                                           |
| `int8_t`        |                                                   |
| `char`          |                                                   |
| `char8_t`       | Requires at least C++20. Not enforced by LotusRPC |
| `unsigned char` |                                                   |
| `signed char`   |                                                   |
| `etl::byte`     |                                                   |
| `std::byte`     | Requires at least C++17. Not enforced by LotusRPC |

## User settings

The `user_settings` section allows free-format data in the definition file. Any valid YAML structure is accepted under `user_settings`. LotusRPC ignores this section internally but makes it available when visiting a `LrpcDef` object with a custom `LrpcVisitor`. See [Extending LotusRPC](extending_lrpc.md#visiting-lrpcdef) for details.

A common use for `user_settings` is to define anchors that can be referenced elsewhere in the definition — for example, a shared array size:

``` yaml
user_settings:
  my_array_size: &array_size 55

services:
  - name: srv0
    functions:
      - name: f0
        params:
          - name: my_array
            type: uint16_t
            count: *array_size
```

## Type aliases

LotusRPC defines the following type aliases in the generated C++ code:

| Alias               | Underlying type               | Notes                                |
|---------------------|-------------------------------|--------------------------------------|
| `lrpc::byte`        | `uint8_t` (default)           | Configurable via `byte_type` setting |
| `lrpc::bytearray`   | `etl::span<const lrpc::byte>` | View over a byte buffer              |
| `lrpc::string_view` | `etl::string_view`            | View over a string buffer            |
| `lrpc::span`        | `etl::span`                   | Generic span                         |
| `lrpc::array`       | `std::array`                  | Fixed-size array                     |
| `lrpc::optional`    | `etl::optional`               | Optional value                       |

## Parameter and return value ownership

In LotusRPC, incoming bytes are decoded from the server receive buffer and forwarded to your function implementation as arguments. Return values are encoded back into the server transmit buffer. LotusRPC uses value semantics as much as possible, with a few exceptions for efficiency.

**Note:** Returning a reference of any kind to a local variable leads to undefined behavior in C++. The ownership rules below follow the same principle.
{: .notice--warning}

| Type                                                  | Parameter semantics                                               | Return semantics                                                                 |
|-------------------------------------------------------|-------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Scalar (`(u)intN_t`, `bool`, `float`, `double`, enum) | Passed by value                                                   | Returned by value                                                                |
| Struct                                                | Decoded into a local copy, passed by `const&`                     | Returned by value                                                                |
| String (fixed or auto)                                | `lrpc::string_view` into the receive buffer                       | `lrpc::string_view` — caller must ensure the viewed string outlives the function |
| Array                                                 | Decoded into a local copy (for alignment), passed as `lrpc::span` | `lrpc::span` — same lifetime rules as string                                     |
| Bytearray                                             | `lrpc::bytearray` (span) into the receive buffer                  | `lrpc::bytearray` — same lifetime rules as string                                |

For strings, arrays and bytearrays: the parameter can be used safely inside the function, but must be copied if needed beyond the call. Struct fields that are strings or bytearrays follow the same rules as standalone strings/bytearrays.

## Multiple return values

A function can return any number of values. In the generated C++ code, multiple return values are expressed as a `std::tuple`. To improve readability when the tuple type is complex, use `returns_alias` to give the return type a short name:

``` yaml
functions:
  - name: get_log
    returns_alias: LogChunk
    returns:
      - name: entries
        type: string_64
        count: 5
      - name: count
        type: uint32_t
```

The generated C++ function signature becomes `LogChunk get_log()` instead of the verbose tuple type.
