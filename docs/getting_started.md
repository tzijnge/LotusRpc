---
title: Getting started
toc: true
---

lorem ipsum

## Concepts and terminology
lorem ipsum

## Installation
lorem ipsum

## Write interface definition
lorem ipsum

## Generate code
lorem ipsum

## Use RPC (server side)
Include the file `<out-dir>/example/battery_ServiceShim.hpp` in your project. Derive you own service class from `ex::batteryServiceShim` and implement all pure virtual functions. These are the remote procedures that are called when issuing a function call on the client. Implement these functions as desired.

Include the file `<out-dir>/example/example.hpp` in your project. This file gives access to the LRPC server class called `ex::example`. Instantiate your service class(es) and register them to the server with `ex::example::registerService`. Feed incoming bytes to the server by calling the `ex::example::decode` function. You are responsible for making sure this data is correct.

### Using streams
Streams are LotusRpc's way of sending many messages in one direction with as little latency as possible. This means that, other than with normal function calls, there is no response to a message.

LotusRpc has two main types of streams. A stream originating from the server and a stream originating from the client. In both cases the client is considered the master in the system; it determines when to start and stop a stream. LotusRpc also makes distinction between finite streams and infinite streams. All cases are covered below with a sequence diagram.

In the case of a client to server stream, the client just starts sending messages and the server will have to handle them. The client can stop sending at any time. Alternatively, the server can send a `requestStop` message to the client to indicate that it does not want to receive any more data. This message is optional and it is left up to the client application what to do with this message. I.e., LotusRpc only provides the infrastructure, but does not enforce any particular behavior.

``` mermaid
sequenceDiagram
    title: Basic client stream

    Client ->> Server: message 1
    Client ->> Server: message 2
    Client ->> Server: message n
    Server ->> Client: requestStop
```

In case of a server to client stream, the client starts the stream by sending the `start` command. It can stop the stream at any time by sending the `stop` command. Again, LotusRpc provides the infrastructure for starting and stopping a stream, but is left up to the server and client applications how to handle these commands. LotusRpc does not enforce actual starting and stopping. In fact, the server could start sending stream data without even receiving a `start` command.

``` mermaid
sequenceDiagram
    title: Basic server stream

    Client ->> Server: start
    Server ->> Client: message 1
    Note over Server, Client: ...
    Server ->> Client: message n
    Client ->> Server: stop
```
Both stream variants can be finite or infinite (default). In case of a finite stream, the stream message gets an additional boolean parameter called `final` to indicate if a message is the last one in the stream (`final` is true) or not (`final` is false). This allows the receiving side to take appropriate action upon receiving the last message in the stream.

``` mermaid
sequenceDiagram
    title: Finite client stream

    Client ->> Server: message 1 [final=false]
    Client ->> Server: message 2 [final=false]
    Client ->> Server: message 3 [final=true]
```

``` mermaid
sequenceDiagram
    title: Finite server stream

    Client ->> Server: start
    Server ->> Client: message 1 [final=false]
    Note over Server, Client: ...
    Server ->> Client: message n [final=true]
```

## Use RPC (client side)
lorem ipsum