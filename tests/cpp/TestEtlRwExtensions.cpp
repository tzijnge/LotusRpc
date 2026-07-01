// IWYU pragma: no_include <etl/string_view.h>
#include <array>

#include <gtest/gtest.h>

#include "generated/core/lrpccore/EtlRwExtensions.hpp"
#include "generated/core/lrpccore/LrpcByteTypes.hpp"
#include "generated/core/lrpccore/LrpcTypes.hpp"
#if (__cplusplus >= 201703L)
// For std::byte
#include <cstddef>
#endif
#include <cstdint>
#include <numeric>
#include <string>
#include <type_traits>

#include <etl/byte_stream.h>
#include <etl/endianness.h>
#include <etl/optional.h>
#include <etl/span.h>
#include <etl/vector.h>

namespace etl { class string_ext; }
namespace etl { enum class byte : unsigned char; }
namespace etl
{
    template <size_t MAX_SIZE_>
    class string;
}
namespace lrpc
{
    namespace tags { struct bytearray_auto; }
}
namespace lrpc
{
    namespace tags { struct string_auto; }
}
namespace lrpc
{
    namespace tags { struct string_n; }
}
namespace lrpc
{
    namespace tags
    {
        template <typename T>
        struct array_n;
    }
}

TEST(TestEtlRwExtensions, is_lrpc_optional)
{
    EXPECT_FALSE(lrpc::is_optional<int>::value);
    EXPECT_TRUE(lrpc::is_optional<lrpc::optional<int>>::value);
}

TEST(TestEtlRwExtensions, is_etl_string)
{
    EXPECT_FALSE(lrpc::is_string_n<int>::value);
    EXPECT_FALSE(lrpc::is_string_n<std::string>::value);
    EXPECT_FALSE(lrpc::is_string_n<lrpc::string_view>::value);
    EXPECT_FALSE(lrpc::is_string_n<etl::string_ext>::value);
    EXPECT_FALSE(lrpc::is_string_n<etl::string<10>>::value);
    EXPECT_TRUE(lrpc::is_string_n<lrpc::tags::string_n>::value);
}

TEST(TestEtlRwExtensions, is_array_n)
{
    EXPECT_FALSE(lrpc::is_array_n<int>::value);
    EXPECT_FALSE((lrpc::is_array_n<std::array<int, 4>>::value));
    EXPECT_FALSE((lrpc::is_array_n<lrpc::array<int, 4>>::value));
    EXPECT_TRUE((lrpc::is_array_n<lrpc::tags::array_n<int>>::value));
}

