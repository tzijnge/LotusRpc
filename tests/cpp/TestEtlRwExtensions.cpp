#include <gtest/gtest.h>
#include "core/lrpccore/EtlRwExtensions.hpp"
#include <string>
#include <array>
#include <etl/vector.h>
#include <etl/string.h>

TEST(TestEtlRwExtensions, is_etl_optional)
{
    EXPECT_FALSE(lrpc::is_etl_optional<int>::value);
    EXPECT_TRUE(lrpc::is_etl_optional<etl::optional<int>>::value);
}

TEST(TestEtlRwExtensions, is_etl_string)
{
    EXPECT_FALSE(lrpc::is_string_n<int>::value);
    EXPECT_FALSE(lrpc::is_string_n<std::string>::value);
    EXPECT_FALSE(lrpc::is_string_n<etl::string_view>::value);
    EXPECT_FALSE(lrpc::is_string_n<etl::string_ext>::value);
    EXPECT_FALSE(lrpc::is_string_n<etl::string<10>>::value);
    EXPECT_TRUE(lrpc::is_string_n<lrpc::string_n>::value);
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

TEST(TestEtlRwExtensions, readArithmetic)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02, 0x03, 0x04, 0x79, 0xE9, 0xF6, 0x42};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_FALSE(lrpc::read_unchecked<bool>(reader));
    EXPECT_TRUE(lrpc::read_unchecked<bool>(reader));
    EXPECT_EQ(0x02, lrpc::read_unchecked<uint8_t>(reader));
    EXPECT_EQ(0x0403, lrpc::read_unchecked<uint16_t>(reader));
    EXPECT_FLOAT_EQ(123.456F, lrpc::read_unchecked<float>(reader));
}

TEST(TestEtlRwExtensions, readEnum)
{
    enum class Dummy
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

    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::string_auto>(reader));
}

TEST(TestEtlRwExtensions, readFixedSizeString)
{
    etl::vector<char, 10> storage{'T', 'e', 's', 't', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("Tes", lrpc::read_unchecked<lrpc::string_n>(reader, 3));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::string_n>(reader, 4));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::string_n>(reader, 5));
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

TEST(TestEtlRwExtensions, readOptionalAutoString)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto o1 = lrpc::read_unchecked<etl::optional<lrpc::string_auto>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<lrpc::string_auto>>(reader);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ("T1", o2.value());
}

TEST(TestEtlRwExtensions, readOptionalFixedSizeString)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto o1 = lrpc::read_unchecked<etl::optional<lrpc::string_n>>(reader, 2);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<lrpc::string_n>>(reader, 2);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ("T1", o2.value());
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

TEST(TestEtlRwExtensions, readArrayOfFixedSizeString)
{
    etl::vector<char, 10> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto a = lrpc::read_unchecked<etl::array<lrpc::string_n, 3>>(reader, 2);
    ASSERT_EQ(3, a.size());
    EXPECT_EQ("t1", a.at(0));
    EXPECT_EQ("t2", a.at(1));
    EXPECT_EQ("t3", a.at(2));
}

TEST(TestEtlRwExtensions, readArrayOfAutoString)
{
    etl::vector<char, 12> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '4', '5', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto a = lrpc::read_unchecked<etl::array<lrpc::string_auto, 3>>(reader);
    ASSERT_EQ(3, a.size());
    EXPECT_EQ("t1", a.at(0));
    EXPECT_EQ("t2", a.at(1));
    EXPECT_EQ("t345", a.at(2));
}

TEST(TestEtlRwExtensions, writeArithmetic)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    lrpc::write_unchecked<bool>(writer, false);
    lrpc::write_unchecked<bool>(writer, true);
    lrpc::write_unchecked<uint8_t>(writer, 0x02);
    lrpc::write_unchecked<uint16_t>(writer, 0x0403);
    lrpc::write_unchecked<float>(writer, 123.456F);

    const auto written = writer.used_data();
    ASSERT_EQ(9, written.size());
    EXPECT_EQ(0x00, static_cast<uint8_t>(written[0]));
    EXPECT_EQ(0x01, static_cast<uint8_t>(written[1]));
    EXPECT_EQ(0x02, static_cast<uint8_t>(written[2]));
    EXPECT_EQ(0x03, static_cast<uint8_t>(written[3]));
    EXPECT_EQ(0x04, static_cast<uint8_t>(written[4]));
    EXPECT_EQ(0x79, static_cast<uint8_t>(written[5]));
    EXPECT_EQ(0xE9, static_cast<uint8_t>(written[6]));
    EXPECT_EQ(0xF6, static_cast<uint8_t>(written[7]));
    EXPECT_EQ(0x42, static_cast<uint8_t>(written[8]));
}

