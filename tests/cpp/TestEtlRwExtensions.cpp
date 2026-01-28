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
    EXPECT_TRUE(lrpc::is_string_n<lrpc::tags::string_n>::value);
}

TEST(TestEtlRwExtensions, is_array_n)
{
    EXPECT_FALSE(lrpc::is_array_n<int>::value);
    EXPECT_FALSE((lrpc::is_array_n<std::array<int, 4>>::value));
    EXPECT_FALSE((lrpc::is_array_n<etl::array<int, 4>>::value));
    EXPECT_TRUE((lrpc::is_array_n<lrpc::tags::array_n<int>>::value));
}

TEST(TestEtlRwExtensions, etl_optional_type)
{
    EXPECT_TRUE((etl::is_same<uint16_t, lrpc::etl_optional_type<etl::optional<uint16_t>>::type>::value));
    EXPECT_FALSE((etl::is_same<uint16_t, lrpc::etl_optional_type<etl::optional<uint32_t>>::type>::value));
    EXPECT_TRUE((etl::is_same<lrpc::tags::string_auto, lrpc::etl_optional_type<etl::optional<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE((etl::is_same<lrpc::tags::string_n, lrpc::etl_optional_type<etl::optional<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE((etl::is_same<lrpc::tags::bytearray_auto, lrpc::etl_optional_type<etl::optional<lrpc::tags::bytearray_auto>>::type>::value));
}

TEST(TestEtlRwExtensions, etl_optional_pr_type)
{
    EXPECT_TRUE((etl::is_same<etl::optional<uint16_t>, lrpc::etl_optional_pr_type<etl::optional<uint16_t>>::type>::value));
    EXPECT_FALSE((etl::is_same<etl::optional<uint16_t>, lrpc::etl_optional_pr_type<etl::optional<uint32_t>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::optional<etl::string_view>, lrpc::etl_optional_pr_type<etl::optional<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::optional<etl::string_view>, lrpc::etl_optional_pr_type<etl::optional<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::optional<lrpc::bytearray_t>, lrpc::etl_optional_pr_type<etl::optional<lrpc::tags::bytearray_auto>>::type>::value));
}

TEST(TestEtlRwExtensions, array_n_type)
{
    EXPECT_NE(typeid(uint16_t), typeid(lrpc::array_n_type<lrpc::tags::array_n<uint32_t>>::type));
    EXPECT_EQ(typeid(uint16_t), typeid(lrpc::array_n_type<lrpc::tags::array_n<uint16_t>>::type));
}

TEST(TestEtlRwExtensions, array_param_type)
{
    EXPECT_TRUE((etl::is_same<etl::span<const uint16_t>, lrpc::array_param_type<lrpc::tags::array_n<uint16_t>>::type>::value));
    EXPECT_FALSE((etl::is_same<etl::span<const uint16_t>, lrpc::array_param_type<lrpc::tags::array_n<uint32_t>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::span<const etl::string_view>, lrpc::array_param_type<lrpc::tags::array_n<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::span<const lrpc::tags::string_n>, lrpc::array_param_type<lrpc::tags::array_n<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::span<const lrpc::bytearray_t>, lrpc::array_param_type<lrpc::tags::array_n<lrpc::tags::bytearray_auto>>::type>::value));
}

TEST(TestEtlRwExtensions, array_out_param_type)
{
    EXPECT_TRUE((etl::is_same<etl::span<uint16_t>, lrpc::array_outparam_type<lrpc::tags::array_n<uint16_t>>::type>::value));
    EXPECT_FALSE((etl::is_same<etl::span<uint16_t>, lrpc::array_outparam_type<lrpc::tags::array_n<uint32_t>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::span<etl::string_view>, lrpc::array_outparam_type<lrpc::tags::array_n<lrpc::tags::string_auto>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::span<lrpc::tags::string_n>, lrpc::array_outparam_type<lrpc::tags::array_n<lrpc::tags::string_n>>::type>::value));
    EXPECT_TRUE((etl::is_same<etl::span<lrpc::bytearray_t>, lrpc::array_outparam_type<lrpc::tags::array_n<lrpc::tags::bytearray_auto>>::type>::value));
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

    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::tags::string_auto>(reader));
}

TEST(TestEtlRwExtensions, readFixedSizeString)
{
    etl::vector<char, 10> storage{'T', 'e', 's', 't', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    EXPECT_EQ("Tes", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 3));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 4));
    reader.restart();
    EXPECT_EQ("Test", lrpc::read_unchecked<lrpc::tags::string_n>(reader, 5));
}

TEST(TestEtlRwExtensions, readOptional)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x02};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<etl::optional<uint8_t>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<uint8_t>>(reader);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ(0x02, o2.value());
}

TEST(TestEtlRwExtensions, readOptionalAutoString)
{
    etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<etl::optional<lrpc::tags::string_auto>>(reader);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<lrpc::tags::string_auto>>(reader);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ("T1", o2.value());
}

