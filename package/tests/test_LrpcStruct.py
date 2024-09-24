from lrpc.core import LrpcStruct, LrpcStructDict


def test_minimal_notation() -> None:
    s: LrpcStructDict = {
        "name": "MyStruct",
        "fields": [
            {"name": "f1", "type": "uint64_t"},
            {"name": "f2", "type": "bool"},
            {"name": "f3", "type": "struct@MyStruct"},
            {"name": "f4", "type": "enum@MyEnum"},
        ],
    }

    struct = LrpcStruct(s)

    assert struct.name() == "MyStruct"
    assert struct.is_external() is False
    assert struct.external_file() is None
    assert struct.external_namespace() is None

    fields = struct.fields()
    assert len(fields) == 4
    assert fields[0].name() == "f1"
    assert fields[0].base_type() == "uint64_t"

    assert fields[1].name() == "f2"
    assert fields[1].base_type() == "bool"
    assert fields[1].base_type_is_custom() is False
    assert fields[1].base_type_is_struct() is False
    assert fields[1].base_type_is_enum() is False

    assert fields[2].name() == "f3"
    assert fields[2].base_type() == "MyStruct"
    assert fields[2].base_type_is_custom() is True
    assert fields[2].base_type_is_struct() is True
    assert fields[2].base_type_is_enum() is False

    assert fields[3].name() == "f4"
    assert fields[3].base_type() == "MyEnum"
    assert fields[3].base_type_is_custom() is True
    assert fields[3].base_type_is_struct() is False
    assert fields[3].base_type_is_enum() is True


def test_external() -> None:
    s: LrpcStructDict = {
        "name": "MyStruct",
        "fields": [{"name": "f1", "type": "uint64_t"}],
        "external": "path/to/enum.hpp",
    }

    struct = LrpcStruct(s)

    assert struct.name() == "MyStruct"
    assert struct.is_external() is True
    assert struct.external_file() == "path/to/enum.hpp"
    assert struct.external_namespace() is None


def test_external_with_namespace() -> None:
    s: LrpcStructDict = {
        "name": "MyStruct",
        "fields": [{"name": "f1", "type": "uint64_t"}],
        "external": "path/to/enum.hpp",
        "external_namespace": "path::to",
    }

    struct = LrpcStruct(s)

    assert struct.name() == "MyStruct"
    assert struct.is_external() is True
    assert struct.external_file() == "path/to/enum.hpp"
    assert struct.external_namespace() == "path::to"
