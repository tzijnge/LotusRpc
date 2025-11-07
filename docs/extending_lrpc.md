---
title: Extending LotusRPC
toc: true
---

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

It is not currently possible to add custom code generation to **lrpcg**, the LotusRPC generator tool.
