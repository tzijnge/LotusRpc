from lrpc.client import LrpcClient
import struct, pytest

client = LrpcClient('test_lrpc_encode_decode.lrpc.yaml')

def test_encode_nested_struct():
    assert client.encode('s0', 'f1', p1={'a': {'a': 4567, 'b': 123, 'c': True}}) == b'\x07\x00\x01\xD7\x11\x7B\x01'

def test_call():
    encoded = client.encode('s1', 'add5', **{'p0': 123})
    # client: send encoded to server

    # server: copy service ID and function ID and append return value
    response = b'\x04' + encoded[1:2] + encoded[2:3] + struct.pack('<B', encoded[3] + 5)

    # client: receive bytes and decode
    received = client.decode(response)
    
    assert 'r0' in received
    assert received['r0'] == 128

def test_encode_invalid_service():
    with pytest.raises(ValueError):
        client.encode('invalid_service', 'f2')

def test_encode_invalid_function():
    with pytest.raises(ValueError):
        client.encode('s1', 'invalid_function')

def test_encode_too_many_parameters():
    with pytest.raises(ValueError):
        # function takes no parameters
        client.encode('s1', 'f2', invalid=123)

def test_encode_missing_parameter():
    with pytest.raises(ValueError):
        # function takes one parameter, but none given
        client.encode('s1', 'add5')

def test_encode_invalid_parameter_name():
    with pytest.raises(ValueError):
        # function takes one parameter, but none given
        client.encode('s1', 'add5', invalid=5)

def test_decode_invalid_service_id():
    with pytest.raises(ValueError):
        encoded = b'\x04\xAA\x00\x02'
        client.decode(encoded)

def test_decode_invalid_function_id():
    with pytest.raises(ValueError):
        encoded = b'\x04\x01\xAA\x02'
        client.decode(encoded)