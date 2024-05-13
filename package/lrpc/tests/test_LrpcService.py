from lrpc.core import LrpcService

def test_short_notation():
    s = {
        'name': 's0',
        'id': 123,
        'functions': [
            { 'name': 'f0' },
            { 'name': 'f1', 'id': 55 },
            { 'name': 'f2'}
        ]
    }
    service = LrpcService(s)

    assert service.name() == 's0'
    assert service.id() == 123
    assert len(service.functions()) == 3
    assert service.functions()[0].name() == 'f0'
    assert service.functions()[0].id() == 0
    assert service.functions()[1].name() == 'f1'
    assert service.functions()[1].id() == 55
    assert service.functions()[2].name() == 'f2'
    assert service.functions()[2].id() == 56

def test_get_function_by_name():
    s = {
        'name': 's0',
        'functions': [
            { 'name': 'f0' },
            { 'name': 'f1' }
        ]
    }
    service = LrpcService(s)

    assert service.function('') is None
    assert service.function('f0') is not None
    assert service.function('f0').name() == 'f0'
