---
title: lrpcg
toc: true
toc_icon: tools
---

`lrpcg` is the LotusRPC code generator. It takes a YAML interface definition file and generates all C++ server code needed to run an LotusRPC server. `lrpcg` is installed as a command line tool with LotusRPC and can be called from any location.

Basic usage: `lrpcg cpp -d example.lrpc.yaml -o output-dir`

For more info type `lrpcg --help`

## C++ server side code generation

The `cpp` command generates all C++ files needed for the RPC server.

`lrpcg cpp -d example.lrpc.yaml -o output-dir`

Definition overlays can be specified with one or more `-ov` options. A single overlay may contain multiple [YAML documents](https://yaml.org/spec/1.2.2/#91-documents). For more information about definition overlays see [Definition overlays](../reference/overlays.md).

For more info type `lrpcg cpp --help`

## Overlay merge

Basic usage: `lrpcg merge -d base.lrpc.yaml -ov overlay1.lrpc.yaml -ov overlay2.lrpc.yaml -o result.lrpc.yaml`

The `merge` command merges the specified overlay files into the base definition and saves the result to a new file. See the [cpp command](#c-server-side-code-generation) for details about the overlay files.

For more info type `lrpcg merge --help`

## C++ server core code generation

The `cppcore` command generates only the core files of the RPC server. These files are static and do not depend on the definition file. In some cases it may be beneficial to generate them separately from the rest of the RPC server.

`lrpcg cppcore -o output-dir`

For more info type `lrpcg cppcore --help`

## Schema export

The `schema` command exports the [LotusRPC definition schema](../reference/schema.md) to the specified directory.

`lrpcg schema -o output-dir`

For more info type `lrpcg schema --help`

## PlantUML diagram

The `puml` command transforms your LotusRPC definition file into a PlantUML diagram. The output of this command is a _.puml_ file that can be rendered to an image with PlantUML. This can be useful for documentation purposes

`lrpcg puml -o output-dir`

For more info type `lrpcg puml --help`
