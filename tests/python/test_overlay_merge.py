import pytest

from lrpc.utils import YamlValues
from lrpc.utils import merge_definition as lrpc_merge_definition


class TestBasicPropertyOperations:
    @staticmethod
    def test_add_basic_property() -> None:
        base: YamlValues = {"name": "test", "value": 1}
        overlay: YamlValues = {"description": "example"}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"name": "test", "value": 1, "description": "example"}

    @staticmethod
    def test_replace_basic_property() -> None:
        base: YamlValues = {"name": "test", "value": 1}
        overlay: YamlValues = {"value": 42}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"name": "test", "value": 42}

    @staticmethod
    def test_remove_basic_property() -> None:
        base: YamlValues = {"name": "test", "value": 1, "description": "old"}
        overlay: YamlValues = {"description": None}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"name": "test", "value": 1}

    @staticmethod
    def test_merge_strategy_on_basic_property() -> None:
        base: YamlValues = {"name": "test"}
        overlay: YamlValues = {"value": 42, "merge_strategy": "add"}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"name": "test", "value": 42}

    @staticmethod
    def test_add_multiple_basic_types() -> None:
        base: YamlValues = {"name": "test"}
        overlay: YamlValues = {"int_val": 1, "float_val": 3.14, "bool_val": True, "str_val": "hello"}

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "name": "test",
            "int_val": 1,
            "float_val": 3.14,
            "bool_val": True,
            "str_val": "hello",
        }


class TestNestedDictOperations:
    @staticmethod
    def test_replace_in_empty_dict() -> None:
        base: YamlValues = {}
        overlay: YamlValues = {"service": {"description": "A service"}}

        result = lrpc_merge_definition(base, overlay, "replace")

        assert result == {
            "service": {"description": "A service"},
        }

    @staticmethod
    def test_add_to_empty_dict() -> None:
        base: YamlValues = {}
        overlay: YamlValues = {"service": {"description": "A service"}}

        result = lrpc_merge_definition(base, overlay, "add")

        assert result == {
            "service": {"description": "A service"},
        }

    @staticmethod
    def test_merge_nested_dicts() -> None:
        base: YamlValues = {"service": {"name": "srv0", "id": 1}}
        overlay: YamlValues = {"service": {"description": "A service"}}

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "service": {"name": "srv0", "id": 1, "description": "A service"},
        }

    @staticmethod
    def test_nested_dict_with_add() -> None:
        base: YamlValues = {
            "config": {"database": {"host": "localhost", "port": 5432}},
        }
        overlay: YamlValues = {
            "config": {
                "database": {"user": "admin"},
                "merge_strategy": "add",
            },
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "config": {"database": {"host": "localhost", "port": 5432, "user": "admin"}},
        }

    @staticmethod
    def test_nested_dict_deep_nesting() -> None:
        base: YamlValues = {
            "service": {
                "name": "srv0",
                "functions": [
                    {
                        "name": "func0",
                        "params": [{"name": "p0", "type": "uint8_t", "value": 1}],
                    },
                ],
            },
        }
        overlay: YamlValues = {
            "service": {
                "functions": [
                    {
                        "name": "func0",
                        "params": [{"name": "p0", "description": "first param"}],
                    },
                ],
            },
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "service": {
                "name": "srv0",
                "functions": [
                    {
                        "name": "func0",
                        "params": [
                            {
                                "name": "p0",
                                "type": "uint8_t",
                                "value": 1,
                                "description": "first param",
                            },
                        ],
                    },
                ],
            },
        }

    @staticmethod
    def test_replace_nested_dict() -> None:
        base: YamlValues = {"config": {"a": 1, "b": 2}}
        overlay: YamlValues = {"config": {"c": 3, "merge_strategy": "replace"}}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"config": {"c": 3}}


