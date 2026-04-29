---
title: Extending LotusRPC
toc: true
toc_icon: plug
---

**Audience:** This page is for advanced users who want to build tools on top of LotusRPC or integrate a custom transport layer.
{: .notice--info}

## Visiting LrpcDef

LotusRPC parses the interface definition file (_*.lrpc.yaml_) into an object of type `LrpcDef`. The visitor pattern is used for various internal operations to separate traversal of the `LrpcDef` data structure and the operations done on that data. It is possible to create a custom visitor and hook into the `LrpcDef` data structure. Simply derive from `LrpcVisitor`, implement the visit methods you are interested in and pass the visitor to `LrpcDef.accept()`.

For the full visitor API — traversal order and all visit methods — see the [Python visitor API](../python-api/visitor.md). For the attributes of the objects passed to visit methods, see the [Python definition model](../python-api/definition.md).

## Extending LRPCC

**lrpcc** is the client CLI app for LotusRPC and can work with different transport layers. A serial port transport layer is included with LotusRPC, but it's easy to make **lrpcc** work with your own transport layer by following these steps:

1. Create a Python file called lrpcc_my_transport.py in the working directory of **lrpcc**
2. This file should contain at least a class called `Transport`
3. The `Transport` class should adhere to the `lrpc.client.LrpcTransport` protocol. I.e. it should have these methods
    * `read(count:int = 1) -> bytes`. In case of timeout, read should return an empty `bytes` object
    * `write(data: bytes) -> None`
4. Use your transport layer by updating the _lrpcc.config.yaml_ file with
    * `transport_type: my_transport`
    * `transport_params` is a list of parameters that is passed to your `Transport` class constructor

**lrpcc** will first try to load a user supplied transport layer as specified in _lrpcc.config.yaml_. If no transport layer is found it will try to load a built-in transport layer with the same name.

## Extending LRPCG

Custom code generation backends for **lrpcg** are not yet supported. The architecture allows for it, but the extension points are not yet exposed. If this is something you need, please open an issue or discussion on [GitHub](https://github.com/tzijnge/LotusRpc).
