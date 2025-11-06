---
title: Interface definition schema
toc: true
---
## A schema for LotusRPC definition files

LotusRPC generates RPC code from a user definition in YAML. To validate the definition file a schema is used. LotusRPC uses this schema internally, but it can also be very helpful to end users when writing a definition file. Schemas for YAML are supported by a wide range of tools and can offer code completion, documentation and live validation of the definition file

## Installing the schema

There are two ways to get the LotusRPC schema on your PC

1. Download from [GitHub](https://github.com/tzijnge/LotusRpc/blob/main/src/lrpc/schema/lotusrpc-schema.json)
2. Export the schema file from the installed python package. After installation of _lotusrpc_ from [PyPi](https://pypi.org/project/lotusrpc/), run the following command to export the LotusRPC schema to your PC `lrpcg schema -o <out_dir>`

## Using the schema in VS Code

* Install the [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension
* In the global or local settings.json, add the following entry: `"yaml.schemas": { "/path/to/LotusRpc/generator/lotusrpc-schema.json": "*.lrpc.yaml"}`
* Now every file with `.lrpc.yaml` extension will get code completion and validation in VS Code