TEST(TestEtlRwExtensions, optional_type)
{
    EXPECT_TRUE((std::is_same<uint16_t, lrpc::optional_type<lrpc::optional<uint16_t>>::type>::value));
    EXPECT_FALSE((std::is_same<uint16_t, lrpc::optional_type<lrpc::optional<uint32_t>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::tags::string_auto,
                              lrpc::optional_type<lrpc::optional<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE(
        (std::is_same<lrpc::tags::string_n, lrpc::optional_type<lrpc::optional<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::tags::bytearray_auto,
                              lrpc::optional_type<lrpc::optional<lrpc::tags::bytearray_auto>>::type>::value));
}

TEST(TestEtlRwExtensions, optional_pr_type)
{
    EXPECT_TRUE(
        (std::is_same<lrpc::optional<uint16_t>, lrpc::optional_pr_type<lrpc::optional<uint16_t>>::type>::value));
    EXPECT_FALSE(
        (std::is_same<lrpc::optional<uint16_t>, lrpc::optional_pr_type<lrpc::optional<uint32_t>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::optional<lrpc::string_view>,
                              lrpc::optional_pr_type<lrpc::optional<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::optional<lrpc::string_view>,
                              lrpc::optional_pr_type<lrpc::optional<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::optional<lrpc::bytearray>,
                              lrpc::optional_pr_type<lrpc::optional<lrpc::tags::bytearray_auto>>::type>::value));
}

TEST(TestEtlRwExtensions, array_n_type)
{
    EXPECT_NE(typeid(uint16_t), typeid(lrpc::array_n_type<lrpc::tags::array_n<uint32_t>>::type));
    EXPECT_EQ(typeid(uint16_t), typeid(lrpc::array_n_type<lrpc::tags::array_n<uint16_t>>::type));
}

TEST(TestEtlRwExtensions, array_param_type)
{
    EXPECT_TRUE(
        (std::is_same<lrpc::span<const uint16_t>, lrpc::array_param_type<lrpc::tags::array_n<uint16_t>>::type>::value));
    EXPECT_FALSE(
        (std::is_same<lrpc::span<const uint16_t>, lrpc::array_param_type<lrpc::tags::array_n<uint32_t>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::span<const lrpc::string_view>,
                              lrpc::array_param_type<lrpc::tags::array_n<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::span<const lrpc::string_view>,
                              lrpc::array_param_type<lrpc::tags::array_n<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::span<const lrpc::bytearray>,
                              lrpc::array_param_type<lrpc::tags::array_n<lrpc::tags::bytearray_auto>>::type>::value));
}

TEST(TestEtlRwExtensions, array_out_param_type)
{
    EXPECT_TRUE(
        (std::is_same<lrpc::span<uint16_t>, lrpc::array_outparam_type<lrpc::tags::array_n<uint16_t>>::type>::value));
    EXPECT_FALSE(
        (std::is_same<lrpc::span<uint16_t>, lrpc::array_outparam_type<lrpc::tags::array_n<uint32_t>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::span<lrpc::string_view>,
                              lrpc::array_outparam_type<lrpc::tags::array_n<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE((std::is_same<lrpc::span<lrpc::string_view>,
                              lrpc::array_outparam_type<lrpc::tags::array_n<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE(
        (std::is_same<lrpc::span<lrpc::bytearray>,
                      lrpc::array_outparam_type<lrpc::tags::array_n<lrpc::tags::bytearray_auto>>::type>::value));
}

template <typename T>
class TestEtlRwExtArithTypes : public ::testing::Test
{
};

using ArithmeticTypes =
    ::testing::Types<bool, uint8_t, int8_t, uint16_t, int16_t, uint32_t, int32_t, uint64_t, int64_t, float, double>;

struct ArithmeticTypeNames
{
    template <typename T>
    static std::string GetName(int64_t /* index */)
    {
        static_assert(sizeof(T) == 0, "unknown type in ArithmeticTypes");
        return "";
    }
};

// clang-format off
template <> std::string ArithmeticTypeNames::GetName<bool>(int64_t /* index */)     { return "bool"; }
template <> std::string ArithmeticTypeNames::GetName<uint8_t>(int64_t /* index */)  { return "uint8_t"; }
template <> std::string ArithmeticTypeNames::GetName<int8_t>(int64_t /* index */)   { return "int8_t"; }
template <> std::string ArithmeticTypeNames::GetName<uint16_t>(int64_t /* index */) { return "uint16_t"; }
template <> std::string ArithmeticTypeNames::GetName<int16_t>(int64_t /* index */)  { return "int16_t"; }
template <> std::string ArithmeticTypeNames::GetName<uint32_t>(int64_t /* index */) { return "uint32_t"; }
template <> std::string ArithmeticTypeNames::GetName<int32_t>(int64_t /* index */)  { return "int32_t"; }
template <> std::string ArithmeticTypeNames::GetName<uint64_t>(int64_t /* index */) { return "uint64_t"; }
template <> std::string ArithmeticTypeNames::GetName<int64_t>(int64_t /* index */)  { return "int64_t"; }
template <> std::string ArithmeticTypeNames::GetName<float>(int64_t /* index */)    { return "float"; }
template <> std::string ArithmeticTypeNames::GetName<double>(int64_t /* index */)   { return "double"; }
// clang-format on

TYPED_TEST_SUITE(TestEtlRwExtArithTypes, ArithmeticTypes, ArithmeticTypeNames);

TYPED_TEST(TestEtlRwExtArithTypes, write)
{
    etl::vector<uint8_t, sizeof(TypeParam)> storage(sizeof(TypeParam));
    etl::byte_stream_writer writer(storage, etl::endian::little);
    lrpc::write_unchecked<TypeParam>(writer, TypeParam{1});
    EXPECT_EQ(sizeof(TypeParam), writer.used_data().size());
}

TYPED_TEST(TestEtlRwExtArithTypes, read)
{
    etl::vector<uint8_t, sizeof(TypeParam)> storage(sizeof(TypeParam));
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    EXPECT_EQ(TypeParam{0}, lrpc::read_unchecked<TypeParam>(reader));
    EXPECT_EQ(0U, reader.available_bytes());
}

TYPED_TEST(TestEtlRwExtArithTypes, roundTrip)
{
    const auto value = static_cast<TypeParam>(42);
    etl::vector<uint8_t, sizeof(TypeParam)> storage(sizeof(TypeParam));
    etl::byte_stream_writer writer(storage, etl::endian::little);
    lrpc::write_unchecked<TypeParam>(writer, value);

    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    EXPECT_EQ(value, lrpc::read_unchecked<TypeParam>(reader));
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, readEnum)
{
    enum class Dummy : uint8_t
    {
        V1 = 0xAA
    };

    etl::vector<uint8_t, 1> storage{0xAA};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ(Dummy::V1, lrpc::read_unchecked<Dummy>(reader));
}

TEST(TestEtlRwExtensions, readAutoString)
{
    etl::vector<char, 10> storage{'T', 'e', 's', 't', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::tags::string_auto>(reader));
}

TEST(TestEtlRwExtensions, readAutoStringEmpty)
{
    etl::vector<char, 3> storage{'\0', 'x', 'y'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("", lrpc::read_unchecked<lrpc::tags::string_auto>(reader));
    EXPECT_EQ(2U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, readAutoStringNoNullTerminator)
{
    // No null in stream: all remaining bytes are returned as the string
    etl::vector<char, 4> storage{'a', 'b', 'c', 'd'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("abcd", lrpc::read_unchecked<lrpc::tags::string_auto>(reader));
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, readFixedSizeString)
{
    etl::vector<char, 10> storage{'T', 'e', 's', 't', '\0', '\0', 'q', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("Tes", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 3));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 4));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 5));
    EXPECT_EQ("q", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 1));
}

TEST(TestEtlRwExtensions, readFixedSizeStringEmpty)
{
    // Slot starts with '\0': returns empty string, skips full slot
    etl::vector<char, 6> storage{'\0', '\0', '\0', '\0', 'q', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 3));
    EXPECT_EQ("q", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 1));
}

TEST(TestEtlRwExtensions, readOptional)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<lrpc::optional<uint8_t>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<lrpc::optional<uint8_t>>(reader);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ(0x02, o2.value());
}

TEST(TestEtlRwExtensions, readOptionalAutoString)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::string_auto>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::string_auto>>(reader);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ("T1", o2.value());
}

