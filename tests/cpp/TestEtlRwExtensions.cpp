#include <gtest/gtest.h>
#include "lrpccore/EtlRwExtensions.hpp"
#include <string>
#include <array>
#include <etl/vector.h>

TEST(TestEtlRwExtensions, is_etl_optional)
{
    EXPECT_FALSE(lrpc::is_etl_optional<int>::value);
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

TEST(TestEtlRwExtensions, readOptionalAutoString)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto o1 = lrpc::read_unchecked<etl::optional<etl::string_view>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<etl::string_view>>(reader);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ("T1", o2.value());
}

TEST(TestEtlRwExtensions, readOptionalFixedSizeString)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    auto o1 = lrpc::read_unchecked<etl::optional<etl::string<2>>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<etl::string<2>>>(reader);
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

TEST(TestEtlRwExtensions, copyString)
{
    etl::string_view source{"test"};
    etl::string<4> dest4;
    lrpc::copy<etl::string<4>>(source, dest4);
    EXPECT_EQ("test", dest4);

    etl::string<2> dest2;
    lrpc::copy<etl::string<2>>(source, dest2);
    EXPECT_EQ("te", dest2);

    etl::string<6> dest6;
    lrpc::copy<etl::string<6>>(source, dest6);
    EXPECT_EQ("test", dest6);
}

TEST(TestEtlRwExtensions, copyArrayOfString)
{
    etl::array<etl::string_view, 2> source{"T1", "T2"};
    etl::array<etl::string<2>, 2> dest;
    lrpc::copy<etl::array<etl::string<2>, 2>>(source, dest);
    EXPECT_EQ("T1", dest[0]);
    EXPECT_EQ("T2", dest[1]);
}

TEST(TestEtlRwExtensions, copyOptionalString)
{
    etl::optional<etl::string_view> source1{"T1"};
    etl::optional<etl::string<2>> dest1;
    lrpc::copy<etl::optional<etl::string<2>>>(source1, dest1);
    ASSERT_TRUE(dest1.has_value());
    EXPECT_EQ("T1", dest1.value());

    etl::optional<etl::string<2>> dest2{"~~"};
    lrpc::copy<etl::optional<etl::string<2>>>(source1, dest2);
    ASSERT_TRUE(dest2.has_value());
    EXPECT_EQ("T1", dest2.value());

    etl::optional<etl::string_view> source2;
    lrpc::copy<etl::optional<etl::string<2>>>(source2, dest2);
    EXPECT_FALSE(dest2.has_value());
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

    lrpc::write_unchecked<etl::string<4>>(writer, "T1");
    const etl::string<2> t2("T2");
    lrpc::write_unchecked<etl::string<2>>(writer, t2);

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

    lrpc::write_unchecked<etl::string_view>(writer, "T1");
    const etl::string_view t2("T2");
    lrpc::write_unchecked<etl::string_view>(writer, t2);

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

TEST(TestEtlRwExtensions, writeArrayOfString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::string<2>, 2> a{"T1", "T2"};
    lrpc::write_unchecked<etl::array<etl::string<2>, 2>>(writer, a);

    const auto written = writer.used_data();
    ASSERT_EQ(6, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('T', written[3]);
    EXPECT_EQ('2', written[4]);
    EXPECT_EQ('\0', written[5]);
}

TEST(TestEtlRwExtensions, writeOptionalString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::optional<etl::string<2>> a{"T1"};
    etl::optional<etl::string<5>> b{};
    lrpc::write_unchecked<etl::optional<etl::string<2>>>(writer, a);
    lrpc::write_unchecked<etl::optional<etl::string<5>>>(writer, b);

    const auto written = writer.used_data();
    ASSERT_EQ(5, written.size());
    EXPECT_EQ(0x01, written[0]);
    EXPECT_EQ('T', written[1]);
    EXPECT_EQ('1', written[2]);
    EXPECT_EQ('\0', written[3]);
    EXPECT_EQ(0x00, written[4]);
}