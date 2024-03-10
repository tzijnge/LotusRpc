from lrpc.core.LrpcDef import LrpcDef
import yaml

def test_optional_service_id():
    rpc_def = \
'''name: "test"
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
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    services = lrpc_def.services()
    assert(len(services) == 4)
    assert(services[0].id() == 0)
    assert(services[1].id() == 1)
    assert(services[2].id() == 17)
    assert(services[3].id() == 18)

def test_optional_function_id():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "a4"
      - name: "a3"
      - name: "a2"
        id: 17
      - name: "a1"
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    services = lrpc_def.services()
    assert(len(services) == 1)
    functions = services[0].functions()
    assert(len(functions) == 4)

    assert(functions[0].id() == 0)
    assert(functions[1].id() == 1)
    assert(functions[2].id() == 17)
    assert(functions[3].id() == 18)
    
def test_max_service_id():
    rpc_def = \
'''name: "test"
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
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    assert(lrpc_def.max_service_id() == 43)

def test_no_constants_no_enums_no_structs():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    assert(len(lrpc_def.constants()) == 0)
    assert(len(lrpc_def.enums()) == 0)
    assert(len(lrpc_def.structs()) == 0)

def test_constants():
    rpc_def = \
'''name: "test"
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
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    constants = lrpc_def.constants()
    assert(len(constants) == 6)

    c1 = constants[0]
    assert(c1.name() == "c1")
    assert(c1.value() == True)
    assert(c1.cpp_type() == "bool")

    c2 = constants[1]
    assert(c2.name() == "c2")
    assert(c2.value() == 123)
    assert(c2.cpp_type() == "int32_t")

    c3 = constants[2]
    assert(c3.name() == "c3")
    assert(c3.value() == 123.456)
    assert(c3.cpp_type() == "float")

    c4 = constants[3]
    assert(c4.name() == "c4")
    assert(c4.value() == 123.456)
    assert(c4.cpp_type() == "double")

    c5 = constants[4]
    assert(c5.name() == "c5")
    assert(c5.value() == 123)
    assert(c5.cpp_type() == "uint64_t")

    c6 = constants[5]
    assert(c6.name() == "c6")
    assert(c6.value() == "This is a string")
    assert(c6.cpp_type() == "string")

def test_enums():
    rpc_def = \
'''name: "test"
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
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    enums = lrpc_def.enums()
    assert(len(enums) == 2)

    assert(enums[0].name() == "MyEnum1")
    fields = enums[0].fields()
    assert(len(fields) == 2)
    assert(fields[0].name() == "f1")
    assert(fields[0].id() == 111)
    assert(fields[1].name() == "f2")
    assert(fields[1].id() == 222)

    assert(enums[1].name() == "MyEnum2")
    fields = enums[1].fields()
    assert(len(fields) == 2)
    assert(fields[0].name() == "f1")
    assert(fields[0].id() == 0)
    assert(fields[1].name() == "f2")
    assert(fields[1].id() == 1)

def test_external_enum():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
enums:
  - name: "MyEnum1"
    fields: [f1, f2]
    external: a/b/c/d.hpp
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    enum = lrpc_def.enums()[0]

    assert(enum.is_external() == True)
    assert(enum.external_file() == "a/b/c/d.hpp")

def test_enum_with_omitted_ids():
    rpc_def = \
'''name: "test"
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
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    enums = lrpc_def.enums()
    assert(len(enums) == 1)

    assert(enums[0].name() == "MyEnum1")
    fields = enums[0].fields()
    assert(len(fields) == 4)
    assert(fields[0].name() == "f1")
    assert(fields[0].id() == 0)
    assert(fields[1].name() == "f2")
    assert(fields[1].id() == 1)
    assert(fields[2].name() == "f3")
    assert(fields[2].id() == 222)
    assert(fields[3].name() == "f4")
    assert(fields[3].id() == 223)

def test_structs():
    rpc_def = \
'''name: "test"
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
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    structs = lrpc_def.structs()
    assert(len(structs) == 2)

    assert(structs[0].name() == "MyStruct1")
    fields = structs[0].fields()
    assert(len(fields) == 2)
    assert(fields[0].name() == "f1")
    assert(fields[0].base_type() == "double")
    assert(fields[1].name() == "f2")
    assert(fields[1].base_type() == "int8_t")

    assert(structs[1].name() == "MyStruct2")
    fields = structs[1].fields()
    assert(len(fields) == 1)
    assert(fields[0].name() == "ms1")
    assert(fields[0].base_type() == "float")

def test_external_struct():
    rpc_def = \
'''name: "test"
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
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    struct = lrpc_def.structs()[0]

    assert(struct.is_external() == True)
    assert(struct.external_file() == "a/b/c/d.hpp")
    assert(struct.external_namespace() == "a::b::c")