TEST(TestEtlRwExtensions, readOptionalFixedSizeString)
{
    const etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::string_n>>(reader, 2);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::string_n>>(reader, 2);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ("T1", o2.value());
}

TEST(TestEtlRwExtensions, readOptionalBytearray)
{
    const etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x03, 0x11, 0x22, 0x33};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::bytearray_auto>>(reader);
    EXPECT_FALSE(o1.has_value());
    const auto o2 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::bytearray_auto>>(reader);
    EXPECT_TRUE(o2.has_value());
    ASSERT_EQ(3, o2.value().size());
    EXPECT_EQ(0x11, o2.value().at(0));
    EXPECT_EQ(0x22, o2.value().at(1));
    EXPECT_EQ(0x33, o2.value().at(2));
}

TEST(TestEtlRwExtensions, readArrayOfBytearray)
{
    const etl::vector<uint8_t, 10> storage{0x02, 0x11, 0x22, 0x03, 0x33, 0x44, 0x55};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    lrpc::array<lrpc::bytearray, 2> a1;
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::bytearray_auto>>(reader, a1, 2);
    ASSERT_EQ(2, a1.size());
    ASSERT_EQ(2, a1.at(0).size());
    EXPECT_EQ(0x11, a1.at(0).at(0));
    EXPECT_EQ(0x22, a1.at(0).at(1));
    ASSERT_EQ(3, a1.at(1).size());
    EXPECT_EQ(0x33, a1.at(1).at(0));
    EXPECT_EQ(0x44, a1.at(1).at(1));
    EXPECT_EQ(0x55, a1.at(1).at(2));
}

TEST(TestEtlRwExtensions, readArray)
{
    const etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02, 0x00};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    lrpc::array<uint8_t, 4> dest{0xFF, 0xFF, 0xFF, 0xFF};
    lrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, dest, 3);
    EXPECT_EQ(0x00, dest.at(0));
    EXPECT_EQ(0x01, dest.at(1));
    EXPECT_EQ(0x02, dest.at(2));
    EXPECT_EQ(0xFF, dest.at(3));
}

TEST(TestEtlRwExtensions, readArrayToInsufficientStorage)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02, 0xAB};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    // Read of array size 3 is requested, but destination array has capacity 2
    lrpc::array<uint8_t, 2> dest{0xFF, 0xFF};
    lrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, dest, 3);
    EXPECT_EQ(0x00, dest.at(0));
    EXPECT_EQ(0x01, dest.at(1));
    EXPECT_EQ(0xAB, lrpc::read_unchecked<uint8_t>(reader));
}

TEST(TestEtlRwExtensions, readArrayOfEnumToInsufficientStorage)
{
    enum class Dummy : uint8_t
    {
        V1 = 0xAA,
        V2 = 0xBB,
        V3 = 0xCC
    };

    etl::vector<uint8_t, 4> storage{0xAA, 0xBB, 0xCC, 0xAB};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    // Read of array size 3 is requested, but destination array has capacity 2
    lrpc::array<Dummy, 2> dest{Dummy::V1, Dummy::V1};
    lrpc::read_unchecked<lrpc::tags::array_n<Dummy>>(reader, dest, 3);
    EXPECT_EQ(Dummy::V1, dest.at(0));
    EXPECT_EQ(Dummy::V2, dest.at(1));
    EXPECT_EQ(0xAB, lrpc::read_unchecked<uint8_t>(reader));
}

