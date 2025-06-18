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
``` mermaid
sequenceDiagram
    title: Basic client stream

    Server ->> Client: message 1
    Server ->> Client: message 2
    Server ->> Client: message n
    Client ->> Server: requestStop
```

``` mermaid
sequenceDiagram
    title: Basic server stream

    Server ->> Client: start
    Client ->> Server: message 1
    Note over Client, Server: ...
    Client ->> Server: message n
    Server ->> Client: stop
```

``` mermaid
sequenceDiagram
    title: Finite client stream

    Server ->> Client: message 1 [final=false]
    Server ->> Client: message 2 [final=false]
    Server ->> Client: message 3 [final=true]
```

``` mermaid
sequenceDiagram
    title: Finite server stream

    Server ->> Client: start
    Client ->> Server: message 1 [final=false]
    Note over Client, Server: ...
    Client ->> Server: message n [final=true]
```

## Use RPC (client side)
lorem ipsum