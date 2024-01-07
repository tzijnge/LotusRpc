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