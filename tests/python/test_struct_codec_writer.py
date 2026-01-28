from io import StringIO

from code_generation.code_generator import CppFile  # type: ignore[import-untyped]

from lrpc.codegen.struct_codec_writer import StructCodecWriter
from lrpc.core import LrpcStruct, LrpcStructDict


def assert_encoder(struct: LrpcStructDict, expected: str, namespace: str | None = None) -> None:
    mock_file = StringIO()
    writer = StructCodecWriter(CppFile("test", mock_file), LrpcStruct(struct), namespace)
    writer.write_encoder()

    assert mock_file.getvalue() == expected


def assert_decoder(struct: LrpcStructDict, expected: str, namespace: str | None = None) -> None:
    mock_file = StringIO()
    writer = StructCodecWriter(CppFile("test", mock_file), LrpcStruct(struct), namespace)
    writer.write_decoder()

    assert mock_file.getvalue() == expected


def test_encoder_single_field_intrinsic() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "uint8_t"},
        ],
    }
    expected = """template<>
inline void write_unchecked<test_struct>(etl::byte_stream_writer& writer, const test_struct& obj)
{
\tlrpc::write_unchecked<uint8_t>(writer, obj.f1);
}
"""

    assert_encoder(func, expected)


def test_encoder_single_field_auto_string() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "string"},
        ],
    }
    expected = """template<>
inline void write_unchecked<test_struct>(etl::byte_stream_writer& writer, const test_struct& obj)
{
\tlrpc::write_unchecked<lrpc::tags::string_auto>(writer, obj.f1);
}
"""

    assert_encoder(func, expected)


def test_encoder_single_field_fixed_size_string() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "string_2"},
        ],
    }
    expected = """template<>
inline void write_unchecked<test_struct>(etl::byte_stream_writer& writer, const test_struct& obj)
{
\tlrpc::write_unchecked<lrpc::tags::string_n>(writer, obj.f1, 2);
}
"""

    assert_encoder(func, expected)


def test_encoder_single_field_array() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "uint8_t", "count": 2},
        ],
    }
    expected = """template<>
inline void write_unchecked<test_struct>(etl::byte_stream_writer& writer, const test_struct& obj)
{
\tlrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, obj.f1, 2);
}
"""

    assert_encoder(func, expected)


def test_encoder_single_field_array_of_fixed_size_string() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "string_3", "count": 2},
        ],
    }
    expected = """template<>
inline void write_unchecked<test_struct>(etl::byte_stream_writer& writer, const test_struct& obj)
{
\tlrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, obj.f1, 2, 3);
}
"""

    assert_encoder(func, expected)


def test_encoder_single_field_custom_no_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType"},
        ],
    }
    expected = """template<>
inline void write_unchecked<test_struct>(etl::byte_stream_writer& writer, const test_struct& obj)
{
\tlrpc::write_unchecked<MyType>(writer, obj.f1);
}
"""

    assert_encoder(func, expected)


def test_encoder_single_field_custom_in_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType"},
        ],
    }
    expected = """template<>
inline void write_unchecked<ns1::test_struct>(etl::byte_stream_writer& writer, const ns1::test_struct& obj)
{
\tlrpc::write_unchecked<ns1::MyType>(writer, obj.f1);
}
"""

    assert_encoder(func, expected, "ns1")


def test_encoder_single_field_array_of_custom_in_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": 2},
        ],
    }
    expected = """template<>
inline void write_unchecked<ns1::test_struct>(etl::byte_stream_writer& writer, const ns1::test_struct& obj)
{
\tlrpc::write_unchecked<lrpc::tags::array_n<ns1::MyType>>(writer, obj.f1, 2);
}
"""

    assert_encoder(func, expected, "ns1")


def test_encoder_single_field_optional_of_custom_no_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": "?"},
        ],
    }
    expected = """template<>
inline void write_unchecked<test_struct>(etl::byte_stream_writer& writer, const test_struct& obj)
{
\tlrpc::write_unchecked<etl::optional<MyType>>(writer, obj.f1);
}
"""

    assert_encoder(func, expected)


def test_encoder_single_field_optional_of_custom_in_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": "?"},
        ],
    }
    expected = """template<>
inline void write_unchecked<ns1::test_struct>(etl::byte_stream_writer& writer, const ns1::test_struct& obj)
{
\tlrpc::write_unchecked<etl::optional<ns1::MyType>>(writer, obj.f1);
}
"""

    assert_encoder(func, expected, "ns1")


def test_encoder_three_fields() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": "?"},
            {"name": "f2", "type": "string_2", "count": 3},
            {"name": "f3", "type": "bool"},
        ],
    }
    expected = """template<>
inline void write_unchecked<ns1::test_struct>(etl::byte_stream_writer& writer, const ns1::test_struct& obj)
{
\tlrpc::write_unchecked<etl::optional<ns1::MyType>>(writer, obj.f1);
\tlrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, obj.f2, 3, 2);
\tlrpc::write_unchecked<bool>(writer, obj.f3);
}
"""

    assert_encoder(func, expected, "ns1")


