---
title: Meta service
toc: true
---

## Background

A LotusRPC connection between client and server contains one service that is not (completely) user defined. This is called the meta service and it contains various functions that are used by LotusRPC internally for error handling and general improved user experience. Some of the functions in the meta service can be enabled or disabled by the user in the definition file to find the right trade-off between performance and usability, but the meta service itself is always there.

## Implementation details

The meta service has a [service ID](reference.md#service-id) of 255. It is not possible to use this ID for any user services.

The meta service is named `LrpcMeta` and internally treated like any other service. It is therefore not possible to create a user service with that name.

The error stream in the meta service uses an enumeration for the error type with name `LrpcMetaError`. It is therefore not possible to create a user type with that name.

## Functions and streams

### Error

The error stream implements error reporting from the server back to the client. Although it is implemented as a stream it can be viewed as a single response message to a request of any type. E.g., when the LotusRPC definitions on client and server side are out of sync, the client may call a function that does not exist on the server. In that case the server will respond with an error message.

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

| Error type | p1 | p2 | p3 | message |
| ---------- | -- | -- | -- | ------- |
| `UnknownService`           | service ID | function/stream ID | unused | unused |
| `UnknownFunctionOrStream`  | service ID | function/stream ID | unused | unused |
