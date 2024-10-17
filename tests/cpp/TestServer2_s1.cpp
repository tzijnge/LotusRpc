#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "generated/Server2/s01_ServiceShim.hpp"

using ::testing::Return;

MATCHER_P(SPAN_EQ, e, "Equality matcher for etl::span")
{
    if (e.size() != arg.size())
    {
        return false;
    }
    for (size_t i = 0; i < e.size(); ++i)
    {
        if (e[i] != arg[i])
        {
            return false;
        }
    }
    return true;
}

class MockS01Service : public s01ServiceShim
{
public:
    MOCK_METHOD(void, f0, (const etl::span<const etl::string_view> &p0), (override));
    MOCK_METHOD((etl::array<etl::string<2>, 2>), f1, (), (override));
    MOCK_METHOD(void, f2, (const etl::optional<etl::string_view> &p01), (override));
    MOCK_METHOD(void, f3, (const etl::optional<etl::string_view> &p01), (override));
    MOCK_METHOD((etl::optional<etl::string<2>>), f4, (), (override));
    MOCK_METHOD(void, f5, (const StringStruct &a), (override));
    MOCK_METHOD(StringStruct, f6, (), (override));
    MOCK_METHOD((etl::string<5>), f7, (const etl::string_view &p0), (override));
};

class TestServer2_s1 : public ::testing::Test
{
public:
    MockS01Service service;

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

// Decode void function with array of strings param
TEST_F(TestServer2_s1, decodeF0)
{
    using sv = etl::string_view;
    std::vector<sv> expected{sv("T1"), sv("T2")};
    EXPECT_CALL(service, f0(SPAN_EQ(expected)));
    auto response = receive({0, 'T', '1', '\0', 'T', '2', '\0'});
    EXPECT_RESPONSE({0}, response);
}

TEST_F(TestServer2_s1, decodeF0WithStringShorterThanMax)
{
    using sv = etl::string_view;
    std::vector<sv> expected{sv("1"), sv("2")};
    EXPECT_CALL(service, f0(SPAN_EQ(expected)));
    auto response = receive({0, '1', '\0', '2', '\0'});
    EXPECT_RESPONSE({0}, response);
}

// Decode function that returns array of strings
TEST_F(TestServer2_s1, decodeF1)
{
    etl::array<etl::string<2>, 2> retVal{"T1", "T2"};
    EXPECT_CALL(service, f1()).WillOnce(Return(retVal));
    auto response = receive({1});
    EXPECT_RESPONSE({1, 'T', '1', '\0', 'T', '2', '\0'}, response);
}

// Decode void function with optional fixed size string param
TEST_F(TestServer2_s1, decodeF2)
{
    using sv = etl::string_view;
    etl::optional<sv> expected{"T1"};
    EXPECT_CALL(service, f2(expected));
    auto response = receive({2, 0x01, 'T', '1', '\0'});
    EXPECT_RESPONSE({2}, response);
}

// Decode void function with optional auto string param
TEST_F(TestServer2_s1, decodeF3)
{
    using sv = etl::string_view;
    etl::optional<sv> expected{"T1"};
    EXPECT_CALL(service, f3(expected));
    auto response = receive({3, 0x01, 'T', '1', '\0'});
    EXPECT_RESPONSE({3}, response);
}

// Decode function that returns optional string
TEST_F(TestServer2_s1, decodeF4)
{
    etl::optional<etl::string<2>> expected{"T1"};
    EXPECT_CALL(service, f4()).WillOnce(Return(expected));
    auto response = receive({4});
    EXPECT_RESPONSE({4, 0x01, 'T', '1', '\0'}, response);
}

// Decode function that takes custom struct argument
TEST_F(TestServer2_s1, decodeF5)
{
    StringStruct expected;
    expected.aa = "T1";
    expected.b = {"T2", "T3"};
    expected.c = "T4";
    EXPECT_CALL(service, f5(expected));
    auto response = receive({5, 'T', '1', '\0', 'T', '2', '\0', 'T', '3', '\0', 0x01, 'T', '4', '\0'});
    EXPECT_RESPONSE({5}, response);
}

// Decode function that returns custom struct
TEST_F(TestServer2_s1, decodeF6)
{
    StringStruct retVal;
    retVal.aa = "T1";
    retVal.b = {"T2", "T3"};
    retVal.c = "T4";
    EXPECT_CALL(service, f6()).WillOnce(Return(retVal));
    auto response = receive({6});
    EXPECT_RESPONSE({6, 'T', '1', '\0', 'T', '2', '\0', 'T', '3', '\0', 0x01, 'T', '4', '\0'}, response);
}

// Decode function that takes auto string argument and returns fixed size string
TEST_F(TestServer2_s1, decodeF7)
{
    etl::string<5> retVal{"T1234"};
    etl::string_view expected{"T0"};
    EXPECT_CALL(service, f7(expected)).WillOnce(Return(retVal));
    auto response = receive({7, 'T', '0', '\0'});
    EXPECT_RESPONSE({7, 'T', '1', '2', '3', '4', '\0'}, response);
}