TEST(TestEtlRwExtensions, writeEnum)
{
    enum class Dummy
    {
        V1 = 0xBB
    };

    etl::vector<uint8_t, 1> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    lrpc::write_unchecked<Dummy>(writer, Dummy::V1);
    const auto written = writer.used_data();
    ASSERT_EQ(1, written.size());
    EXPECT_EQ(0xBB, static_cast<uint8_t>(written[0]));
}

TEST(TestEtlRwExtensions, writeOptional)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    lrpc::write_unchecked<etl::optional<uint8_t>>(writer, {});
    lrpc::write_unchecked<etl::optional<uint8_t>>(writer, 0x02);

    const auto written = writer.used_data();
    ASSERT_EQ(3, written.size());
    EXPECT_EQ(0x00, static_cast<uint8_t>(written[0]));
    EXPECT_EQ(0x01, static_cast<uint8_t>(written[1]));
    EXPECT_EQ(0x02, static_cast<uint8_t>(written[2]));
}

TEST(TestEtlRwExtensions, writeString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    lrpc::write_unchecked<lrpc::string_n>(writer, "T1", 4);
    const etl::string_view t2("T2");
    lrpc::write_unchecked<lrpc::string_n>(writer, t2, 2);

    const auto written = writer.used_data();
    ASSERT_EQ(8, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('\0', written[3]);
    EXPECT_EQ('\0', written[4]);
    EXPECT_EQ('T', written[5]);
    EXPECT_EQ('2', written[6]);
    EXPECT_EQ('\0', written[7]);
}

TEST(TestEtlRwExtensions, writeAutoString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    lrpc::write_unchecked<lrpc::string_auto>(writer, "T1");
    const etl::string_view t2("T2");
    lrpc::write_unchecked<lrpc::string_auto>(writer, t2);

    const auto written = writer.used_data();
    ASSERT_EQ(6, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('T', written[3]);
    EXPECT_EQ('2', written[4]);
    EXPECT_EQ('\0', written[5]);
}

TEST(TestEtlRwExtensions, writeArray)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<uint8_t, 2> t2{0x01, 0x02};
    lrpc::write_unchecked<etl::array<uint8_t, 2>>(writer, t2);

    const auto written = writer.used_data();
    ASSERT_EQ(2, written.size());
    EXPECT_EQ(0x01, written[0]);
    EXPECT_EQ(0x02, written[1]);
}

TEST(TestEtlRwExtensions, writeArrayOfFixedSizeString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::string_view, 2> a{"T1", "T22"};
    lrpc::write_unchecked<etl::array<lrpc::string_n, 2>>(writer, a, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(8, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('\0', written[3]);
    EXPECT_EQ('T', written[4]);
    EXPECT_EQ('2', written[5]);
    EXPECT_EQ('2', written[6]);
    EXPECT_EQ('\0', written[7]);
}

TEST(TestEtlRwExtensions, writeArrayOfAutoString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::string_view, 2> a{"T1", "T1234"};
    lrpc::write_unchecked<etl::array<lrpc::string_auto, 2>>(writer, a);

    const auto written = writer.used_data();
    ASSERT_EQ(9, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('T', written[3]);
    EXPECT_EQ('1', written[4]);
    EXPECT_EQ('2', written[5]);
    EXPECT_EQ('3', written[6]);
    EXPECT_EQ('4', written[7]);
    EXPECT_EQ('\0', written[8]);
}

TEST(TestEtlRwExtensions, writeOptionalFixedSizeString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::optional<etl::string_view> a{"T1"};
    etl::optional<etl::string_view> b{};
    lrpc::write_unchecked<etl::optional<lrpc::string_n>>(writer, a, 3);
    lrpc::write_unchecked<etl::optional<lrpc::string_n>>(writer, b, 5);

    const auto written = writer.used_data();
    ASSERT_EQ(6, written.size());
    EXPECT_EQ(0x01, written[0]);
    EXPECT_EQ('T', written[1]);
    EXPECT_EQ('1', written[2]);
    EXPECT_EQ('\0', written[3]);
    EXPECT_EQ('\0', written[4]);
    EXPECT_EQ(0x00, written[5]);
}

TEST(TestEtlRwExtensions, writeOptionalAutoString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::optional<etl::string_view> a{"T1"};
    etl::optional<etl::string_view> b{};
    lrpc::write_unchecked<etl::optional<lrpc::string_auto>>(writer, a);
    lrpc::write_unchecked<etl::optional<lrpc::string_auto>>(writer, b);

    const auto written = writer.used_data();
    ASSERT_EQ(5, written.size());
    EXPECT_EQ(0x01, written[0]);
    EXPECT_EQ('T', written[1]);
    EXPECT_EQ('1', written[2]);
    EXPECT_EQ('\0', written[3]);
    EXPECT_EQ(0x00, written[4]);
}