#include "generated/Server2/s00_ServiceShim.hpp"
#include "generated/Server2/Server2.hpp"
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <etl/to_arithmetic.h>

using ::testing::Return;

class MockS00Service : public s00ServiceShim
{
public:
    MOCK_METHOD(void, f0, (bool p0, const etl::string_view &p1), (override));
    MOCK_METHOD(void, f1, (const etl::string_view &p0, bool p1), (override));
    MOCK_METHOD(void, f2, (const etl::string_view &p0, const etl::string_view &p1), (override));
};

class TestServer2 : public ::testing::Test
{
public:
    MockS00Service service;

    std::vector<uint8_t> hexToBytes(etl::string_view hex)
    {
        if (hex.size() % 2 != 0)
        {
            return {};
        }

        const auto numberBytes = hex.size() / 2;

        std::vector<uint8_t> bytes;

        for (auto i = 0U; i < numberBytes; i += 1)
        {
            bytes.emplace_back(etl::to_arithmetic<uint8_t>(hex.substr(i * 2, 2), etl::hex));
        }

        return bytes;
    }

    void SetUp() override
    {
        responseBuffer.fill(0xAA);
    }

    etl::span<uint8_t> receive(const etl::string_view hex)
    {
        return receive(hexToBytes(hex));
    }

    etl::span<uint8_t> receive(const std::vector<uint8_t> &bytes)
    {
        const etl::span<const uint8_t> s(bytes.begin(), bytes.end());

        lrpc::Service::Reader reader(s.begin(), s.end(), etl::endian::little);
        lrpc::Service::Writer writer(responseBuffer.begin(), responseBuffer.end(), etl::endian::little);
        service.invoke(reader, writer);

        return {responseBuffer.begin(), writer.size_bytes()};
    }

    void EXPECT_RESPONSE(const etl::string_view expected, const etl::span<uint8_t> actual)
    {
        std::vector<uint8_t> actualVec{actual.begin(), actual.end()};
        EXPECT_EQ(hexToBytes(expected), actualVec);
    }

private:
    etl::array<uint8_t, 256> responseBuffer;
};

static_assert(std::is_same<Server2, lrpc::Server<1, 100, 256>>::value, "RX and/or TX buffer size are unequal to the definition file");

// Decode void function with auto string as last param
TEST_F(TestServer2, decodeF0)
{
    EXPECT_CALL(service, f0(true, etl::string_view("Test")));
    auto response = receive("00015465737400");
    EXPECT_RESPONSE("0000", response);
}

// Decode void function with auto string as first param
TEST_F(TestServer2, decodeF1)
{
    EXPECT_CALL(service, f1(etl::string_view("Test"), true));
    auto response = receive("01546573740001");
    EXPECT_RESPONSE("0001", response);
}

// Decode void function with two auto string params
TEST_F(TestServer2, decodeF2)
{
    using sv = etl::string_view;
    EXPECT_CALL(service, f2(sv("T1"), sv("T2")));
    auto response = receive("02543100543200");
    EXPECT_RESPONSE("0002", response);
}