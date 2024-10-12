from lrpc.core import LrpcService, LrpcServiceDict


def test_short_notation() -> None:
    s = {
        "name": "s0",
        "id": 123,
        "functions": [{"name": "f0"}, {"name": "f1", "id": 55}, {"name": "f2"}],
    }

    # One of the goals of this test is to verify the automatic
    # ID assignment of functions by LrpcService. Although the `id`
    # field is required in LrpcFunDict, it is not required at
    # LrpcService level. Therefore MyPy warning is ignored here
    service = LrpcService(s)  # type: ignore[arg-type]

    assert service.name() == "s0"
    assert service.id() == 123
    assert len(service.functions()) == 3
    assert service.functions()[0].name() == "f0"
    assert service.functions()[0].id() == 0
    assert service.functions()[1].name() == "f1"
    assert service.functions()[1].id() == 55
    assert service.functions()[2].name() == "f2"
    assert service.functions()[2].id() == 56


def test_function_by_name() -> None:
    s: LrpcServiceDict = {"name": "s0", "id": 123, "functions": [{"name": "f0", "id": 40}, {"name": "f1", "id": 41}]}
    service = LrpcService(s)

    assert service.function_by_name("") is None
    f0 = service.function_by_name("f0")
    assert f0 is not None
    assert f0.name() == "f0"


def test_function_by_id() -> None:
    s: LrpcServiceDict = {"name": "s0", "id": 123, "functions": [{"name": "f0", "id": 36}, {"name": "f1", "id": 40}]}
    service = LrpcService(s)

    assert service.function_by_id(55) is None
    f0 = service.function_by_id(36)
    assert f0 is not None
    assert f0.name() == "f0"
