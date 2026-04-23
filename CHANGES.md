---
title: LotusRPC release notes
toc: true
toc_icon: history
---

LotusRPC is an RPC framework for embedded systems. Here are the release notes.

<!-- towncrier release notes start -->

## lotusrpc 0.10.0 (2026-02-27)

### Features

- Added option to embed definition in generated server code. This way server and client can never go out of sync ([#81](https://github.com/tzijnge/LotusRpc/issues/81))
- Added a meta service with ID 255. this service contains an error stream to report internal errors from server to client. The meta service is not directly accessible to users but provides an enhanced user experience ([#83](https://github.com/tzijnge/LotusRpc/issues/83))
- Add version function in meta service. Allows client to check compatibility with server. ([#84](https://github.com/tzijnge/LotusRpc/issues/84))
- Reference semantics for array and string ([#185](https://github.com/tzijnge/LotusRpc/issues/185))

⚠ **Breaking change:** This change may require updates to existing service implementations (classes deriving from `*_shim`).
{: .notice--warning}

- Added bytearray convenience type. LotusRPC bytearray has flexible length, handling in C++ is more efficient than 'array of uint8_t' and is translated to bytes/bytearray/memoryview in Python ([#186](https://github.com/tzijnge/LotusRpc/issues/186))

### Bugfixes

- Fix code generation for array parameter in a stream ([#188](https://github.com/tzijnge/LotusRpc/issues/188))
- Size field now encodes message size minus 1. This way a message of size 256 is possible in a 256-byte receive/transmit buffer. ([#202](https://github.com/tzijnge/LotusRpc/issues/202))

⚠ **Breaking change:** This change causes binary incompatibility with all previous versions of LotusRPC.
{: .notice--warning}

### Misc

- [#16](https://github.com/tzijnge/LotusRpc/issues/16), [#106](https://github.com/tzijnge/LotusRpc/issues/106), [#160](https://github.com/tzijnge/LotusRpc/issues/160), [#167](https://github.com/tzijnge/LotusRpc/issues/167), [#170](https://github.com/tzijnge/LotusRpc/issues/170), [#176](https://github.com/tzijnge/LotusRpc/issues/176)
⚠ **Breaking change:** C++ service shims no longer get a `_ServiceShim` postfix — the suffix is now simply `_shim`.
{: .notice--warning}


## lotusrpc 0.9.7 (2025-11-16)

### Features

- Meta and constants includes are now available in main server include ([#103](https://github.com/tzijnge/LotusRpc/issues/103))
- Using yamllint and markdownlint in development process ([#147](https://github.com/tzijnge/LotusRpc/issues/147))
- LrpcClient is easier to use ([#157](https://github.com/tzijnge/LotusRpc/issues/157))

### Improved Documentation

- Added release notes ([#62](https://github.com/tzijnge/LotusRpc/issues/62))
- Documentation about frame format. General documentation improvements ([#86](https://github.com/tzijnge/LotusRpc/issues/86))

### Deprecations and Removals

- Drop support for Python 3.9 ([#145](https://github.com/tzijnge/LotusRpc/issues/145))
