#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "generated/TestDecoder2/s01_DecoderShim.hpp"

using ::testing::Return;

MATCHER_P(SPAN_EQ, e, "Equality matcher for etl::span")
{
    if (e.size() != arg.size())
    {
        return false;
    }
    for (auto i = 0; i < e.size(); ++i)
    {
        if (e[i] != arg[i])
        {
            return false;
        }
    }
    return true;

}

class MockS01Decoder : public s01DecoderShim
{
public:
    MOCK_METHOD(void, f0, (const etl::span<const etl::string_view> &p0), (override));
    MOCK_METHOD((etl::array<etl::string<2>, 2>), f1, (), (override));
    MOCK_METHOD(void, f2, (const etl::optional<etl::string_view> &p01), (override));
    MOCK_METHOD(void, f3, (const etl::optional<etl::string_view> &p01), (override));
    MOCK_METHOD((etl::optional<etl::string<2>>), f4, (), (override));
    MOCK_METHOD(void, f5, (const StringStruct &a), (override));
    MOCK_METHOD(StringStruct, f6, (), (override));
};

class TestDecoder2_s1 : public ::testing::Test
{
public:
    MockS01Decoder decoder;

    etl::span<uint8_t> decode(const std::vector<uint8_t> &bytes)
    {
        const etl::span<const uint8_t> s(bytes.begin(), bytes.end());

        Decoder::Reader reader(s.begin(), s.end(), etl::endian::little);
        Decoder::Writer writer(response.begin(), response.end(), etl::endian::little);
        decoder.decode(reader, writer);

        return { response.begin(), writer.size_bytes()};
    }

    void EXPECT_RESPONSE(const std::vector<uint8_t> &expected, const etl::span<uint8_t> actual)
    {
        std::vector<uint8_t> actualVec {actual.begin(), actual.end()};
        EXPECT_EQ(expected, actualVec);
    }

private:
    etl::array<uint8_t, 256> response;
};

// Decode void function with array of strings param
TEST_F(TestDecoder2_s1, decodeF0)
{
    using sv = etl::string_view;
    std::vector<sv> expected{sv("T1"), sv("T2")};
    EXPECT_CALL(decoder, f0(SPAN_EQ(expected)));
    auto response = decode({0, 'T', '1', '\0', 'T', '2', '\0'});
    EXPECT_TRUE(response.empty());
}

TEST_F(TestDecoder2_s1, decodeF0WithStringShorterThanMax)
{
    using sv = etl::string_view;
    std::vector<sv> expected{sv("1"), sv("2")};
    EXPECT_CALL(decoder, f0(SPAN_EQ(expected)));
    auto response = decode({0, '1', '\0', '2', '\0'});
    EXPECT_TRUE(response.empty());
}

// Decode function that returns array of strings
TEST_F(TestDecoder2_s1, decodeF1)
{
    etl::array<etl::string<2>, 2> retVal {"T1", "T2"};
    EXPECT_CALL(decoder, f1()).WillOnce(Return(retVal));
    auto response = decode({1});
    EXPECT_RESPONSE({'T', '1', '\0', 'T', '2', '\0'}, response);
}

// Decode void function with optional fixed size string param
TEST_F(TestDecoder2_s1, decodeF2)
{
    using sv = etl::string_view;
    etl::optional<sv> expected{"T1"};
    EXPECT_CALL(decoder, f2(expected));
    auto response = decode({2, 0x01, 'T', '1', '\0'});
    EXPECT_TRUE(response.empty());
}

// Decode void function with optional auto string param
TEST_F(TestDecoder2_s1, decodeF3)
{
    using sv = etl::string_view;
    etl::optional<sv> expected{"T1"};
    EXPECT_CALL(decoder, f3(expected));
    auto response = decode({3, 0x01, 'T', '1', '\0'});
    EXPECT_TRUE(response.empty());
}

// Decode function that returns optional string
TEST_F(TestDecoder2_s1, decodeF4)
{
    etl::optional<etl::string<2>> expected{"T1"};
    EXPECT_CALL(decoder, f4()).WillOnce(Return(expected));
    auto response = decode({4});
    EXPECT_RESPONSE({0x01, 'T', '1', '\0'}, response);
}

// Decode function that takes custom struct argument
TEST_F(TestDecoder2_s1, decodeF5)
{
    StringStruct expected;
    expected.aa = "T1";
    expected.b = {"T2", "T3"};
    expected.c = "T4";
    EXPECT_CALL(decoder, f5(expected));
    auto response = decode({5, 'T', '1', '\0', 'T', '2', '\0', 'T', '3', '\0', 0x01, 'T', '4', '\0'});
    EXPECT_TRUE(response.empty());
}

// Decode function that returns custom struct
TEST_F(TestDecoder2_s1, decodeF6)
{
    StringStruct retVal;
    retVal.aa = "T1";
    retVal.b = {"T2", "T3"};
    retVal.c = "T4";
    EXPECT_CALL(decoder, f6()).WillOnce(Return(retVal));
    auto response = decode({6});
    EXPECT_RESPONSE({'T', '1', '\0', 'T', '2', '\0', 'T', '3', '\0', 0x01, 'T', '4', '\0'}, response);
}