import logging
import jsonschema.exceptions
import pytest

from lrpc.utils import load_lrpc_def_from_str


def load_def(rpc_def: str) -> None:
    _ = load_lrpc_def_from_str(rpc_def, warnings_as_errors=False)


def assert_log_entries(expected_entries: list[str], actual: str) -> None:
    actual_entries = actual.splitlines()
    assert len(actual_entries) == len(expected_entries)
    for e in expected_entries:
        assert e in actual


def test_duplicate_enum_field_names(caplog: pytest.LogCaptureFixture) -> None:
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
    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate field name in enum e0: f", "Duplicate field name in enum e1: g"], caplog.text)


def test_duplicate_enum_field_ids(caplog: pytest.LogCaptureFixture) -> None:
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
    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate field id in enum e0: 111", "Duplicate field id in enum e1: 222"], caplog.text)


def test_duplicate_enum_names(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate name: e0"], caplog.text)


def test_duplicate_struct_names(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate name: s0"], caplog.text)


def test_duplicate_names(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate name: s0", "Duplicate name: s1", "Duplicate name: s2"], caplog.text)


def test_duplicate_struct_field_names(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate struct field name(s): [('s0', 'f'), ('s1', 'g')]"], caplog.text)


def test_duplicate_service_names(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate name: i0", "Duplicate name: i0ServiceShim"], caplog.text)


def test_duplicate_service_ids(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate service id: 111"], caplog.text)


def test_duplicate_function_ids(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(
        ["Duplicate function id in service i0: 111", "Duplicate function id in service i1: 111"], caplog.text
    )


def test_duplicate_function_names(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(
        ["Duplicate function name in service i0: f0", "Duplicate function name in service i1: f1"], caplog.text
    )


def test_invalid_function_name(caplog: pytest.LogCaptureFixture) -> None:
    rpc_def = """name: "test"
services:
  - name: "s0"
    functions:
      - { name: "s0ServiceShim" }
"""

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(
        [
            "Invalid function name: s0ServiceShim. This name is incompatible with the generated code for the containing service"
        ],
        caplog.text,
    )


def test_duplicate_server_name(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    errors = caplog.text.splitlines()
    assert len(errors) == 4
    assert caplog.text.count("Duplicate name: server") == 4


def test_duplicate_constant_names(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Duplicate name: c0", "Duplicate name: c1"], caplog.text)


def test_undeclared_custom_type(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(
        ["Undeclared custom type: MyType1", "Undeclared custom type: MyType2", "Undeclared custom type: MyType3"],
        caplog.text,
    )


def test_unused_custom_type(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.WARNING)
    load_def(rpc_def)
    assert_log_entries(["Unused custom type: s0", "Unused custom type: e0"], caplog.text)


def test_auto_string_not_allowed_in_struct(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Auto string not allowed in struct: [('s0', 'f0'), ('s1', 'f1')]"], caplog.text)


def test_only_one_auto_string_param_allowed(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(
        [
            "More than one auto string per parameter list or return value list is not allowed: [('f0', 'p0'), ('f0', 'p1')]"
        ],
        caplog.text,
    )


def test_array_of_auto_strings_is_not_allowed(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(["Array of auto strings is not allowed: [('f2', 'p0')]"], caplog.text)


def test_auto_string_return_value_is_not_allowed(caplog: pytest.LogCaptureFixture) -> None:
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

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError):
        load_def(rpc_def)

    assert_log_entries(
        [
            "A function cannot return an auto string: [('s0', 'f0', 'r0'), ('s0', 'f1', 'r0'), ('s0', 'f1', 'r1'), ('s0', 'f2', 'r0'), ('s0', 'f3', 'r0')]"
        ],
        caplog.text,
    )


def test_service_id_out_of_range(caplog: pytest.LogCaptureFixture) -> None:
    rpc_def = """name: test
services:
  - name: s0
    id: 254
    functions:
      - name: f0
  - name: s1
    id: 255
    functions:
      - name: f0
"""

    caplog.set_level(logging.ERROR)
    with pytest.raises(jsonschema.ValidationError) as e:
        load_def(rpc_def)

    assert e.value.message == "255 is greater than the maximum of 254"
