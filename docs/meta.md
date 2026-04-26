---
title: Meta service
toc: true
toc_icon: server
---

**Audience:** This page covers LotusRPC internals used automatically by the framework. Most users do not need to interact with the meta service directly.
{: .notice--info}

## Background

A LotusRPC connection between client and server contains one service that is not (completely) user defined. This is called the meta service and it contains various functions that are used by LotusRPC internally for error handling and general improved user experience. Some of the functions in the meta service can be enabled or disabled by the user in the definition file to find the right trade-off between performance and usability, but the meta service itself is always there.

## Implementation details

The meta service has a [service ID](reference.md#service-id) of 255. It is not possible to use this ID for any user services.

The meta service is named `LrpcMeta` and internally treated like any other service. It is therefore not possible to create a user service with that name.

The error stream in the meta service uses an enumeration for the error type with name `LrpcMetaError`. It is therefore not possible to create a user type with that name.

## Functions and streams

Streams start at function/stream ID 0, while functions start at ID 128. This leaves room for future streams while not having to change any function IDs.

### Error

The `error` stream implements error reporting from the server back to the client. Although it is implemented as a stream it can be viewed as a single response message to a request of any type. E.g., when the LotusRPC definitions on client and server side are out of sync, the client may call a function that does not exist on the server. In that case the server will respond with an error message.

The error stream has the following parameters

* type (`LrpcMetaError`)
* p1 (`uint8_t`)
* p2 (`uint8_t`)
* p3 (`int32_t`)
* message (`string`)

The parameters have generic names because their meaning depends on error type.

`LrpcMetaError` is an enumeration that holds the error types that can be reported:

* `UnknownService`
* `UnknownFunctionOrStream`

The following table shows the meaning of the error parameters for each error type

| Error type                | p1         | p2                 | p3     | message |
|---------------------------|------------|--------------------|--------|---------|
| `UnknownService`          | service ID | function/stream ID | unused | unused  |
| `UnknownFunctionOrStream` | service ID | function/stream ID | unused | unused  |

### Version

The `version` function takes no arguments and returns three fields that together identify the exact state of the server:

| Field             | Type   | Content                                                                                                                                                                                                                    |
|-------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `definition`      | string | User-supplied version string from [`settings.version`](reference_settings.md#version). Empty string if not set.                                                                                                               |
| `definition_hash` | string | SHA3-256 of the rendered YAML definition file (UTF-8), as a 64-character hex string. Optionally truncated — see [`definition_hash_length`](reference_settings.md#definition_hash_length). Empty string if length is set to 0. |
| `lrpc`            | string | Version of the LotusRPC package used to run `lrpcg` when generating the server code.                                                                                                                                       |

`definition_hash` is the strongest signal: it changes whenever any part of the definition changes, regardless of whether the user set a `version` string. The hash is computed from the complete YAML as LotusRPC parses it, so whitespace-only edits that don't change the parsed content do not change the hash.

## Version mismatch behavior

### Proactive check

`lrpcc` calls `version()` on startup and compares all three fields against the client-side values. If any field differs, it logs a warning before continuing:

``` batch
Server mismatch detected. Details client vs server:
  LotusRPC version : 0.10.0 vs 0.9.7
  Definition version : 1.2 vs 1.1
  Definition hash : 3a7f1c9b2e... vs 9d4f0c1a8b...
```

A mismatch is a **warning, not a hard error** — `lrpcc` continues and attempts the requested function call. This makes it easy to discover drift without blocking automated scripts. Set `check_server_version: false` in `lrpcc.config.yaml` to skip the check entirely.

The `LrpcClient` Python class exposes the same check via `check_server_version()`, which returns `False` if any field mismatches.

### Calling an unknown function or service

If the client calls a function or service that does not exist on the server — for example because the definitions have drifted — the server responds immediately with an `error` stream message instead of a function response:

| Scenario                                | `type`                    | `p1`       | `p2`               |
|-----------------------------------------|---------------------------|------------|--------------------|
| Service ID not registered               | `UnknownService`          | service ID | function/stream ID |
| Function/stream ID not found in service | `UnknownFunctionOrStream` | service ID | function/stream ID |

The `error` message is delivered through the same transport as any other response. `lrpcc` logs it as a warning and exits. A custom `LrpcClient` receives it as a response with `is_error_response = True`.

**Neither error type raises an exception on the server or crashes the server.** The server discards the frame, sends the error response, and continues processing subsequent requests normally.

### Staying in sync with `definition_from_server`

If the server has [`embed_definition: true`](reference_settings.md#embed_definition) set, `lrpcc` can retrieve the definition directly from the server at startup, eliminating the possibility of a client/server definition drift:

```yaml
definition_from_server: always   # always fetch from server; definition_url is ignored
```

See [`definition_from_server`](tools.md#lrpcc) in the tools reference for the `once` and `never` modes and their trade-offs.

### Definition

The `definition` stream (finite, origin: server) in the meta service returns the embedded definition in chunks as big as possible with the current [tx_buffer_size](reference_settings.md#rx_buffer_size--tx_buffer_size) setting. Each chunk is of type [bytearray](reference.md#lrpctype).

For more info on embedding the definition in the server, see the [settings reference](reference_settings.md#embed_definition).
