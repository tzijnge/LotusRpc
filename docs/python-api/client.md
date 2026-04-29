---
title: Python client API
toc: true
toc_icon: python
---

**Audience:** This page is for Python developers building clients that communicate with a running LotusRPC server.
{: .notice--info}

## Overview

LotusRPC ships a Python client library that lets you call functions and send/receive stream data from Python code. The same library powers `lrpcc` under the hood.

``` python
from lrpc.client import LrpcClient, LrpcResponse
from lrpc.utils import load_lrpc_def
```

## Loading a definition

Both `LrpcClient` and the helper functions need an `LrpcDef` object parsed from the interface definition file. The simplest way is `load_lrpc_def`. For the full `LrpcDef` API see the [Python definition model](definition.md) reference.

``` python
from lrpc.utils import load_lrpc_def

lrpc_def = load_lrpc_def("example.lrpc.yaml")   # path, YAML string, or file object
```

For definitions that use [overlays](../reference/overlays.md), use `DefinitionLoader` instead — see [DefinitionLoader](#definitionloader).

## Transport

`LrpcClient` is transport-agnostic. It communicates through any object that satisfies the `LrpcTransport` protocol:

``` python
class LrpcTransport(Protocol):
    def read(self, count: int = 1) -> bytes: ...
    def write(self, data: bytes) -> None: ...
```

`read` must block until `count` bytes are available and return them. On timeout it should return an empty `bytes` object — `LrpcClient` raises `TimeoutError` in that case. `pyserial`'s `serial.Serial` satisfies this protocol directly.

For a custom transport, see [Extending LotusRPC](../advanced/extending-lrpc.md).

## LrpcClient

``` python
from lrpc.client import LrpcClient
```

### Constructor

``` python
LrpcClient(lrpc_def: LrpcDef, transport: LrpcTransport)
```

### from_server

``` python
LrpcClient.from_server(transport: LrpcTransport, save_to: Path | None = None) -> LrpcClient
```

Class method. Retrieves the embedded definition from the server and constructs a client from it. The server must have [`embed_definition: true`](../reference/settings.md#embed_definition) set. Raises `ValueError` if no definition is found on the server.

If `save_to` is given, the retrieved definition is written to that path as a YAML file.

### communicate

``` python
communicate(service_name: str, function_or_stream_name: str, **kwargs) -> Generator[LrpcResponse, ...]
```

The primary communication method. Encodes the call, writes it to the transport, then reads and yields responses. Pass function arguments or stream parameters as keyword arguments.

Response behavior depends on the call type:

| Call type | Yields |
|-----------|--------|
| Function | Exactly one `LrpcResponse` |
| Server stream, `start=True` | One `LrpcResponse` per message until the stream ends |
| Server stream, `start=False` | Nothing (stop message is sent, no response expected) |
| Client stream | Nothing (message is sent, no response) |

For **finite streams**, the implicit `final` field is automatically removed from each response payload before yielding. Reading continues as long as `final` was `False` on the last message.

``` python
# Function call — yields exactly once
for response in client.communicate("math", "add", a=3, b=7):
    print(response.payload["result"])   # 10

# Server stream — start it and collect messages
for response in client.communicate("sensor", "readings", start=True):
    print(response.payload["value"])

# Stop a server stream
next(client.communicate("sensor", "readings", start=False), None)

# Client stream — fire and forget
next(client.communicate("logger", "write", message="hello"), None)

# Finite client stream — mark the last message
next(client.communicate("logger", "write", message="last", final=True), None)
```

Raises `TimeoutError` if the transport times out while waiting for a response.

### communicate_single

``` python
communicate_single(service_name: str, function_or_stream_name: str, **kwargs) -> LrpcResponse
```

Convenience wrapper that calls `communicate` and returns the first response. Use for regular function calls where exactly one response is expected.

``` python
response = client.communicate_single("math", "add", a=3, b=7)
print(response.payload["result"])   # 10
```

### encode

``` python
encode(service_name: str, function_or_stream_name: str, **kwargs) -> bytes
```

Encodes a request to raw bytes without sending it. Useful for testing or for custom transport implementations.

### decode

``` python
decode(encoded: bytes) -> LrpcResponse
```

Decodes a raw response frame. The frame must be complete (minimum 3 bytes, correct length prefix). Raises `ValueError` for malformed frames or unrecognized service and function IDs.

### check_server_version

``` python
check_server_version() -> bool
```

Calls `LrpcMeta.version()` on the server and compares three fields against client-side values:

| Field | Compared against |
|-------|-----------------|
| LotusRPC package version | installed `lotusrpc` version |
| Definition version string | `settings.version` in the definition |
| Definition hash | SHA3-256 hash of the parsed definition |

Returns `True` if all three match. Logs a warning for each mismatch and returns `False`.

## LrpcResponse

`LrpcResponse` is a dataclass returned by `communicate` and `communicate_single`:

``` python
@dataclass
class LrpcResponse:
    service_name: str
    function_or_stream_name: str
    is_function_response: bool
    is_stream_response: bool
    is_error_response: bool
    is_expected_response: bool
    payload: dict[str, ...]
```

`payload` maps parameter and return value names to their decoded Python values:

| LrpcType | Python type |
|----------|-------------|
| `uint8_t` … `int64_t` | `int` |
| `float`, `double` | `float` |
| `bool` | `bool` |
| `string` | `str` |
| `bytearray` | `bytes` |
| enum | `str` (field name) |
| struct | `dict[str, ...]` |
| array | `list` |
| optional (present) | underlying value |
| optional (absent) | `None` |

**Error responses** are delivered when the server cannot find the requested service or function — for example when the client and server definitions have drifted. `is_error_response` is `True` and `payload` contains `type`, `p1`, and `p2` from the meta error stream. `lrpcc` logs these as warnings; a custom client should inspect `is_error_response` before using the payload. See [Calling an unknown function or service](../advanced/meta.md#calling-an-unknown-function-or-service).

## DefinitionLoader

For definitions that use overlays, use `DefinitionLoader` instead of `load_lrpc_def`:

``` python
from lrpc.utils import DefinitionLoader

loader = DefinitionLoader("base.lrpc.yaml")
loader.add_overlay("overlay1.lrpc.yaml")   # can be called multiple times
loader.add_overlay("overlay2.lrpc.yaml")
lrpc_def = loader.lrpc_def()
```

`DefinitionLoader` accepts a file path (`Path`), a YAML string, or an open file object as `definition_base`. The `warnings_as_errors` parameter (default `True`) controls whether semantic warnings raise exceptions.
