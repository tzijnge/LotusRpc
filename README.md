![example workflow](https://github.com/tzijnge/LotusRpc/actions/workflows/cmake.yml/badge.svg)

# LotusRpc
RPC framework for embedded systems based on [ETL](https://github.com/ETLCPP/etl)

## Using the schema in VS Code
* Install the [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension
* In the global or local settings.json, add the following entry: `"yaml.schemas": { "/path/to/LotusRpc/generator/lotusrpc-schema.json": "*.lrpc.yaml"}`
* Now every file with `.lrpc.yaml` extension will get code completion and validation in VS Code
