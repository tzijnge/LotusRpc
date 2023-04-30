#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "generated/TestDecoder2/s00_DecoderShim.hpp"

using ::testing::Return;

class MockS00Decoder : public s00DecoderShim
{
public:
    MOCK_METHOD(void, f0, (bool p0, const etl::string_view &p1), (override));
    MOCK_METHOD(void, f1, (const etl::string_view &p0, bool p1), (override));
};

class TestDecoder2 : public ::testing::Test
{
public:
    MockS00Decoder decoder;

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

// Decode void function with auto string as last param
TEST_F(TestDecoder2, decodeF0)
{
    EXPECT_CALL(decoder, f0(true, etl::string_view("Test")));
    auto response = decode({0, 0x01, 'T', 'e', 's', 't', '\0'});
    EXPECT_TRUE(response.empty());
}

// Decode void function with auto string as first param
TEST_F(TestDecoder2, decodeF1)
{
    EXPECT_CALL(decoder, f1(etl::string_view("Test"), true));
    auto response = decode({1, 'T', 'e', 's', 't', '\0', 0x01});
    EXPECT_TRUE(response.empty());
}