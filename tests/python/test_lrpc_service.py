import pytest
from lrpc.core import LrpcService, LrpcServiceDict
from .utilities import StringifyVisitor


def test_short_notation() -> None:
    s = {
        "name": "s0",
        "id": 123,
        "functions": [{"name": "f0"}, {"name": "f1", "id": 55}, {"name": "f2"}],
        "functions_before_streams": True,
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
    s: LrpcServiceDict = {
        "name": "s0",
        "id": 123,
        "functions": [{"name": "f0", "id": 40}, {"name": "f1", "id": 41}],
        "functions_before_streams": True,
    }
    service = LrpcService(s)

    assert service.function_by_name("") is None
    f0 = service.function_by_name("f0")
    assert f0 is not None
    assert f0.name() == "f0"


def test_function_by_id() -> None:
    s: LrpcServiceDict = {
        "name": "s0",
        "id": 123,
        "functions": [{"name": "f0", "id": 36}, {"name": "f1", "id": 40}],
        "functions_before_streams": True,
    }
    service = LrpcService(s)

    assert service.function_by_id(55) is None
    f0 = service.function_by_id(36)
    assert f0 is not None
    assert f0.name() == "f0"

    f1 = service.function_by_id(40)
    assert f1 is not None
    assert f1.name() == "f1"


def test_stream_by_id() -> None:
    s: LrpcServiceDict = {
        "name": "s0",
        "id": 123,
        "streams": [
            {"name": "s0", "id": 36, "origin": "server"},
            {"name": "s1", "id": 40, "origin": "client"},
        ],
        "functions_before_streams": True,
    }
    service = LrpcService(s)

    assert service.stream_by_id(55) is None
    s0 = service.stream_by_id(36)
    assert s0 is not None
    assert s0.name() == "s0"

    s1 = service.stream_by_id(40)
    assert s1 is not None
    assert s1.name() == "s1"


def test_only_streams() -> None:
    s: LrpcServiceDict = {
        "name": "srv0",
        "id": 123,
        "streams": [{"name": "s0", "id": 36, "origin": "client"}, {"name": "s1", "id": 40, "origin": "server"}],
        "functions_before_streams": False,
    }
    service = LrpcService(s)

    streams = service.streams()
    assert len(streams) == 2
    assert streams[0].name() == "s0"
    assert streams[0].id() == 36
    assert streams[1].name() == "s1"
    assert streams[1].id() == 40


def test_functions_and_streams() -> None:
    s: LrpcServiceDict = {
        "name": "srv0",
        "id": 123,
        "functions": [{"name": "f0", "id": 36}, {"name": "f1", "id": 40}],
        "streams": [{"name": "s0", "id": 36, "origin": "client"}, {"name": "s1", "id": 40, "origin": "server"}],
        "functions_before_streams": True,
    }
    service = LrpcService(s)

    functions = service.functions()
    assert len(functions) == 2
    assert functions[0].name() == "f0"
    assert functions[0].id() == 36
    assert functions[1].name() == "f1"
    assert functions[1].id() == 40

    streams = service.streams()
    assert len(streams) == 2
    assert streams[0].name() == "s0"
    assert streams[0].id() == 36
    assert streams[1].name() == "s1"
    assert streams[1].id() == 40


def test_fail_when_neither_functions_nor_streams() -> None:
    s: LrpcServiceDict = {"name": "srv0", "id": 123, "functions_before_streams": True}

    with pytest.raises(AssertionError):
        LrpcService(s)


def test_visit_stream() -> None:
    v = StringifyVisitor()

    s: LrpcServiceDict = {
        "name": "srv0",
        "id": 123,
        "functions": [{"name": "f0", "id": 36}, {"name": "f1", "id": 40}],
        "streams": [{"name": "s0", "id": 36, "origin": "client"}, {"name": "s1", "id": 40, "origin": "server"}],
        "functions_before_streams": True,
    }
    service = LrpcService(s)

    service.accept(v)

    functions = "function[f0+36]-return_end-param_end-function_end-function[f1+40]-return_end-param_end-function_end"
    streams = "stream[s0+36+client]-param_end-return_end-stream_end-stream[s1+40+server]-param[start]-param_end-return_end-stream_end"

    assert v.result == f"service[srv0]-{functions}-{streams}-service_end"


def test_stream_by_name() -> None:
    s: LrpcServiceDict = {
        "name": "srv0",
        "id": 123,
        "streams": [{"name": "s0", "id": 36, "origin": "client"}, {"name": "s1", "id": 40, "origin": "server"}],
        "functions_before_streams": True,
    }
    service = LrpcService(s)

    s0 = service.stream_by_name("s0")
    assert s0 is not None and s0.name() == "s0"
    s1 = service.stream_by_name("s1")
    assert s1 is not None and s1.name() == "s1"
    assert service.stream_by_name("s2") is None
