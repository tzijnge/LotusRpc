from os import path

from lrpc.client import lrpc_decode, lrpc_encode
from lrpc.core import LrpcVar
from lrpc.utils import load_lrpc_def_from_url

definition_file = path.join(path.dirname(path.abspath(__file__)), "test_lrpc_encode_decode.lrpc.yaml")
lrpc_def = load_lrpc_def_from_url(definition_file, warnings_as_errors=False)


def test_encode_decode() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct2"})

    before = {"a": {"b": 123, "a": 4567, "c": True}}
    encoded = lrpc_encode(before, var, lrpc_def)
    after = lrpc_decode(encoded, var, lrpc_def)

    assert before == after
