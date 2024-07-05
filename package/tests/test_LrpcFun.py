from lrpc.core import LrpcFun

def test_short_notation():
    f = {'name': 'f1', 'id': 123}

    fun = LrpcFun(f)

    assert fun.name() == 'f1'
    assert len(fun.params()) == 0
    assert len(fun.param_names()) == 0
    assert fun.number_returns() == 0
    assert len(fun.returns()) == 0
    assert fun.id() == 123

def test_full_notation():
    f = {
        'name': 'f1',
        'id': 123,
        'params': [ {'name': 'p1', 'type': 'uint8_t'} ],
        'returns': [ {'name': 'r1', 'type': 'uint8_t'} ]
        }

    fun = LrpcFun(f)

    assert fun.name() == 'f1'
    assert len(fun.params()) == 1
    assert fun.params()[0].name() == 'p1'
    assert len(fun.param_names()) == 1
    assert fun.param_names()[0] == 'p1'
    assert fun.number_returns() == 1
    assert len(fun.returns()) == 1
    assert fun.returns()[0].name() == 'r1'
    assert fun.id() == 123

def test_get_param_by_name():
    f = {
        'name': 'f1',
        'id': 123,
        'params': [ {'name': 'p1', 'type': 'uint8_t'} ],
        'returns': [ {'name': 'r1', 'type': 'uint8_t'} ]
        }

    fun = LrpcFun(f)

    assert fun.param('') is None
    assert fun.param('p1') is not None
    assert fun.param('p1').name() == 'p1'

def test_get_return_by_name():
    f = {
        'name': 'f1',
        'id': 123,
        'params': [ {'name': 'p1', 'type': 'uint8_t'} ],
        'returns': [ {'name': 'r1', 'type': 'uint8_t'} ]
        }

    fun = LrpcFun(f)

    assert fun.ret('') is None
    assert fun.ret('r1') is not None
    assert fun.ret('r1').name() == 'r1'
