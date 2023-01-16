import pytest
import jsonschema
import yaml

def test_missing_namespace():
    with open('generator/test.lrpc.yaml') as def_file, open('generator/lotusrpc-schema.json') as schema_file:
        definition = yaml.safe_load(def_file)
        schema = yaml.safe_load(schema_file)
        jsonschema.validate(definition, schema)


def test_duplicate_enum_fields():
    rpc_def = \
        '''namespace: "a"
interfaces:
  - name: "a"
    id: 0
    functions:
      - name: "a"
        id: 0
enums:
  - name: "e"
    fields:
      - name: "f"
        id: 0
      - name: "f"
        id: 1
'''

    with open('generator/lotusrpc-schema.json') as schema_file:
        definition = yaml.safe_load(rpc_def)
        schema = yaml.safe_load(schema_file)
        jsonschema.validate(definition, schema)

        fields = definition["enums"][0]["fields"]
        field_names = [field["name"] for field in fields]
        unique_field_names = set(field_names)
        print(fields)