TEST(TestEtlRwExtensions, readOptionalFixedSizeString)
{
    const etl::vector<uint8_t, 10> storage{0x00, 0x01, 'T', '1', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<etl::optional<lrpc::tags::string_n>>(reader, 2);
    EXPECT_FALSE(o1.has_value());
    auto o2 = lrpc::read_unchecked<etl::optional<lrpc::tags::string_n>>(reader, 2);
    EXPECT_TRUE(o2.has_value());
    EXPECT_EQ("T1", o2.value());
}

TEST(TestEtlRwExtensions, readOptionalBytearray)
{
    const etl::vector<uint8_t, 10> storage{0x00, 0x01, 0x03, 0x11, 0x22, 0x33};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    const auto o1 = lrpc::read_unchecked<etl::optional<lrpc::tags::bytearray_auto>>(reader);
    EXPECT_FALSE(o1.has_value());
    const auto o2 = lrpc::read_unchecked<etl::optional<lrpc::tags::bytearray_auto>>(reader);
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

    etl::array<etl::span<const uint8_t>, 2> a1;
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

    etl::array<uint8_t, 4> dest{0xFF, 0xFF, 0xFF, 0xFF};
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

    // Read of array size 3 is requested, but storage is only 2
    etl::array<uint8_t, 2> dest{0xFF, 0xFF};
    lrpc::read_unchecked<lrpc::tags::array_n<uint8_t>>(reader, dest, 3);
    EXPECT_EQ(0x00, dest.at(0));
    EXPECT_EQ(0x01, dest.at(1));
    EXPECT_EQ(0xAB, lrpc::read_unchecked<uint8_t>(reader));
}

TEST(TestEtlRwExtensions, readArrayOfFixedSizeString)
{
    etl::vector<char, 10> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::string_view, 4> dest{"o1", "o2", "o3", "o4"};
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

    // Read of array size 3 is requested, but storage is only 2
    etl::array<etl::string_view, 2> dest{"o1", "o2"};
    lrpc::read_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(reader, dest, 3, 2);
    EXPECT_EQ("t1", dest.at(0));
    EXPECT_EQ("t2", dest.at(1));
    EXPECT_EQ(0xAB, lrpc::read_unchecked<uint8_t>(reader));
}

TEST(TestEtlRwExtensions, readArrayOfAutoString)
{
    etl::vector<char, 12> storage{'t', '1', '\0', 't', '2', '\0', 't', '3', '4', '5', '\0'};
    etl::byte_stream_reader reader(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::string_view, 4> dest{"o1", "o2", "o3", "o4"};
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

    // Read of array size 3 is requested, but storage is only 2
    etl::array<etl::string_view, 2> dest{"o1", "o2"};
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

    lrpc::write_unchecked<lrpc::tags::string_n>(writer, "T1", 4);
    const etl::string_view t2("T2");
    lrpc::write_unchecked<lrpc::tags::string_n>(writer, t2, 2);

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

    lrpc::write_unchecked<lrpc::tags::string_auto>(writer, "T1");
    const etl::string_view t2("T2");
    lrpc::write_unchecked<lrpc::tags::string_auto>(writer, t2);

    const auto written = writer.used_data();
    ASSERT_EQ(6, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('T', written[3]);
    EXPECT_EQ('2', written[4]);
    EXPECT_EQ('\0', written[5]);
}

TEST(TestEtlRwExtensions, writeByteArray)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    const etl::array<uint8_t, 3> a{0x11, 0x12, 0x13};
    const etl::array<uint8_t, 2> b{0x14, 0x15};
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, a);
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, b);
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, {});
    // overflows the storage
    lrpc::write_unchecked<lrpc::tags::bytearray_auto>(writer, b);

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

TEST(TestEtlRwExtensions, writeArray)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<uint8_t, 3> t2{0x01, 0x02, 0x03};
    lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, t2, 2);

    const auto written = writer.used_data();
    ASSERT_EQ(2, written.size());
    EXPECT_EQ(0x01, written[0]);
    EXPECT_EQ(0x02, written[1]);
}

TEST(TestEtlRwExtensions, writeArrayFromInsufficientStorage)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    // request to write 3, but only 2 available. Fill remaining with default values
    etl::array<uint8_t, 2> t2{0x01, 0x02};
    lrpc::write_unchecked<lrpc::tags::array_n<uint8_t>>(writer, t2, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(3, written.size());
    EXPECT_EQ(0x01, written[0]);
    EXPECT_EQ(0x02, written[1]);
    EXPECT_EQ(0x00, written[2]);
}

