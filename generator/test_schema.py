import pytest
import jsonschema
import yaml

def test_missing_namespace():
    with open('generator/test.lrpc.yaml') as def_file, open('generator/lotusrpc-schema.json') as schema_file:
        definition = yaml.safe_load(def_file)
        schema = yaml.safe_load(schema_file)
        jsonschema.validate(definition, schema)

        with open('generator/test.lrpc.yaml', 'r') as stream:
            try:
                a= yaml.safe_load(stream)
                print(a)
            except yaml.YAMLError as exc:
                print(exc)
