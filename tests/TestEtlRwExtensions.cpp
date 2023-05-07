#include <gtest/gtest.h>
#include "EtlRwExtensions.hpp"
#include <string>
#include <array>
#include <etl/vector.h>

// MATCHER_P(SPAN_EQ, e, "Equality matcher for etl::span")
// {
//     if (e.size() != arg.size())
//     {
//         return false;
//     }
//     for (auto i = 0; i < e.size(); ++i)
//     {
//         if (e[i] != arg[i])
//         {
//             return false;
//         }
//     }
//     return true;
// }

TEST(TestEtlRwExtensions, is_etl_optional)
{
    EXPECT_FALSE(lrpc::is_etl_optional<int>::value);
    EXPECT_FALSE(lrpc::is_etl_optional<std::optional<int>>::value);
    EXPECT_TRUE(lrpc::is_etl_optional<etl::optional<int>>::value);
}

TEST(TestEtlRwExtensions, is_etl_string)
{
    EXPECT_FALSE(lrpc::is_etl_string<int>::value);
    EXPECT_FALSE(lrpc::is_etl_string<std::string>::value);
    EXPECT_FALSE(lrpc::is_etl_string<etl::string_view>::value);
    EXPECT_FALSE(lrpc::is_etl_string<etl::string_ext>::value);
    EXPECT_TRUE(lrpc::is_etl_string<etl::string<10>>::value);
}

TEST(TestEtlRwExtensions, is_etl_array)
{
    EXPECT_FALSE(lrpc::is_etl_array<int>::value);
    EXPECT_FALSE((lrpc::is_etl_array<std::array<int, 4>>::value));
    EXPECT_TRUE((lrpc::is_etl_array<etl::array<int, 4>>::value));
}

TEST(TestEtlRwExtensions, etl_optional_type)
{
    EXPECT_NE(typeid(uint32_t), typeid(lrpc::etl_optional_type<etl::optional<uint16_t>>::type));
    EXPECT_EQ(typeid(uint16_t), typeid(lrpc::etl_optional_type<etl::optional<uint16_t>>::type));
}

TEST(TestEtlRwExtensions, etl_array_type)
{
    EXPECT_NE(typeid(uint16_t), typeid(lrpc::etl_array_type<etl::array<uint32_t, 2>>::type));
    EXPECT_EQ(typeid(uint16_t), typeid(lrpc::etl_array_type<etl::array<uint16_t, 2>>::type));
}

TEST(TestEtlRwExtensions, etl_array_size)
{
    EXPECT_NE(2, (lrpc::etl_array_size<etl::array<uint16_t, 3>>::value));
    EXPECT_EQ(2, (lrpc::etl_array_size<etl::array<uint16_t, 2>>::value));
}

TEST(TestEtlRwExtensions, etl_string_size)
{
    EXPECT_NE(2, (lrpc::etl_string_size<etl::string<3>>::value));
    EXPECT_EQ(2, (lrpc::etl_string_size<etl::string<2>>::value));
}

TEST(TestEtlRwExtensions, readArithmetic)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02, 0x03, 0x04, 0x79, 0xE9, 0xF6, 0x42};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_FALSE(lrpc::read_unchecked<bool>(reader));
    EXPECT_TRUE(lrpc::read_unchecked<bool>(reader));
    EXPECT_EQ(0x02, lrpc::read_unchecked<uint8_t>(reader));
    EXPECT_EQ(0x0403, lrpc::read_unchecked<uint16_t>(reader));
    EXPECT_FLOAT_EQ(123.456, lrpc::read_unchecked<float>(reader));
}

TEST(TestEtlRwExtensions, readAutoString)
{
    etl::vector<uint8_t, 10> storage{'T', 'e', 's', 't', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("Test", lrpc::read_unchecked<etl::string_view>(reader));
}

TEST(TestEtlRwExtensions, readFixedSizeString)
{
    etl::vector<uint8_t, 10> storage{'T', 'e', 's', 't', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("Tes", lrpc::read_unchecked<etl::string<3>>(reader));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<etl::string<4>>(reader));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<etl::string<5>>(reader));
}

TEST(TestEtlRwExtensions, readOptional)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto o1 = lrpc::read_unchecked<etl::optional<int>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<uint8_t>>(reader);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ(0x02, o2.value());
}

TEST(TestEtlRwExtensions, readArray)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto a = lrpc::read_unchecked<etl::array<uint8_t, 3>>(reader);
    ASSERT_EQ(3, a.size());
    EXPECT_EQ(0x00, a.at(0));
    EXPECT_EQ(0x01, a.at(1));
    EXPECT_EQ(0x02, a.at(2));
}

TEST(TestEtlRwExtensions, readArrayOfString)
{
    etl::vector<uint8_t, 10> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '\0', };
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto a = lrpc::read_unchecked<etl::array<etl::string<2>, 3>>(reader);
    ASSERT_EQ(3, a.size());
    EXPECT_EQ("t1", a.at(0));
    EXPECT_EQ("t2", a.at(1));
    EXPECT_EQ("t3", a.at(2));
}