TEST(TestEtlRwExtensions, writeArrayOfFixedSizeString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::string_view, 2> a{"T1", "T22"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, a, 2, 3);

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

TEST(TestEtlRwExtensions, writeArrayOfFixedSizeStringFromInsufficientStorage)
{
    etl::array<uint8_t, 12> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    // request to write 3, but only 2 available. Fill remaining with default values
    etl::array<etl::string_view, 2> a{"T1", "T22"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_n>>(writer, a, 3, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(12, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('\0', written[3]);
    EXPECT_EQ('T', written[4]);
    EXPECT_EQ('2', written[5]);
    EXPECT_EQ('2', written[6]);
    EXPECT_EQ('\0', written[7]);
    EXPECT_EQ('\0', written[8]);
    EXPECT_EQ('\0', written[9]);
    EXPECT_EQ('\0', written[10]);
    EXPECT_EQ('\0', written[11]);
}

TEST(TestEtlRwExtensions, writeArrayOfAutoString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::string_view, 2> a{"T1", "T1234"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_auto>>(writer, a, 2);

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

TEST(TestEtlRwExtensions, writeArrayOfAutoStringFromInsufficientStorage)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    // request to write 3, but only 2 available. Fill remaining with default values
    etl::array<etl::string_view, 2> a{"T1", "T1234"};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::string_auto>>(writer, a, 3);

    const auto written = writer.used_data();
    ASSERT_EQ(10, written.size());
    EXPECT_EQ('T', written[0]);
    EXPECT_EQ('1', written[1]);
    EXPECT_EQ('\0', written[2]);
    EXPECT_EQ('T', written[3]);
    EXPECT_EQ('1', written[4]);
    EXPECT_EQ('2', written[5]);
    EXPECT_EQ('3', written[6]);
    EXPECT_EQ('4', written[7]);
    EXPECT_EQ('\0', written[8]);
    EXPECT_EQ('\0', written[9]);
}

TEST(TestEtlRwExtensions, writeOptionalFixedSizeString)
{
    etl::array<uint8_t, 10> storage;
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    const etl::optional<etl::string_view> a{"T1"};
    const etl::optional<etl::string_view> b{};
    lrpc::write_unchecked<etl::optional<lrpc::tags::string_n>>(writer, a, 3);
    lrpc::write_unchecked<etl::optional<lrpc::tags::string_n>>(writer, b, 5);

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

    const etl::optional<etl::string_view> a{"T1"};
    const etl::optional<etl::string_view> b{};
    lrpc::write_unchecked<etl::optional<lrpc::tags::string_auto>>(writer, a);
    lrpc::write_unchecked<etl::optional<lrpc::tags::string_auto>>(writer, b);

    const auto written = writer.used_data();
    ASSERT_EQ(5, written.size());
    EXPECT_EQ(0x01, written[0]);
    EXPECT_EQ('T', written[1]);
    EXPECT_EQ('1', written[2]);
    EXPECT_EQ('\0', written[3]);
    EXPECT_EQ(0x00, written[4]);
}

TEST(TestEtlRwExtensions, writeOptionalBytearray)
{
    etl::array<uint8_t, 10> storage;
    const etl::array<uint8_t, 2> o1{0x11, 0x22};
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    lrpc::write_unchecked<etl::optional<lrpc::tags::bytearray_auto>>(writer, {});
    lrpc::write_unchecked<etl::optional<lrpc::tags::bytearray_auto>>(writer, etl::span<const uint8_t>{});
    lrpc::write_unchecked<etl::optional<lrpc::tags::bytearray_auto>>(writer, etl::span<const uint8_t>{o1});

    const auto written = writer.used_data();
    ASSERT_EQ(7, written.size());
    // optional without value
    EXPECT_EQ(0x00, written[0]);
    // optional with empty bytearray
    EXPECT_EQ(0x01, written[1]);
    EXPECT_EQ(0x00, written[2]);
    // optional with o1
    EXPECT_EQ(0x01, written[3]);
    EXPECT_EQ(0x02, written[4]);
    EXPECT_EQ(0x11, written[5]);
    EXPECT_EQ(0x22, written[6]);
}

TEST(TestEtlRwExtensions, writeArrayOfBytearray)
{
    etl::array<uint8_t, 10> storage;
    const etl::array<uint8_t, 2> ba1{0x11, 0x22};
    const etl::array<uint8_t, 3> ba2{0x33, 0x44, 0x55};
    etl::byte_stream_writer writer(storage.begin(), storage.end(), etl::endian::little);

    etl::array<etl::span<const uint8_t>, 2> baArray{ba1, ba2};
    lrpc::write_unchecked<lrpc::tags::array_n<lrpc::tags::bytearray_auto>>(writer, baArray, 2);

    const auto written = writer.used_data();
    ASSERT_EQ(7, written.size());
    EXPECT_EQ(0x02, written[0]);
    EXPECT_EQ(0x11, written[1]);
    EXPECT_EQ(0x22, written[2]);
    EXPECT_EQ(0x03, written[3]);
    EXPECT_EQ(0x33, written[4]);
    EXPECT_EQ(0x44, written[5]);
    EXPECT_EQ(0x55, written[6]);
}