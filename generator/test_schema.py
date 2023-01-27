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
    assert len(errors) == 1
    assert "Duplicate enum field name(s): [('e0', 'f'), ('e1', 'g')]" in errors

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
    assert len(errors) == 1
    assert "Duplicate enum field id(s): [('e0', 111), ('e1', 222)]" in errors

def test_duplicate_enum_names():
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
  - name: "e0"
    fields:
      - name: "f1"
        id: 222
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Duplicate struct/enum name(s): ['e0']" in errors

def test_duplicate_struct_names():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "a"
    id: 0
    functions:
      - name: "a"
        id: 0
structs:
  - name: "s0"
    fields:
      - name: "f0"
        type: uint64_t
  - name: "s0"
    fields:
      - name: "f1"
        type: bool
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Duplicate struct/enum name(s): ['s0']" in errors

def test_duplicate_struct_enum_names():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "a"
    id: 0
    functions:
      - name: "a"
        id: 0
structs:
  - name: "s0"
    fields:
      - name: "f0"
        type: uint64_t
enums:
  - name: "s0"
    fields:
      - name: "f1"
        id: 111
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Duplicate struct/enum name(s): ['s0']" in errors

def test_duplicate_struct_field_names():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "a"
    id: 0
    functions:
      - name: "a"
        id: 0
structs:
  - name: "s0"
    fields:
      - name: "f"
        type: int8_t
      - name: "f"
        type: float
  - name: "s1"
    fields:
      - name: "g"
        type: bool
      - name: "g"
        type: uint32_t
'''
    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Duplicate struct field name(s): [('s0', 'f'), ('s1', 'g')]" in errors

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
    assert len(errors) == 1
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
    assert len(errors) == 1
    assert "Duplicate interface id(s): [111]" in errors

def test_duplicate_function_ids():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 111
      - name: "f1"
        id: 111
  - name: "i1"
    id: 1
    functions:
      - name: "f0"
        id: 111
      - name: "f1"
        id: 111
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Duplicate function id(s): [('i0', 111), ('i1', 111)]" in errors

def test_duplicate_function_names():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 111
      - name: "f0"
        id: 222
  - name: "i1"
    id: 1
    functions:
      - name: "f1"
        id: 111
      - name: "f1"
        id: 222
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Duplicate function name(s): [('i0', 'f0'), ('i1', 'f1')]" in errors

def test_undeclared_custom_type():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 111
        params:
          - name: "p0"
            type: "@MyType1"
        returns:
          - name: "r0"
            type: "@MyType2"
          - name: "r1"
            type: "@MyType2"
      - name: "f1"
        id: 222
        params:
          - name: "p0"
            type: "@MyType0"
          - name: "p1"
            type: "@MyType4"
        returns:
          - name: "r0"
            type: bool
structs:
  - name: "MyType0"
    fields:
      - name: "f0"
        type: "@MyType3"
      - name: "f1"
        type: "int8_t"
enums:
  - name: "MyType4"
    fields:
      - name: "f1"
        id: 0
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Undeclared custom type(s): ['MyType1', 'MyType2', 'MyType3']" in errors

def test_auto_string_not_allowed_in_struct():
    rpc_def = \
'''namespace: "a"
interfaces:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 111
structs:
  - name: "s0"
    fields:
      - name: "f0"
        type: "string_auto"
  - name: "s1"
    fields:
      - name: "f1"
        type: "string_auto"
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Auto string not allowed in struct: [('s0', 'f0'), ('s1', 'f1')]" in errors

def test_only_one_auto_string_param_or_return_allowed():
    rpc_def = \
'''namespace: "ns"
interfaces:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 0
        params:
          - name: "p0"
            type: string_auto
          - name: "p1"
            type: "string_auto"
        returns:
          - name: "r0"
            type: bool
          - name: "r1"
            type: "string_auto"
      - name: "f1"
        id: 1
        params:
          - name: "p0"
            type: string_auto
          - name: "p1"
            type: "bool"
        returns:
          - name: "r0"
            type: string_auto
          - name: "r1"
            type: "string_auto"
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "More than one auto string per parameter list or return value list is not allowed: [('f0', 'p0'), ('f0', 'p1'), ('f1', 'r0'), ('f1', 'r1')]" in errors

def test_array_of_auto_strings_is_not_allowed():
    rpc_def = \
'''namespace: "ns"
interfaces:
  - name: "i0"
    id: 0
    functions:
      - name: "f2"
        id: 2
        params:
          - name: "p0"
            type: string_auto
            count: 10
        returns:
          - name: "r0"
            type: string_auto
            count: 10
'''

    errors = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert "Array of auto strings is not allowed: [('f2', 'p0'), ('f2', 'r0')]" in errors