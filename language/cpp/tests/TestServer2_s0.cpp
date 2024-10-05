#include "generated/Server2/s00_ServiceShim.hpp"
#include "generated/Server2/Server2.hpp"
#include <gmock/gmock.h>
#include <gtest/gtest.h>

using ::testing::Return;

class MockS00Service : public s00ServiceShim
{
public:
    MOCK_METHOD(void, f0, (bool p0, const etl::string_view &p1), (override));
    MOCK_METHOD(void, f1, (const etl::string_view &p0, bool p1), (override));
};

class TestServer2 : public ::testing::Test
{
public:
    MockS00Service service;

    etl::span<uint8_t> receive(const std::vector<uint8_t> &bytes)
    {
        const etl::span<const uint8_t> s(bytes.begin(), bytes.end());

        lrpc::Service::Reader reader(s.begin(), s.end(), etl::endian::little);
        lrpc::Service::Writer writer(responseBuffer.begin(), responseBuffer.end(), etl::endian::little);
        service.invoke(reader, writer);

        return {responseBuffer.begin(), writer.size_bytes()};
    }

    void EXPECT_RESPONSE(const std::vector<uint8_t> &expected, const etl::span<uint8_t> actual)
    {
        std::vector<uint8_t> actualVec{actual.begin(), actual.end()};
        EXPECT_EQ(expected, actualVec);
    }

private:
    etl::array<uint8_t, 256> responseBuffer;
};

static_assert(std::is_same<Server2, lrpc::Server<1, 100, 256>>::value, "RX and/or TX buffer size are unequal to the definition file");

// Decode void function with auto string as last param
TEST_F(TestServer2, decodeF0)
{
    EXPECT_CALL(service, f0(true, etl::string_view("Test")));
    auto response = receive({0, 0x01, 'T', 'e', 's', 't', '\0'});
    EXPECT_RESPONSE({0}, response);
}

// Decode void function with auto string as first param
TEST_F(TestServer2, decodeF1)
{
    EXPECT_CALL(service, f1(etl::string_view("Test"), true));
    auto response = receive({1, 'T', 'e', 's', 't', '\0', 0x01});
    EXPECT_RESPONSE({1}, response);
}