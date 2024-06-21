from lrpc.client import LrpcClient
from lrpc.core import LrpcDef
import yaml

def test_call_void():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
      - name: "f2"
  - name: "s2"
    id: 123
    functions:
      - name: "f1"
        id: 111
      - name: "f2"
        id: 222
'''
    client = LrpcClient(LrpcDef(yaml.safe_load(rpc_def)))

    assert client.call('s1', 'f1') == b'\x00\x00'
    assert client.call('s1', 'f2') == b'\x00\x01'
    assert client.call('s2', 'f1') == b'\x7B\x6F'
    assert client.call('s2', 'f2') == b'\x7B\xDE'

def test_call_uint8():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
        params:
          - name: p1
            type: uint8_t
'''
    client = LrpcClient(LrpcDef(yaml.safe_load(rpc_def)))

    assert client.call('s1', 'f1', p1=0xAB) == b'\x00\x00\xAB'

def test_call_uint16():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
        params:
          - name: p1
            type: uint16_t
'''
    client = LrpcClient(LrpcDef(yaml.safe_load(rpc_def)))

    assert client.call('s1', 'f1', p1=0xABCD) == b'\x00\x00\xCD\xAB'

def test_call_uint32():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
        params:
          - name: p1
            type: uint32_t
'''
    client = LrpcClient(LrpcDef(yaml.safe_load(rpc_def)))

    assert client.call('s1', 'f1', p1=0xABCD1234) == b'\x00\x00\x34\x12\xCD\xAB'

def test_call_uint64():
    rpc_def = \
'''name: "test"
services:
  - name: "s1"
    functions:
      - name: "f1"
        params:
          - name: p1
            type: uint64_t
'''
    client = LrpcClient(LrpcDef(yaml.safe_load(rpc_def)))

    assert client.call('s1', 'f1', p1=0xABCD1234ABCD1234) == b'\x00\x00\x34\x12\xCD\xAB\x34\x12\xCD\xAB'

def test_call_nested_struct():
    lrpc_def = LrpcDef.load('package/lrpc/tests/test_lrpc_encode_decode.lrpc.yaml')
    client = LrpcClient(lrpc_def)

    assert client.call('s0', 'f1', p1={'a': {'a': 4567, 'b': 123, 'c': True}}) == b'\x00\x01\xD7\x11\x7B\x01'