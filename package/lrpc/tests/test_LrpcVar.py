from lrpc.core import LrpcVar

def test_construct_basic():
    v = { 'name': 'v1', 'type': 'uint8_t' }
    var = LrpcVar(v)

    assert var.name() == "v1"
    assert var.base_type() == "uint8_t"