def test_decoder_single_field_intrinsic() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "uint8_t"},
        ],
    }
    expected = """template<>
inline test_struct read_unchecked<test_struct>(etl::byte_stream_reader& reader)
{
\ttest_struct obj;
\tobj.f1 = lrpc::read_unchecked<uint8_t>(reader);
\treturn obj;
}
"""

    assert_decoder(func, expected)


def test_decoder_single_field_auto_string() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "string"},
        ],
    }
    expected = """template<>
inline test_struct read_unchecked<test_struct>(etl::byte_stream_reader& reader)
{
\ttest_struct obj;
\tobj.f1 = lrpc::read_unchecked<lrpc::tags::string_auto>(reader);
\treturn obj;
}
"""

    assert_decoder(func, expected)


def test_decoder_single_field_fixed_size_string() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "string_2"},
        ],
    }
    expected = """template<>
inline test_struct read_unchecked<test_struct>(etl::byte_stream_reader& reader)
{
\ttest_struct obj;
\tobj.f1 = lrpc::read_unchecked<lrpc::tags::string_n>(reader, 2);
\treturn obj;
}
"""

    assert_decoder(func, expected)


def test_decoder_single_field_array() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "uint8_t", "count": 2},
        ],
    }
    expected = """template<>
inline test_struct read_unchecked<test_struct>(etl::byte_stream_reader& reader)
{
\ttest_struct obj;
\tlrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, obj.f1, 2);
\treturn obj;
}
"""

    assert_decoder(func, expected)


def test_decoder_single_field_array_of_fixed_size_string() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "string_3", "count": 2},
        ],
    }
    expected = """template<>
inline test_struct read_unchecked<test_struct>(etl::byte_stream_reader& reader)
{
\ttest_struct obj;
\tlrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, obj.f1, 2, 3);
\treturn obj;
}
"""

    assert_decoder(func, expected)


def test_decoder_single_field_custom_no_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType"},
        ],
    }
    expected = """template<>
inline test_struct read_unchecked<test_struct>(etl::byte_stream_reader& reader)
{
\ttest_struct obj;
\tobj.f1 = lrpc::read_unchecked<MyType>(reader);
\treturn obj;
}
"""

    assert_decoder(func, expected)


def test_decoder_single_field_custom_in_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType"},
        ],
    }
    expected = """template<>
inline ns1::test_struct read_unchecked<ns1::test_struct>(etl::byte_stream_reader& reader)
{
\tns1::test_struct obj;
\tobj.f1 = lrpc::read_unchecked<ns1::MyType>(reader);
\treturn obj;
}
"""

    assert_decoder(func, expected, "ns1")


def test_decoder_single_field_array_of_custom_in_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": 2},
        ],
    }
    expected = """template<>
inline ns1::test_struct read_unchecked<ns1::test_struct>(etl::byte_stream_reader& reader)
{
\tns1::test_struct obj;
\tlrpc::read_unchecked<lrpc::tags::array_n<ns1::MyType>>(reader, obj.f1, 2);
\treturn obj;
}
"""

    assert_decoder(func, expected, "ns1")


def test_decoder_single_field_optional_of_custom_no_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": "?"},
        ],
    }
    expected = """template<>
inline test_struct read_unchecked<test_struct>(etl::byte_stream_reader& reader)
{
\ttest_struct obj;
\tobj.f1 = lrpc::read_unchecked<etl::optional<MyType>>(reader);
\treturn obj;
}
"""

    assert_decoder(func, expected)


def test_decoder_single_field_optional_of_custom_in_namespace() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": "?"},
        ],
    }
    expected = """template<>
inline ns1::test_struct read_unchecked<ns1::test_struct>(etl::byte_stream_reader& reader)
{
\tns1::test_struct obj;
\tobj.f1 = lrpc::read_unchecked<etl::optional<ns1::MyType>>(reader);
\treturn obj;
}
"""

    assert_decoder(func, expected, "ns1")


def test_decoder_three_fields() -> None:
    func: LrpcStructDict = {
        "name": "test_struct",
        "fields": [
            {"name": "f1", "type": "@MyType", "count": "?"},
            {"name": "f2", "type": "string_2", "count": 3},
            {"name": "f3", "type": "bool"},
        ],
    }
    expected = """template<>
inline ns1::test_struct read_unchecked<ns1::test_struct>(etl::byte_stream_reader& reader)
{
\tns1::test_struct obj;
\tobj.f1 = lrpc::read_unchecked<etl::optional<ns1::MyType>>(reader);
\tlrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, obj.f2, 3, 2);
\tobj.f3 = lrpc::read_unchecked<bool>(reader);
\treturn obj;
}
"""

    assert_decoder(func, expected, "ns1")
