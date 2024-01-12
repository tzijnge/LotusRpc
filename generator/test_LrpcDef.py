from LrpcDef import LrpcDef
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

def test_no_constants():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
'''
    lrpc_def = LrpcDef(yaml.safe_load(rpc_def))
    assert(len(lrpc_def.constants()) == 0)

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
