from importlib import resources
from typing import List, Tuple

import jsonschema
import yaml
from lrpc import schema as lrpc_schema
from lrpc.core import LrpcDef
from lrpc.validation import SemanticAnalyzer


def semantic_errors(rpc_def: str) -> Tuple[List[str], List[str]]:
    url = resources.files(lrpc_schema) / "lotusrpc-schema.json"

    # Not sure how to make type hints work from Traversable to PathLike, hence ignored
    with open(url, mode="rt", encoding="utf8") as schema_file:  # type: ignore[call-overload]
        definition = yaml.safe_load(rpc_def)
        schema = yaml.safe_load(schema_file)
        jsonschema.validate(definition, schema)

        sa = SemanticAnalyzer(LrpcDef(definition))
        sa.analyze()
        return sa.errors, sa.warnings


def test_duplicate_enum_field_names() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""
    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 2
    assert len(warnings) == 2
    assert "Duplicate field name in enum e0: f" in errors
    assert "Duplicate field name in enum e1: g" in errors


def test_duplicate_enum_field_ids() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 2
    assert len(warnings) == 2
    assert "Duplicate field id in enum e0: 111" in errors
    assert "Duplicate field id in enum e1: 222" in errors


def test_duplicate_enum_names() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 1
    assert "Duplicate name: e0" in errors


def test_duplicate_struct_names() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 1
    assert "Duplicate name: s0" in errors


def test_duplicate_names() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
  - name: "s0"
    id: 0
    functions:
      - name: "a"
        id: 0
structs:
  - name: "s1"
    fields:
      - name: "f0"
        type: uint64_t
enums:
  - name: "s2"
    fields:
      - name: "f1"
        id: 111
constants:
  - name: s0
    value: 123
  - name: s1
    value: 123
  - name: s2
    value: 123
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 3
    assert len(warnings) == 2
    assert "Duplicate name: s0" in errors
    assert "Duplicate name: s1" in errors
    assert "Duplicate name: s2" in errors


def test_duplicate_struct_field_names() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""
    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 2
    assert "Duplicate struct field name(s): [('s0', 'f'), ('s1', 'g')]" in errors


def test_duplicate_service_names() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 2
    assert len(warnings) == 0
    assert "Duplicate name: i0" in errors
    assert "Duplicate name: i0ServiceShim" in errors


def test_duplicate_service_ids() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 0
    assert "Duplicate service id: 111" in errors


def test_duplicate_function_ids() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 2
    assert len(warnings) == 0
    assert "Duplicate function id in service i0: 111" in errors
    assert "Duplicate function id in service i1: 111" in errors


def test_duplicate_function_names() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 2
    assert len(warnings) == 0
    assert "Duplicate function name in service i0: f0" in errors
    assert "Duplicate function name in service i1: f1" in errors


def test_invalid_function_name() -> None:
    rpc_def = """name: "test"
services:
  - name: "s0"
    functions:
      - { name: "s0ServiceShim" }
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 0
    assert (
        "Invalid function name: s0ServiceShim. This name is incompatible with the generated code for the containing service"
        in errors
    )


def test_duplicate_server_name() -> None:
    rpc_def = """name: "server"
services:
  - name: "server"
    functions:
      - { name: "f0" }
constants:
  - name: server
    cppType: bool
    value: true
enums:
  - { name: server, fields: [V0]}
structs:
  - name: server
    fields: [{name: f1, type: bool}]
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 4
    assert len(warnings) == 1
    assert errors.count("Duplicate name: server") == 4


def test_duplicate_constant_names() -> None:
    rpc_def = """name: "test"
constants:
  - name : c0
    value : 1
  - name : c0
    value : 2
  - name : c1
    value : 1
  - name : c1
    value : 2 
services:
  - name: "s0"
    functions:
      - name: "f0"
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 2
    assert len(warnings) == 0
    assert "Duplicate name: c0" in errors
    assert "Duplicate name: c1" in errors


def test_undeclared_custom_type() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
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
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 3
    assert len(warnings) == 0
    assert "Undeclared custom type: MyType1" in errors
    assert "Undeclared custom type: MyType2" in errors
    assert "Undeclared custom type: MyType3" in errors


def test_unused_custom_type() -> None:
    rpc_def = """name: "test"
namespace: "ns"
services:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 0
        params:
          - name: "p0"
            type: bool
structs:
  - name: "s0"
    fields:
      - name: "f0"
        type: bool
enums:
  - name: "e0"
    fields:
      - name: "f0"
        id: 0
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 0
    assert len(warnings) == 2
    assert "Unused custom type: s0" in warnings
    assert "Unused custom type: e0" in warnings


def test_auto_string_not_allowed_in_struct() -> None:
    rpc_def = """name: "test"
namespace: "a"
services:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 111
structs:
  - name: "s0"
    fields:
      - name: "f0"
        type: "string"
  - name: "s1"
    fields:
      - name: "f1"
        type: "string"
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 2
    assert "Auto string not allowed in struct: [('s0', 'f0'), ('s1', 'f1')]" in errors


def test_only_one_auto_string_param_allowed() -> None:
    rpc_def = """name: "test"
namespace: "ns"
services:
  - name: "i0"
    id: 0
    functions:
      - name: "f0"
        id: 0
        params:
          - name: "p0"
            type: string
          - name: "p1"
            type: "string"
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 0
    assert (
        "More than one auto string per parameter list or return value list is not allowed: [('f0', 'p0'), ('f0', 'p1')]"
        in errors
    )


def test_array_of_auto_strings_is_not_allowed() -> None:
    rpc_def = """name: "test"
namespace: "ns"
services:
  - name: "i0"
    id: 0
    functions:
      - name: "f2"
        id: 2
        params:
          - name: "p0"
            type: string
            count: 10
"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 0
    assert "Array of auto strings is not allowed: [('f2', 'p0')]" in errors


def test_auto_string_return_value_is_not_allowed() -> None:
    rpc_def = """name: "test"
namespace: "ns"
services:
  - name: "s0"
    id: 0
    functions:
      - name: "f0"
        id: 0
        returns:
          - name: "r0"
            type: string
      - name: "f1"
        id: 1
        returns:
          - name: "r0"
            type: string
          - name: "r1"
            type: string
      - name: "f2"
        id: 2
        returns:
          - name: "r0"
            type: string
            count: "?"
      - name: "f3"
        id: 3
        returns:
          - name: "r0"
            type: string
            count: 10

"""

    errors, warnings = semantic_errors(rpc_def)
    assert len(errors) == 1
    assert len(warnings) == 0
    assert (
        "A function cannot return an auto string: [('s0', 'f0', 'r0'), ('s0', 'f1', 'r0'), ('s0', 'f1', 'r1'), ('s0', 'f2', 'r0'), ('s0', 'f3', 'r0')]"
        in errors
    )
