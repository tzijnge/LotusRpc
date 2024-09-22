from lrpc.core import LrpcEnum, LrpcEnumDict


def test_full_notation() -> None:
    e: LrpcEnumDict = {
        "name": "MyEnum1",
        "fields": [
            {"name": "f1", "id": 111},
            {"name": "f2", "id": 222},
        ],
    }

    enum = LrpcEnum(e)

    assert enum.name() == "MyEnum1"
    fields = enum.fields()
    assert len(fields) == 2
    assert fields[0].name() == "f1"
    assert fields[0].id() == 111
    assert fields[1].name() == "f2"
    assert fields[1].id() == 222


def test_short_notation() -> None:
    e: LrpcEnumDict = {"name": "MyEnum2", "fields": ["f1", "f2"]}

    enum = LrpcEnum(e)

    assert enum.name() == "MyEnum2"
    fields = enum.fields()
    assert len(fields) == 2
    assert fields[0].name() == "f1"
    assert fields[0].id() == 0
    assert fields[1].name() == "f2"
    assert fields[1].id() == 1


def test_not_external() -> None:
    e: LrpcEnumDict = {
        "name": "MyEnum2",
        "fields": ["f1", "f2"],
    }

    enum = LrpcEnum(e)
    assert enum.is_external() is False
    assert enum.external_file() is None


def test_external() -> None:
    e: LrpcEnumDict = {"name": "MyEnum2", "fields": ["f1", "f2"], "external": "a/b/c/d.hpp"}

    enum = LrpcEnum(e)
    assert enum.name() == "MyEnum2"
    assert enum.is_external() is True
    assert enum.external_file() == "a/b/c/d.hpp"
    assert enum.external_namespace() is None


def test_external_with_namespace() -> None:
    e: LrpcEnumDict = {
        "name": "MyEnum2",
        "fields": ["f1", "f2"],
        "external": "a/b/c/d.hpp",
        "external_namespace": "ext",
    }

    enum = LrpcEnum(e)
    assert enum.name() == "MyEnum2"
    assert enum.is_external() is True
    assert enum.external_file() == "a/b/c/d.hpp"
    assert enum.external_namespace() == "ext"


def test_omitted_id() -> None:
    # Although field `id` is required for LrpcEnumFieldDict,
    # it may be assigned automatically by LrpcEnum and therefore
    # not required at the level of LrpcEnumDict. This test
    # verifies the auto ID assignment and therefore the type
    # warning is ignored
    e: LrpcEnumDict = {
        "name": "MyEnum1",
        "fields": [
            {"name": "f1"},  # type: ignore[list-item]
            {"name": "f2"},  # type: ignore[list-item]
            {"name": "f3", "id": 222},
            {"name": "f4"},  # type: ignore[list-item]
        ],
    }

    enum = LrpcEnum(e)

    assert enum.name() == "MyEnum1"
    fields = enum.fields()
    assert len(fields) == 4
    assert fields[0].name() == "f1"
    assert fields[0].id() == 0
    assert fields[1].name() == "f2"
    assert fields[1].id() == 1
    assert fields[2].name() == "f3"
    assert fields[2].id() == 222
    assert fields[3].name() == "f4"
    assert fields[3].id() == 223


def test_field_id() -> None:
    e: LrpcEnumDict = {
        "name": "MyEnum1",
        "fields": [
            {"name": "f1", "id": 111},
            {"name": "f2", "id": 222},
        ],
    }

    enum = LrpcEnum(e)

    assert enum.field_id("f1") == 111
    assert enum.field_id("f2") == 222
    assert enum.field_id("f3") is None
