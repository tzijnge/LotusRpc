from lrpc.client import lrpc_decode, lrpc_encode
from lrpc.core import LrpcVar

from .utilities import load_test_definition

lrpc_def = load_test_definition("test_lrpc_encode_decode.lrpc.yaml")


def test_encode_decode() -> None:
    var = LrpcVar({"name": "v1", "type": "struct@MyStruct2"})

    before = {"f0": {"f1": 123, "f0": 4567, "f2": True}}
    encoded = lrpc_encode(before, var, lrpc_def)
    after = lrpc_decode(encoded, var, lrpc_def)

    assert before == after
