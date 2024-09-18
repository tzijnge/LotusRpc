from lrpc.core import LrpcVar

def test_construct_basic():
    v = { 'name': 'v1', 'type': 'uint8_t' }
    var = LrpcVar(v)

    assert var.name() == 'v1'
    assert var.base_type() == 'uint8_t'
    assert var.base_type_is_integral() == True


def test_base_type_is_bool():
    v = { 'name': 'v1', 'type': 'bool' }
    var = LrpcVar(v)

    assert var.base_type() == 'bool'
    assert var.base_type_is_bool() == True

def test_base_type_is_float():
    v1 = { 'name': 'v1', 'type': 'float' }
    v2 = { 'name': 'v2', 'type': 'double' }
    
    var = LrpcVar(v1)
    assert var.base_type() == 'float'
    assert var.base_type_is_float() == True

    var = LrpcVar(v2)
    assert var.base_type() == 'double'
    assert var.base_type_is_float() == True

def test_base_type_is_string():
    v1 = { 'name': 'v1', 'type': 'string' }
    v2 = { 'name': 'v2', 'type': 'string_10', 'count': 3 }
    
    var = LrpcVar(v1)
    assert var.base_type() == 'string'
    assert var.base_type_is_string() == True
    assert var.is_array_of_strings() == False

    var = LrpcVar(v2)
    assert var.base_type() == 'string_10'
    assert var.base_type_is_string() == True
    assert var.is_array_of_strings() == True
