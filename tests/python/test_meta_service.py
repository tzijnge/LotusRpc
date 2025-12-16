from lrpc.core import LrpcDef
from lrpc.utils import load_lrpc_def_from_str


def load_meta_def() -> LrpcDef:
    def_str = """name: test
services:
  - name: "srv0"
    functions:
      - name: "f0"
"""

    return load_lrpc_def_from_str(def_str, warnings_as_errors=False)


def test_meta_service_properties() -> None:
    lrpc_def = load_meta_def()
    services = lrpc_def.services()
    assert len(services) == 1
    assert services[0].id() == 0
    assert services[0].name() == "srv0"

    meta_service = lrpc_def.meta_service()
    assert meta_service.id() == 255
    assert meta_service.name() == "LrpcMeta"

    meta_streams = meta_service.streams()
    assert len(meta_streams) == 1
    assert meta_streams[0].id() == 0
    assert meta_streams[0].name() == "error"

    meta_functions = meta_service.functions()
    assert len(meta_functions) == 1
    assert meta_functions[0].id() == 1
    assert meta_functions[0].name() == "version"
