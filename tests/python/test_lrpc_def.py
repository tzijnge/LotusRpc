import math
import pytest
from lrpc.utils import load_lrpc_def_from_str
from lrpc.core.definition import LrpcDef


def load_lrpc_def(def_str: str) -> LrpcDef:
    lrpc_def = load_lrpc_def_from_str(def_str, warnings_as_errors=False)
    return lrpc_def


def test_optional_service_id() -> None:
    def_str = """name: "test"
services:
  - name: "a4"
    functions:
      - name: "a"
        id: 0
  - name: "a3"
    functions:
      - name: "a"
        id: 0
  - name: "a2"
    id: 17
    functions:
      - name: "a"
        id: 0
  - name: "a1"
    functions:
      - name: "a"
        id: 0
"""
    lrpc_def = load_lrpc_def(def_str)
    services = lrpc_def.services()
    assert len(services) == 4
    assert services[0].id() == 0
    assert services[1].id() == 1
    assert services[2].id() == 17
    assert services[3].id() == 18


def test_optional_function_id() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "a4"
      - name: "a3"
      - name: "a2"
        id: 17
      - name: "a1"
"""
    lrpc_def = load_lrpc_def(def_str)
    services = lrpc_def.services()
    assert len(services) == 1
    functions = services[0].functions()
    assert len(functions) == 4

    assert functions[0].id() == 0
    assert functions[1].id() == 1
    assert functions[2].id() == 17
    assert functions[3].id() == 18


def test_max_service_id() -> None:
    def_str = """name: "test"
services:
  - name: "a4"
    functions:
      - name: "a"
        id: 0
  - name: "a3"
    id: 43
    functions:
      - name: "a"
        id: 0
  - name: "a2"
    id: 17
    functions:
      - name: "a"
        id: 0
"""
    lrpc_def = load_lrpc_def(def_str)
    assert lrpc_def.max_service_id() == 43


def test_no_constants_no_enums_no_structs() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
"""
    lrpc_def = load_lrpc_def(def_str)
    assert len(lrpc_def.constants()) == 0
    assert len(lrpc_def.enums()) == 0
    assert len(lrpc_def.structs()) == 0


def test_constants() -> None:
    def_str = """name: "test"
constants:
  - name: "c1"
    value: true
  - name: "c2"
    value: 123
  - name: "c3"
    value: 123.456
  - name: "c4"
    value: 123.456
    cppType: double
  - name: "c5"
    value: 123
    cppType: uint64_t
  - name: "c6"
    value: This is a string
services:
  - name: "s1"
    functions:
      - name: "f1"
"""
    lrpc_def = load_lrpc_def(def_str)
    constants = lrpc_def.constants()
    assert len(constants) == 6

    c1 = constants[0]
    assert c1.name() == "c1"
    assert c1.value() is True
    assert c1.cpp_type() == "bool"

    c2 = constants[1]
    assert c2.name() == "c2"
    assert c2.value() == 123
    assert c2.cpp_type() == "int32_t"

    c3 = constants[2]
    assert c3.name() == "c3"
    assert math.isclose(float(c3.value()), 123.456)
    assert c3.cpp_type() == "float"

    c4 = constants[3]
    assert c4.name() == "c4"
    assert math.isclose(float(c4.value()), 123.456)
    assert c4.cpp_type() == "double"

    c5 = constants[4]
    assert c5.name() == "c5"
    assert c5.value() == 123
    assert c5.cpp_type() == "uint64_t"

    c6 = constants[5]
    assert c6.name() == "c6"
    assert c6.value() == "This is a string"
    assert c6.cpp_type() == "string"


def test_enums() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
enums:
  - name: "MyEnum1"
    fields:
      - name: f1
        id: 111
      - name: f2
        id: 222
  - name: "MyEnum2"
    fields: [f1, f2]
"""
    lrpc_def = load_lrpc_def(def_str)
    enums = lrpc_def.enums()
    assert len(enums) == 2

    assert enums[0].name() == "MyEnum1"
    fields = enums[0].fields()
    assert len(fields) == 2
    assert fields[0].name() == "f1"
    assert fields[0].id() == 111
    assert fields[1].name() == "f2"
    assert fields[1].id() == 222

    assert enums[1].name() == "MyEnum2"
    fields = enums[1].fields()
    assert len(fields) == 2
    assert fields[0].name() == "f1"
    assert fields[0].id() == 0
    assert fields[1].name() == "f2"
    assert fields[1].id() == 1


def test_external_enum() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
enums:
  - name: "MyEnum1"
    fields: [f1, f2]
    external: a/b/c/d.hpp
"""
    lrpc_def = load_lrpc_def(def_str)
    enum = lrpc_def.enums()[0]

    assert enum.is_external() is True
    assert enum.external_file() == "a/b/c/d.hpp"