class TestListOperations:
    @staticmethod
    def test_list_add_basic_items() -> None:
        base: YamlValues = {"items": [1, 2]}
        overlay: YamlValues = {"items": [3], "merge_strategy": "add"}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"items": [1, 2, 3]}

    @staticmethod
    def test_list_add_composite_items() -> None:
        base: YamlValues = {"items": [{"id": 1}, {"id": 2}]}
        overlay: YamlValues = {"items": [{"id": 3}], "merge_strategy": "add"}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"items": [{"id": 1}, {"id": 2}, {"id": 3}]}

    @staticmethod
    def test_list_add_composite_merge_existing_by_name() -> None:
        base: YamlValues = {
            "functions": [
                {"name": "func0", "type": "void", "params": []},
                {"name": "func1", "type": "int", "params": []},
            ],
        }
        overlay: YamlValues = {
            "functions": [{"name": "func0", "description": "First function"}],
            "merge_strategy": "add",
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "functions": [
                {
                    "name": "func0",
                    "type": "void",
                    "params": [],
                    "description": "First function",
                },
                {
                    "name": "func1",
                    "type": "int",
                    "params": [],
                },
            ],
        }

    @staticmethod
    def test_list_remove_composite_by_name() -> None:
        base: YamlValues = {
            "functions": [
                {"name": "func0", "type": "void"},
                {"name": "func1", "type": "int"},
                {"name": "func2", "type": "bool"},
            ],
        }
        overlay: YamlValues = {
            "functions": [{"name": "func1", "merge_strategy": "remove"}],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "functions": [
                {"name": "func0", "type": "void"},
                {"name": "func2", "type": "bool"},
            ],
        }

    @staticmethod
    def test_list_remove_multiple_by_name() -> None:
        base: YamlValues = {
            "functions": [
                {"name": "func0"},
                {"name": "func1"},
                {"name": "func2"},
            ],
        }
        overlay: YamlValues = {
            "functions": [
                {"name": "func0", "merge_strategy": "remove"},
                {"name": "func2", "merge_strategy": "remove"},
            ],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {"functions": [{"name": "func1"}]}

    @staticmethod
    def test_list_replace_all() -> None:
        base: YamlValues = {
            "functions": [
                {"name": "func0"},
                {"name": "func1"},
            ],
        }
        overlay: YamlValues = {
            "functions": [{"name": "func_new"}],
            "merge_strategy": "replace",
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {"functions": [{"name": "func_new"}]}

    @staticmethod
    def test_list_with_merge_strategy_on_list_property() -> None:
        base: YamlValues = {
            "data": {
                "items": [1, 2],
                "metadata": "original",
            },
        }
        overlay: YamlValues = {
            "data": {
                "items": [3],
                "merge_strategy": "add",
            },
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "data": {
                "items": [1, 2, 3],
                "metadata": "original",
            },
        }

    @staticmethod
    def test_list_with_merge_strategy_on_item() -> None:
        base: YamlValues = {
            "params": [
                {"name": "p0", "type": "int", "description": "original"},
            ],
        }
        overlay: YamlValues = {
            "params": [
                {
                    "name": "p0",
                    "extra": "field",
                    "merge_strategy": "add",
                },
            ],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "params": [
                {
                    "name": "p0",
                    "type": "int",
                    "description": "original",
                    "extra": "field",
                },
            ],
        }

    @staticmethod
    def test_list_items_without_name() -> None:
        base: YamlValues = {
            "values": [
                {"id": 1, "data": "a"},
                {"id": 2, "data": "b"},
            ],
        }
        overlay: YamlValues = {
            # No "name" property
            "values": [{"data": "c"}],
            "merge_strategy": "add",
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "values": [
                {"id": 1, "data": "a"},
                {"id": 2, "data": "b"},
                {"data": "c"},
            ],
        }


class TestIntegrationRealisticStructures:
    @staticmethod
    def test_add_function_to_service() -> None:
        base: YamlValues = {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {"name": "func0", "params": [], "returns": []},
                    ],
                },
            ],
        }
        overlay: YamlValues = {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {"name": "func1", "params": [], "returns": []},
                    ],
                },
            ],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {"name": "func0", "params": [], "returns": []},
                        {"name": "func1", "params": [], "returns": []},
                    ],
                },
            ],
        }

    @staticmethod
    def test_remove_parameter_from_function() -> None:
        base: YamlValues = {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {
                            "name": "func0",
                            "params": [
                                {"name": "p0", "type": "uint8_t"},
                                {"name": "p1", "type": "float"},
                            ],
                        },
                    ],
                },
            ],
        }
        overlay: YamlValues = {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {
                            "name": "func0",
                            "params": [{"name": "p1", "merge_strategy": "remove"}],
                        },
                    ],
                },
            ],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {
                            "name": "func0",
                            "params": [{"name": "p0", "type": "uint8_t"}],
                        },
                    ],
                },
            ],
        }

    @staticmethod
    def test_replace_function_type() -> None:
        base: YamlValues = {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {
                            "name": "func0",
                            "returns": [{"name": "r0", "type": "uint8_t"}],
                        },
                    ],
                },
            ],
        }
        overlay: YamlValues = {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {
                            "name": "func0",
                            "returns": [{"name": "r0", "type": "uint32_t"}],
                        },
                    ],
                },
            ],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "services": [
                {
                    "name": "MyService",
                    "functions": [
                        {
                            "name": "func0",
                            "returns": [{"name": "r0", "type": "uint32_t"}],
                        },
                    ],
                },
            ],
        }

    @staticmethod
    def test_complex_multi_level_merge() -> None:
        base: YamlValues = {
            "services": [
                {
                    "name": "Service1",
                    "functions": [
                        {
                            "name": "func1",
                            "id": 1,
                            "params": [
                                {"name": "p1", "type": "int"},
                                {"name": "p2", "type": "char"},
                            ],
                            "returns": [{"name": "r1", "type": "int"}],
                        },
                        {
                            "name": "func2",
                            "id": 2,
                            "params": [],
                            "returns": [],
                        },
                    ],
                },
            ],
            "enums": [{"name": "Colors", "fields": [{"name": "RED"}]}],
        }

        overlay: YamlValues = {
            "services": [
                {
                    "name": "Service1",
                    "functions": [
                        {
                            "name": "func1",
                            "params": [
                                # Add new param
                                {"name": "p3", "type": "bool"},
                                # Remove p2
                                {"name": "p2", "merge_strategy": "remove"},
                            ],
                            "merge_strategy": "add",
                        },
                        {
                            # Add new function
                            "name": "func3",
                            "id": 3,
                            "params": [],
                            "returns": [],
                        },
                    ],
                    "merge_strategy": "add",
                },
            ],
            "enums": [
                {
                    "name": "Colors",
                    "fields": [{"name": "GREEN"}],
                    "merge_strategy": "add",
                },
            ],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "services": [
                {
                    "name": "Service1",
                    "functions": [
                        {
                            "name": "func1",
                            "id": 1,
                            "params": [
                                {"name": "p1", "type": "int"},
                                {"name": "p3", "type": "bool"},
                            ],
                            "returns": [{"name": "r1", "type": "int"}],
                        },
                        {
                            "name": "func2",
                            "id": 2,
                            "params": [],
                            "returns": [],
                        },
                        {
                            "name": "func3",
                            "id": 3,
                            "params": [],
                            "returns": [],
                        },
                    ],
                },
            ],
            "enums": [
                {
                    "name": "Colors",
                    "fields": [
                        {"name": "RED"},
                        {"name": "GREEN"},
                    ],
                },
            ],
        }


