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
- Set `definition_from_server` to `always` or `once` in the [lrpcc](lrpcc.md) config file

### byte_type

Controls `lrpc::byte` alias used internally for `lrpc::bytearray`. See [C++ API — Type aliases](cpp_api.md#type-aliases) and [Protocol internals — Bytearray](binary.md#bytearray) for details.

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