TEST(TestEtlRwExtensions, readArrayOfFixedSizeString)
{
    etl::vector<char, 10> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    lrpc::array<lrpc::string_view, 4> dest{"o1", "o2", "o3", "o4"};
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, dest, 3, 2);
    EXPECT_EQ("t1", dest.at(0));
    EXPECT_EQ("t2", dest.at(1));
    EXPECT_EQ("t3", dest.at(2));
    EXPECT_EQ("o4", dest.at(3));
}

TEST(TestEtlRwExtensions, readArrayOfFixedSizeStringToInsufficientStorage)
{
    etl::vector<char, 10> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '\0', static_cast<char>(0xAB)};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    // Read of array size 3 is requested, but destination array has capacity 2
    lrpc::array<lrpc::string_view, 2> dest{"o1", "o2"};
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, dest, 3, 2);
    EXPECT_EQ("t1", dest.at(0));
    EXPECT_EQ("t2", dest.at(1));
    EXPECT_EQ(0xAB, lrpc::read_unchecked<uint8_t>(reader));
}

TEST(TestEtlRwExtensions, readArrayOfAutoString)
{
    etl::vector<char, 12> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '4', '5', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    lrpc::array<lrpc::string_view, 4> dest{"o1", "o2", "o3", "o4"};
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_auto>>(reader, dest, 3);
    EXPECT_EQ("t1", dest.at(0));
    EXPECT_EQ("t2", dest.at(1));
    EXPECT_EQ("t345", dest.at(2));
    EXPECT_EQ("o4", dest.at(3));
}

TEST(TestEtlRwExtensions, readArrayOfAutoStringToInsufficientStorage)
{
    etl::vector<char, 13> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '4', '5', '\0', static_cast<char>(0xAB)};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    // Read of array size 3 is requested, but destination array has capacity 2
    lrpc::array<lrpc::string_view, 2> dest{"o1", "o2"};
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_auto>>(reader, dest, 3);
    EXPECT_EQ("t1", dest.at(0));
    EXPECT_EQ("t2", dest.at(1));
    EXPECT_EQ(0xAB, lrpc::read_unchecked<uint8_t>(reader));
}

TEST(TestEtlRwExtensions, readBytearray)
{
    etl::vector<uint8_t, 4> storage{0x03, 0x01, 0x02, 0x03};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto bytearray = lrpc::read_unchecked<lrpc::tags::bytearray_auto>(reader);
    ASSERT_EQ(3, bytearray.size());
    EXPECT_EQ(0x01, bytearray.at(0));
    EXPECT_EQ(0x02, bytearray.at(1));
    EXPECT_EQ(0x03, bytearray.at(2));

    storage.at(0) = 0x02;
    reader.restart();

    bytearray = lrpc::read_unchecked<lrpc::tags::bytearray_auto>(reader);
    ASSERT_EQ(2, bytearray.size());
    EXPECT_EQ(0x01, bytearray.at(0));
    EXPECT_EQ(0x02, bytearray.at(1));
    EXPECT_EQ(0x03, lrpc::read_unchecked<uint8_t>(reader));

    storage.at(0) = 0x0A;
    reader.restart();

    bytearray = lrpc::read_unchecked<lrpc::tags::bytearray_auto>(reader);
    ASSERT_EQ(3, bytearray.size());
    EXPECT_EQ(0x01, bytearray.at(0));
    EXPECT_EQ(0x02, bytearray.at(1));
    EXPECT_EQ(0x03, bytearray.at(2));
}

TEST(TestEtlRwExtensions, readBytearrayEmpty)
{
    etl::vector<uint8_t, 3> storage{0x00, 0xAB, 0xCD};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto ba = lrpc::read_unchecked<lrpc::tags::bytearray_auto>(reader);
    EXPECT_EQ(0U, ba.size());
    EXPECT_EQ(lrpc::byte{0xAB}, lrpc::read_unchecked<lrpc::byte>(reader));
}

TEST(TestEtlRwExtensions, readEtlByte)
{
    etl::vector<uint8_t, 4> storage{0x11, 0xAB};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ(etl::byte(0x11), lrpc::read_unchecked<etl::byte>(reader));
    EXPECT_EQ(etl::byte(0xAB), lrpc::read_unchecked<etl::byte>(reader));
}

#if (__cplusplus >= 201703L)
TEST(TestEtlRwExtensions, readStdByte)
{
    etl::vector<uint8_t, 4> storage{0x56, 0xCD};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ(std::byte{0x56}, lrpc::read_unchecked<std::byte>(reader));
    EXPECT_EQ(std::byte{0xCD}, lrpc::read_unchecked<std::byte>(reader));
}
#endif