class TestEdgeCases:
    @staticmethod
    def test_error_base_not_dict() -> None:
        with pytest.raises(TypeError, match="base must be a dict"):
            lrpc_merge_definition([], {})

    @staticmethod
    def test_error_overlay_not_dict() -> None:
        with pytest.raises(TypeError, match="overlay must be a dict"):
            lrpc_merge_definition({}, [])

    @staticmethod
    def test_empty_lists() -> None:
        base: dict[str, YamlValues] = {"items": []}
        overlay: YamlValues = {"items": [1, 2], "merge_strategy": "add"}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"items": [1, 2]}

    @staticmethod
    def test_empty_list_base_replace() -> None:
        base: dict[str, YamlValues] = {"items": []}
        overlay: YamlValues = {"items": [1, 2], "merge_strategy": "replace"}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"items": [1, 2]}

    @staticmethod
    def test_overlay_with_merge_strategy_remove() -> None:
        base: YamlValues = {
            "functions": [
                {"name": "func0", "deprecated": True},
                {"name": "func1"},
            ],
        }
        overlay: YamlValues = {"functions": [{"name": "func0", "merge_strategy": "remove"}]}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"functions": [{"name": "func1"}]}

    @staticmethod
    def test_null_stripping() -> None:
        base: YamlValues = {"a": 1, "b": 2, "c": 3}
        overlay: YamlValues = {"a": None, "b": None}

        result = lrpc_merge_definition(base, overlay)

        assert result == {"c": 3}

    @staticmethod
    def test_null_stripping_nested() -> None:
        base: YamlValues = {
            "service": {
                "name": "srv0",
                "config": {"debug": True, "verbose": False},
            },
        }
        overlay: YamlValues = {
            "service": {
                "config": {"debug": None},
            },
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "service": {
                "name": "srv0",
                "config": {"verbose": False},
            },
        }

    @staticmethod
    def test_null_stripping_in_lists() -> None:
        base: YamlValues = {"params": [{"name": "p0", "deprecated": None}]}
        overlay: dict[str, YamlValues] = {}

        result = lrpc_merge_definition(base, overlay)

        # Base unchanged, merge result should strip nulls
        assert result == {"params": [{"name": "p0"}]}

    @staticmethod
    def test_remove_operation_missing_item_silent_ignore() -> None:
        base: YamlValues = {"items": [1, 2, 3]}
        overlay: YamlValues = {"items": [5, 6], "merge_strategy": "remove"}

        # For basic items (int, str, etc.), remove operation tries exact match removal
        # and silently ignores items not in base
        result = lrpc_merge_definition(base, overlay)

        # Items 5 and 6 not in base, so nothing removed
        assert result == {"items": [1, 2, 3]}

    @staticmethod
    def test_remove_operation_missing_named_item_silent_ignore() -> None:
        base: YamlValues = {"functions": [{"name": "func0"}]}
        overlay: YamlValues = {
            "functions": [{"name": "nonexistent", "merge_strategy": "remove"}],
        }

        result = lrpc_merge_definition(base, overlay)

        # Remove operation silently ignores non-existent items
        assert result == {"functions": [{"name": "func0"}]}

    @staticmethod
    def test_deeply_nested_null_stripping() -> None:
        base: YamlValues = {
            "services": [
                {
                    "name": "srv0",
                    "functions": [
                        {
                            "name": "func0",
                            "params": [
                                {"name": "p0", "old_field": "value"},
                            ],
                        },
                    ],
                },
            ],
        }
        overlay: YamlValues = {
            "services": [
                {
                    "name": "srv0",
                    "functions": [
                        {
                            "name": "func0",
                            "params": [
                                {"name": "p0", "old_field": None},
                            ],
                        },
                    ],
                },
            ],
        }

        result = lrpc_merge_definition(base, overlay)

        assert result == {
            "services": [
                {
                    "name": "srv0",
                    "functions": [
                        {
                            "name": "func0",
                            "params": [{"name": "p0"}],
                        },
                    ],
                },
            ],
        }

    @staticmethod
    def test_immutability_base_unchanged() -> None:
        base: YamlValues = {"a": 1, "b": 2}
        overlay: YamlValues = {"b": 3, "c": 4}

        result = lrpc_merge_definition(base, overlay)

        # Base should be unchanged
        assert base == {"a": 1, "b": 2}
        # Result is new
        assert result == {"a": 1, "b": 3, "c": 4}
        assert result is not base

    @staticmethod
    def test_immutability_overlay_unchanged() -> None:
        base: YamlValues = {"a": 1}
        overlay: YamlValues = {"b": 2, "merge_strategy": "add"}

        result = lrpc_merge_definition(base, overlay)

        # Overlay should be unchanged (dict copy prevents modification)
        assert overlay == {"b": 2, "merge_strategy": "add"}
        # Result shouldn't have merge_strategy
        assert result == {"a": 1, "b": 2}

    @staticmethod
    def test_default_operation_inherited() -> None:
        base: YamlValues = {
            "data": {
                "items": [1, 2],
            },
        }
        overlay: YamlValues = {
            "data": {
                "items": [3],
            },
        }

        result = lrpc_merge_definition(base, overlay, strategy="add")

        assert result == {"data": {"items": [1, 2, 3]}}

    @staticmethod
    def test_list_merge_on_none_base_type_mismatch() -> None:
        base: YamlValues = {"items": "not a list"}
        overlay: YamlValues = {"items": [1, 2], "merge_strategy": "add"}

        result = lrpc_merge_definition(base, overlay)

        # Type mismatch: overlay list replaces the base string value
        assert result == {"items": [1, 2]}
