from lrpc.core import LrpcVar, LrpcDef
from lrpc.client import lrpc_encode, lrpc_decode
from os import path

definition_file = path.join(path.dirname(path.abspath(__file__)), "test_lrpc_encode_decode.lrpc.yaml")
lrpc_def = LrpcDef.load(definition_file)


def test_encode_decode() -> None:
    var = LrpcVar({"name": "v1", "type": "@MyStruct2", "base_type_is_struct": True})

    before = {"a": {"b": 123, "a": 4567, "c": True}}
    encoded = lrpc_encode(before, var, lrpc_def)
    after = lrpc_decode(encoded, var, lrpc_def)

    assert before == after