def test_enum_with_omitted_ids() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
enums:
  - name: "MyEnum1"
    fields:
      - name: f1
      - name: f2
      - name: f3
        id: 222
      - name: f4
"""
    lrpc_def = load_lrpc_def(def_str)
    enums = lrpc_def.enums()
    assert len(enums) == 1

    assert enums[0].name() == "MyEnum1"
    fields = enums[0].fields()
    assert len(fields) == 4
    assert fields[0].name() == "f1"
    assert fields[0].id() == 0
    assert fields[1].name() == "f2"
    assert fields[1].id() == 1
    assert fields[2].name() == "f3"
    assert fields[2].id() == 222
    assert fields[3].name() == "f4"
    assert fields[3].id() == 223


def test_structs() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
structs:
  - name: "MyStruct1"
    fields:
      - name: f1
        type: double
      - name: f2
        type: int8_t
  - name: "MyStruct2"
    fields:
      - name: ms1
        type: float
"""
    lrpc_def = load_lrpc_def(def_str)
    structs = lrpc_def.structs()
    assert len(structs) == 2

    assert structs[0].name() == "MyStruct1"
    fields = structs[0].fields()
    assert len(fields) == 2
    assert fields[0].name() == "f1"
    assert fields[0].base_type() == "double"
    assert fields[1].name() == "f2"
    assert fields[1].base_type() == "int8_t"

    assert structs[1].name() == "MyStruct2"
    fields = structs[1].fields()
    assert len(fields) == 1
    assert fields[0].name() == "ms1"
    assert fields[0].base_type() == "float"


def test_external_struct() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
structs:
  - name: "MyStruct2"
    fields:
      - name: ms1
        type: float
    external: a/b/c/d.hpp
    external_namespace: a::b::c
"""
    lrpc_def = load_lrpc_def(def_str)
    struct = lrpc_def.structs()[0]

    assert struct.is_external() is True
    assert struct.external_file() == "a/b/c/d.hpp"
    assert struct.external_namespace() == "a::b::c"


def test_get_service_by_name() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
"""
    lrpc_def = load_lrpc_def(def_str)

    service = lrpc_def.service_by_name("s1")
    assert service is not None
    assert service.name() == "s1"
    assert lrpc_def.service_by_name("") is None


def test_get_service_by_id() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    id: 21
    functions:
      - name: "f1"
"""
    lrpc_def = load_lrpc_def(def_str)

    service = lrpc_def.service_by_id(21)
    assert service is not None
    assert service.name() == "s1"
    assert lrpc_def.service_by_id(22) is None


def test_get_struct_by_name() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
structs:
  - name: "MyStruct1"
    fields:
      - name: ms1
        type: float
"""
    lrpc_def = load_lrpc_def(def_str)

    s = lrpc_def.struct("MyStruct1")
    assert s.name() == "MyStruct1"

    with pytest.raises(ValueError):
        lrpc_def.struct("")


def test_get_enum_by_name() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
enums:
  - name: "MyEnum1"
    fields:
      - name: ms1
        id: 55
"""
    lrpc_def = load_lrpc_def(def_str)

    e = lrpc_def.enum("MyEnum1")
    assert e.name() == "MyEnum1"

    with pytest.raises(ValueError):
        lrpc_def.enum("")


def test_no_version() -> None:
    def_str = """name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
"""
    lrpc_def = load_lrpc_def(def_str)
    assert lrpc_def.version() is None


def test_version() -> None:
    def_str = """name: "test"
version: 1.2.3
services:
  - name: "s1"
    functions:
      - name: "f1"
"""
    lrpc_def = load_lrpc_def(def_str)
    assert lrpc_def.version() == "1.2.3"


def test_top_level_properties() -> None:
    def_str = """name: "test"
namespace: ns
rx_buffer_size: 123
tx_buffer_size: 456
services:
  - name: "s1"
    functions:
      - name: "f1"
"""
    lrpc_def = load_lrpc_def(def_str)
    assert lrpc_def.namespace() == "ns"
    assert lrpc_def.rx_buffer_size() == 123
    assert lrpc_def.tx_buffer_size() == 456
