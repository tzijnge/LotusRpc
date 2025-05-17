import pytest
from lrpc.core import LrpcService, LrpcServiceDict, LrpcVar, LrpcFun, LrpcStream
from lrpc.visitors import LrpcVisitor


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


def test_only_streams() -> None:
    s: LrpcServiceDict = {
        "name": "srv0",
        "id": 123,
        "streams": [{"name": "s0", "id": 36, "origin": "client"}, {"name": "s1", "id": 40, "origin": "server"}],
    }
    service = LrpcService(s)

    streams = service.streams()
    assert len(streams) == 2
    assert streams[0].name() == "s0"
    assert streams[1].name() == "s1"


def test_functions_and_streams() -> None:
    s: LrpcServiceDict = {
        "name": "srv0",
        "id": 123,
        "functions": [{"name": "f0", "id": 36}, {"name": "f1", "id": 40}],
        "streams": [{"name": "s0", "id": 36, "origin": "client"}, {"name": "s1", "id": 40, "origin": "server"}],
    }
    service = LrpcService(s)

    functions = service.functions()
    assert len(functions) == 2
    assert functions[0].name() == "f0"
    assert functions[1].name() == "f1"

    streams = service.streams()
    assert len(streams) == 2
    assert streams[0].name() == "s0"
    assert streams[1].name() == "s1"


def test_fail_when_neither_functions_not_streams() -> None:
    s: LrpcServiceDict = {"name": "srv0", "id": 123}

    with pytest.raises(AssertionError):
        LrpcService(s)


class TestVisitor(LrpcVisitor):
    def __init__(self) -> None:
        self.result: str = ""

    def _insert_separator(self) -> None:
        if len(self.result) != 0:
            self.result += "-"

    def visit_lrpc_service(self, service: "LrpcService") -> None:
        self._insert_separator()
        self.result += f"service[{service.name()}]"

    def visit_lrpc_service_end(self) -> None:
        self._insert_separator()
        self.result += "service_end"

    def visit_lrpc_stream(self, stream: LrpcStream, origin: LrpcStream.Origin) -> None:
        self._insert_separator()
        self.result += f"stream[{stream.name()}+{stream.id()}+{origin.value}]"

    def visit_lrpc_stream_param(self, param: LrpcVar) -> None:
        self._insert_separator()
        self.result += f"param[{param.name()}]"

    def visit_lrpc_stream_param_end(self) -> None:
        self._insert_separator()
        self.result += "param_end"

    def visit_lrpc_stream_end(self) -> None:
        self._insert_separator()
        self.result += "stream_end"

    def visit_lrpc_function(self, function: LrpcFun) -> None:
        self._insert_separator()
        self.result += f"function[{function.name()}+{function.id()}]"

    def visit_lrpc_function_end(self) -> None:
        self._insert_separator()
        self.result += "function_end"

    def visit_lrpc_function_return(self, ret: LrpcVar) -> None:
        self._insert_separator()
        self.result += f"return[{ret.name()}]"

    def visit_lrpc_function_return_end(self) -> None:
        self._insert_separator()
        self.result += "return_end"

    def visit_lrpc_function_param(self, param: LrpcVar) -> None:
        self._insert_separator()
        self.result += f"param[{param.name()}]"

    def visit_lrpc_function_param_end(self) -> None:
        self._insert_separator()
        self.result += "param_end"


def test_visit_stream() -> None:
    tv = TestVisitor()

    s: LrpcServiceDict = {
        "name": "srv0",
        "id": 123,
        "functions": [{"name": "f0", "id": 36}, {"name": "f1", "id": 40}],
        "streams": [{"name": "s0", "id": 36, "origin": "client"}, {"name": "s1", "id": 40, "origin": "server"}],
    }
    service = LrpcService(s)

    service.accept(tv)

    functions = "function[f0+36]-return_end-param_end-function_end-function[f1+40]-return_end-param_end-function_end"
    streams = "stream[s0+36+client]-param_end-stream_end-stream[s1+40+server]-param_end-stream_end"

    assert tv.result == f"service[srv0]-{functions}-{streams}-service_end"
