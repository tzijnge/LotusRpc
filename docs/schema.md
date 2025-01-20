---
title: Interface definition schema
toc: true
---

## S1
lorem ipsum

## Using the schema in VS Code
* Install the [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension
* In the global or local settings.json, add the following entry: `"yaml.schemas": { "/path/to/LotusRpc/generator/lotusrpc-schema.json": "*.lrpc.yaml"}`
* Now every file with `.lrpc.yaml` extension will get code completion and validation in VS Code