TEST(TestEtlRwExtensions, writeEnum)
{
    enum class Dummy : uint8_t
    {
        V1 = 0xBB
    };

    etl::vector<uint8_t, 1> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<Dummy>(writer, Dummy::V1);
    const auto written = writer.used_data();
    ASSERT_EQ(1, written.size());
    EXPECT_EQ(0xBB, static_cast<uint8_t>(written.at(0)));
}

TEST(TestEtlRwExtensions, writeOptional)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<lrpc::optional<uint8_t>>(writer, {});
    lrpc::write_unchecked<lrpc::optional<uint8_t>>(writer, 0x02);

    const auto written = writer.used_data();
    ASSERT_EQ(3, written.size());
    EXPECT_EQ(0x00, static_cast<uint8_t>(written.at(0)));
    EXPECT_EQ(0x01, static_cast<uint8_t>(written.at(1)));
    EXPECT_EQ(0x02, static_cast<uint8_t>(written.at(2)));
}

TEST(TestEtlRwExtensions, writeFixedSizeString)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<lrpc::tags::string_n>(writer, "T1", 4);
    const lrpc::string_view t2("T2");
    lrpc::write_unchecked<lrpc::tags::string_n>(writer, t2, 2);

    const auto written = writer.used_data();
    ASSERT_EQ(8, written.size());
    EXPECT_EQ('T', written.at(0));
    EXPECT_EQ('1', written.at(1));
    EXPECT_EQ('\0', written.at(2));
    EXPECT_EQ('\0', written.at(3));
    EXPECT_EQ('\0', written.at(4));
    EXPECT_EQ('T', written.at(5));
    EXPECT_EQ('2', written.at(6));
    EXPECT_EQ('\0', written.at(7));
}

TEST(TestEtlRwExtensions, writeFixedSizeStringOverflow)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<lrpc::tags::string_n>(writer, "test123", 4);

    const auto written = writer.used_data();
    ASSERT_EQ(5, written.size());
    EXPECT_EQ('t', written.at(0));
    EXPECT_EQ('e', written.at(1));
    EXPECT_EQ('s', written.at(2));
    EXPECT_EQ('t', written.at(3));
    EXPECT_EQ('\0', written.at(4));
}

TEST(TestEtlRwExtensions, writeFixedSizeStringEmpty)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<lrpc::tags::string_n>(writer, "", 3);

    const auto written = writer.used_data();
    ASSERT_EQ(4, written.size());
    EXPECT_EQ('\0', written.at(0));
    EXPECT_EQ('\0', written.at(1));
    EXPECT_EQ('\0', written.at(2));
    EXPECT_EQ('\0', written.at(3));
}

TEST(TestEtlRwExtensions, writeAutoString)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<lrpc::tags::string_auto>(writer, "T1");
    const lrpc::string_view t2("T2");
    lrpc::write_unchecked<lrpc::tags::string_auto>(writer, t2);

    const auto written = writer.used_data();
    ASSERT_EQ(6, written.size());
    EXPECT_EQ('T', written.at(0));
    EXPECT_EQ('1', written.at(1));
    EXPECT_EQ('\0', written.at(2));
    EXPECT_EQ('T', written.at(3));
    EXPECT_EQ('2', written.at(4));
    EXPECT_EQ('\0', written.at(5));
}

TEST(TestEtlRwExtensions, writeAutoStringEmpty)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<lrpc::tags::string_auto>(writer, "");

    const auto written = writer.used_data();
    ASSERT_EQ(1, written.size());
    EXPECT_EQ('\0', written.at(0));
}

TEST(TestEtlRwExtensions, writeByteArray)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    const lrpc::array<lrpc::byte, 3> a0{0x11, 0x12, 0x13};
    const lrpc::array<lrpc::byte, 2> a1{0x14, 0x15};
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, a0);
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, a1);
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, {});
    // overflows the storage
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, a1);

    const auto written = writer.used_data();
    ASSERT_EQ(10, written.size());
    EXPECT_EQ(0x03, written.at(0));
    EXPECT_EQ(0x11, written.at(1));
    EXPECT_EQ(0x12, written.at(2));
    EXPECT_EQ(0x13, written.at(3));
    EXPECT_EQ(0x02, written.at(4));
    EXPECT_EQ(0x14, written.at(5));
    EXPECT_EQ(0x15, written.at(6));
    EXPECT_EQ(0x00, written.at(7));
    EXPECT_EQ(0x02, written.at(8));
    EXPECT_EQ(0x14, written.at(9));
}

