import pytest
import jsonschema
import yaml
from SematicAnalyzer import SemanticAnalyzer

def semantic_errors(rpc_def):
    with open('generator/lotusrpc-schema.json') as schema_file:
        definition = yaml.safe_load(rpc_def)
        schema = yaml.safe_load(schema_file)
        jsonschema.validate(definition, schema)

        sa = SemanticAnalyzer()
        sa.analyze(definition)
        return sa.errors

def test_missing_namespace():
    with open('generator/test.lrpc.yaml') as def_file, open('generator/lotusrpc-schema.json') as schema_file:
        definition = yaml.safe_load(def_file)
        schema = yaml.safe_load(schema_file)
        jsonschema.validate(definition, schema)


def test_duplicate_enum_field_names():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "a"
    id: 0
    functions:
      - name: "a"
        id: 0
enums:
  - name: "e0"
    fields:
      - name: "f"
        id: 0
      - name: "f"
        id: 1
  - name: "e1"
    fields:
      - name: "g"
        id: 0
      - name: "g"
        id: 1
'''
    errors = semantic_errors(rpc_def)
    assert "Duplicate enum name(s): [('e0', 'f'), ('e1', 'g')]" in errors

def test_duplicate_enum_field_ids():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "a"
    id: 0
    functions:
      - name: "a"
        id: 0
enums:
  - name: "e0"
    fields:
      - name: "f0"
        id: 111
      - name: "f1"
        id: 111
  - name: "e1"
    fields:
      - name: "f0"
        id: 222
      - name: "f1"
        id: 222
'''

    errors = semantic_errors(rpc_def)
    assert "Duplicate enum field id(s): [('e0', 111), ('e1', 222)]" in errors

def test_duplicate_interface_names():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 0
  - name: "i0"
    id: 1
    functions:
      - name: "f1"
        id: 1
'''

    errors = semantic_errors(rpc_def)
    assert "Duplicate interface name(s): ['i0']" in errors

def test_duplicate_interface_ids():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "i0"
    id: 111
    functions:
      - name: "f0"
        id: 0
  - name: "i1"
    id: 111
    functions:
      - name: "f1"
        id: 1
'''

    errors = semantic_errors(rpc_def)
    assert 'Duplicate interface id(s): [111]' in errors