TEST(TestEtlRwExtensions, writeBytearrayTooBig)
{
    // Test that bytearray size is truncated to the max value
    // of the size field. This does not say anything about whether
    // or not the value will fit in the transmit buffer

    lrpc::array<lrpc::byte, 500> storage{};
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::array<lrpc::byte, 300> a0{};
    std::iota(a0.begin(), a0.end(), lrpc::byte{0});
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, a0);

    const auto written = writer.used_data();
    ASSERT_EQ(256, written.size());
    EXPECT_EQ(0xFF, static_cast<uint8_t>(written.at(0)));
    EXPECT_EQ(0x00, static_cast<uint8_t>(written.at(1)));
    EXPECT_EQ(0x01, static_cast<uint8_t>(written.at(2)));
    EXPECT_EQ(0x02, static_cast<uint8_t>(written.at(3)));
    // ...
    EXPECT_EQ(0xFC, static_cast<uint8_t>(written.at(253)));
    EXPECT_EQ(0xFD, static_cast<uint8_t>(written.at(254)));
    EXPECT_EQ(0xFE, static_cast<uint8_t>(written.at(255)));
}

TEST(TestEtlRwExtensions, writeArray)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::array<uint8_t, 3> t2{0x01, 0x02, 0x03};
    lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, t2, 2);

    const auto written = writer.used_data();
    ASSERT_EQ(2, written.size());
    EXPECT_EQ(0x01, written.at(0));
    EXPECT_EQ(0x02, written.at(1));
}

TEST(TestEtlRwExtensions, writeArrayFromInsufficientStorage)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    // request to write 3, but only 2 available. Fill remaining with default values
    lrpc::array<uint8_t, 2> t2{0x01, 0x02};
    lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, t2, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(3, written.size());
    EXPECT_EQ(0x01, written.at(0));
    EXPECT_EQ(0x02, written.at(1));
    EXPECT_EQ(0x00, written.at(2));
}

TEST(TestEtlRwExtensions, writeArrayOfFixedSizeString)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::array<lrpc::string_view, 2> a0{"T1", "T22"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, a0, 2, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(8, written.size());
    EXPECT_EQ('T', written.at(0));
    EXPECT_EQ('1', written.at(1));
    EXPECT_EQ('\0', written.at(2));
    EXPECT_EQ('\0', written.at(3));
    EXPECT_EQ('T', written.at(4));
    EXPECT_EQ('2', written.at(5));
    EXPECT_EQ('2', written.at(6));
    EXPECT_EQ('\0', written.at(7));
}

TEST(TestEtlRwExtensions, writeArrayOfFixedSizeStringFromInsufficientStorage)
{
    lrpc::array<uint8_t, 12> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    // request to write 3, but only 2 available. Fill remaining with default values
    lrpc::array<lrpc::string_view, 2> a0{"T1", "T22"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, a0, 3, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(12, written.size());
    EXPECT_EQ('T', written.at(0));
    EXPECT_EQ('1', written.at(1));
    EXPECT_EQ('\0', written.at(2));
    EXPECT_EQ('\0', written.at(3));
    EXPECT_EQ('T', written.at(4));
    EXPECT_EQ('2', written.at(5));
    EXPECT_EQ('2', written.at(6));
    EXPECT_EQ('\0', written.at(7));
    EXPECT_EQ('\0', written.at(8));
    EXPECT_EQ('\0', written.at(9));
    EXPECT_EQ('\0', written.at(10));
    EXPECT_EQ('\0', written.at(11));
}

TEST(TestEtlRwExtensions, writeArrayOfAutoString)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::array<lrpc::string_view, 2> a0{"T1", "T1234"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_auto>>(writer, a0, 2);

    const auto written = writer.used_data();
    ASSERT_EQ(9, written.size());
    EXPECT_EQ('T', written.at(0));
    EXPECT_EQ('1', written.at(1));
    EXPECT_EQ('\0', written.at(2));
    EXPECT_EQ('T', written.at(3));
    EXPECT_EQ('1', written.at(4));
    EXPECT_EQ('2', written.at(5));
    EXPECT_EQ('3', written.at(6));
    EXPECT_EQ('4', written.at(7));
    EXPECT_EQ('\0', written.at(8));
}

TEST(TestEtlRwExtensions, writeArrayOfAutoStringFromInsufficientStorage)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    // request to write 3, but only 2 available. Fill remaining with default values
    lrpc::array<lrpc::string_view, 2> a0{"T1", "T1234"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_auto>>(writer, a0, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(10, written.size());
    EXPECT_EQ('T', written.at(0));
    EXPECT_EQ('1', written.at(1));
    EXPECT_EQ('\0', written.at(2));
    EXPECT_EQ('T', written.at(3));
    EXPECT_EQ('1', written.at(4));
    EXPECT_EQ('2', written.at(5));
    EXPECT_EQ('3', written.at(6));
    EXPECT_EQ('4', written.at(7));
    EXPECT_EQ('\0', written.at(8));
    EXPECT_EQ('\0', written.at(9));
}

TEST(TestEtlRwExtensions, writeOptionalFixedSizeString)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    const lrpc::optional<lrpc::string_view> a0{"T1"};
    const lrpc::optional<lrpc::string_view> a1{};
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::string_n>>(writer, a0, 3);
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::string_n>>(writer, a1, 5);

    const auto written = writer.used_data();
    ASSERT_EQ(6, written.size());
    EXPECT_EQ(0x01, written.at(0));
    EXPECT_EQ('T', written.at(1));
    EXPECT_EQ('1', written.at(2));
    EXPECT_EQ('\0', written.at(3));
    EXPECT_EQ('\0', written.at(4));
    EXPECT_EQ(0x00, written.at(5));
}

TEST(TestEtlRwExtensions, writeOptionalAutoString)
{
    lrpc::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    const lrpc::optional<lrpc::string_view> a0{"T1"};
    const lrpc::optional<lrpc::string_view> a1{};
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::string_auto>>(writer, a0);
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::string_auto>>(writer, a1);

    const auto written = writer.used_data();
    ASSERT_EQ(5, written.size());
    EXPECT_EQ(0x01, written.at(0));
    EXPECT_EQ('T', written.at(1));
    EXPECT_EQ('1', written.at(2));
    EXPECT_EQ('\0', written.at(3));
    EXPECT_EQ(0x00, written.at(4));
}

TEST(TestEtlRwExtensions, writeOptionalBytearray)
{
    lrpc::array<uint8_t, 10> storage;
    const lrpc::array<lrpc::byte, 2> o1{0x11, 0x22};
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<lrpc::optional<lrpc::tags::bytearray_auto>>(writer, {});
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::bytearray_auto>>(writer, lrpc::span<const lrpc::byte>{});
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::bytearray_auto>>(writer, lrpc::span<const lrpc::byte>{o1});

    const auto written = writer.used_data();
    ASSERT_EQ(7, written.size());
    // optional without value
    EXPECT_EQ(0x00, written.at(0));
    // optional with empty bytearray
    EXPECT_EQ(0x01, written.at(1));
    EXPECT_EQ(0x00, written.at(2));
    // optional with o1
    EXPECT_EQ(0x01, written.at(3));
    EXPECT_EQ(0x02, written.at(4));
    EXPECT_EQ(0x11, written.at(5));
    EXPECT_EQ(0x22, written.at(6));
}

TEST(TestEtlRwExtensions, writeArrayOfBytearray)
{
    lrpc::array<uint8_t, 10> storage;
    const lrpc::array<lrpc::byte, 2> ba1{0x11, 0x22};
    const lrpc::array<lrpc::byte, 3> ba2{0x33, 0x44, 0x55};
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::array<lrpc::span<const lrpc::byte>, 2> baArray{ba1, ba2};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::bytearray_auto>>(writer, baArray, 2);

    const auto written = writer.used_data();
    ASSERT_EQ(7, written.size());
    EXPECT_EQ(0x02, written.at(0));
    EXPECT_EQ(0x11, written.at(1));
    EXPECT_EQ(0x22, written.at(2));
    EXPECT_EQ(0x03, written.at(3));
    EXPECT_EQ(0x33, written.at(4));
    EXPECT_EQ(0x44, written.at(5));
    EXPECT_EQ(0x55, written.at(6));
}

TEST(TestEtlRwExtensions, writeEtlByte)
{
    lrpc::array<uint8_t, 2> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<etl::byte>(writer, static_cast<etl::byte>(0x11));
    lrpc::write_unchecked<etl::byte>(writer, static_cast<etl::byte>(0x56));

    const auto written = writer.used_data();
    ASSERT_EQ(2, written.size());
    EXPECT_EQ(0x11, written.at(0));
    EXPECT_EQ(0x56, written.at(1));
}

#if (__cplusplus >= 201703L)
TEST(TestEtlRwExtensions, writeStdByte)
{
    lrpc::array<uint8_t, 2> storage;
    etl::byte_stream_writer writer(storage, etl::endian::little);

    lrpc::write_unchecked<std::byte>(writer, std::byte{0x11});
    lrpc::write_unchecked<std::byte>(writer, std::byte{0x56});

    const auto written = writer.used_data();
    ASSERT_EQ(2, written.size());
    EXPECT_EQ(0x11, written.at(0));
    EXPECT_EQ(0x56, written.at(1));
}
#endif

TEST(TestEtlRwExtensions, roundTripEnum)
{
    enum class Color : uint8_t
    {
        Red = 0x01,
        Green = 0x02,
        Blue = 0x03
    };

    etl::vector<uint8_t, 3> storage(3);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    lrpc::write_unchecked<Color>(writer, Color::Red);
    lrpc::write_unchecked<Color>(writer, Color::Green);
    lrpc::write_unchecked<Color>(writer, Color::Blue);

    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    EXPECT_EQ(Color::Red, lrpc::read_unchecked<Color>(reader));
    EXPECT_EQ(Color::Green, lrpc::read_unchecked<Color>(reader));
    EXPECT_EQ(Color::Blue, lrpc::read_unchecked<Color>(reader));
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, roundTripAutoString)
{
    // "hello" + null = 6 bytes, "" + null = 1 byte
    etl::vector<uint8_t, 7> storage(7);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    lrpc::write_unchecked<lrpc::tags::string_auto>(writer, "hello");
    lrpc::write_unchecked<lrpc::tags::string_auto>(writer, "");

    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    EXPECT_EQ("hello", lrpc::read_unchecked<lrpc::tags::string_auto>(reader));
    EXPECT_EQ("", lrpc::read_unchecked<lrpc::tags::string_auto>(reader));
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, roundTripFixedSizeString)
{
    // slot size 4: each element occupies exactly 5 bytes (definitionStringSize + 1)
    // three cases: value shorter than slot, equal, longer (truncated)
    etl::vector<uint8_t, 15> storage(15);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    lrpc::write_unchecked<lrpc::tags::string_n>(writer, "hi", 4);
    lrpc::write_unchecked<lrpc::tags::string_n>(writer, "abcd", 4);
    lrpc::write_unchecked<lrpc::tags::string_n>(writer, "toolong", 4);

    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    EXPECT_EQ("hi", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 4));
    EXPECT_EQ("abcd", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 4));
    EXPECT_EQ("tool", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 4));
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, roundTripBytearray)
{
    const lrpc::array<lrpc::byte, 3> ba{0x11, 0x22, 0x33};
    // ba: 1 size byte + 3 data = 4 bytes; empty: 1 size byte = 1 byte
    etl::vector<uint8_t, 5> storage(5);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, ba);
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, {});

    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    const auto result = lrpc::read_unchecked<lrpc::tags::bytearray_auto>(reader);
    ASSERT_EQ(3U, result.size());
    EXPECT_EQ(0x11, result.at(0));
    EXPECT_EQ(0x22, result.at(1));
    EXPECT_EQ(0x33, result.at(2));
    const auto empty = lrpc::read_unchecked<lrpc::tags::bytearray_auto>(reader);
    EXPECT_EQ(0U, empty.size());
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, roundTripOptional)
{
    // absent: 1 byte; present uint16_t: 1 + 2 = 3 bytes
    etl::vector<uint8_t, 4> storage(4);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    lrpc::write_unchecked<lrpc::optional<uint16_t>>(writer, {});
    lrpc::write_unchecked<lrpc::optional<uint16_t>>(writer, 0x1234U);

    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    const auto o1 = lrpc::read_unchecked<lrpc::optional<uint16_t>>(reader);
    EXPECT_FALSE(o1.has_value());
    const auto o2 = lrpc::read_unchecked<lrpc::optional<uint16_t>>(reader);
    ASSERT_TRUE(o2.has_value());
    EXPECT_EQ(0x1234U, o2.value());
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, roundTripOptionalFixedSizeString)
{
    // absent: 1 byte; present "hi" in slot 3: 1 + 4 = 5 bytes
    etl::vector<uint8_t, 6> storage(6);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    const lrpc::optional<lrpc::string_view> absent{};
    const lrpc::optional<lrpc::string_view> present{"hi"};
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::string_n>>(writer, absent, 3);
    lrpc::write_unchecked<lrpc::optional<lrpc::tags::string_n>>(writer, present, 3);

    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    const auto o1 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::string_n>>(reader, 3);
    EXPECT_FALSE(o1.has_value());
    const auto o2 = lrpc::read_unchecked<lrpc::optional<lrpc::tags::string_n>>(reader, 3);
    ASSERT_TRUE(o2.has_value());
    EXPECT_EQ("hi", o2.value());
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, roundTripArray)
{
    etl::vector<uint8_t, 3> storage(3);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    const lrpc::array<uint8_t, 3> values{0x0A, 0x0B, 0x0C};
    lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, values, 3);

    lrpc::array<uint8_t, 3> dest;
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    lrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, dest, 3);
    EXPECT_EQ(0x0A, dest.at(0));
    EXPECT_EQ(0x0B, dest.at(1));
    EXPECT_EQ(0x0C, dest.at(2));
    EXPECT_EQ(0U, reader.available_bytes());
}

TEST(TestEtlRwExtensions, roundTripArrayOfFixedSizeString)
{
    // 2 elements, slot size 3: each uses 4 bytes, total 8 bytes
    etl::vector<uint8_t, 8> storage(8);
    etl::byte_stream_writer writer(storage, etl::endian::little);
    const lrpc::array<lrpc::string_view, 2> values{"ab", "cd"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, values, 2, 3);

    lrpc::array<lrpc::string_view, 2> dest{"", ""};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, dest, 2, 3);
    EXPECT_EQ("ab", dest.at(0));
    EXPECT_EQ("cd", dest.at(1));
    EXPECT_EQ(0U, reader.available_bytes());
}