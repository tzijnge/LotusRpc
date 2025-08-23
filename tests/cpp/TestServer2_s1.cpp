#include "generated/Server2/Server2.hpp"
#include "TestUtils.hpp"

using ::testing::Return;

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
    MOCK_METHOD(void, f8, (const etl::span<const etl::string_view> &p0), (override));
    MOCK_METHOD(void, f9, (const StringStruct2 &a), (override));
    MOCK_METHOD(StringStruct2, f10, (), (override));
};

using TestServer2_s1 = testutils::TestServerBase<Server2, MockS01Service>;

// Decode void function with array of strings param
TEST_F(TestServer2_s1, decodeF0)
{
    using sv = etl::string_view;
    std::vector<sv> expected{sv("T1"), sv("T2")};
    EXPECT_CALL(service, f0(testutils::SPAN_EQ(expected)));
    const auto response = receive("090100543100543200");
    EXPECT_EQ("030100", response);
}

TEST_F(TestServer2_s1, decodeF0WithStringShorterThanMax)
{
    using sv = etl::string_view;
    std::vector<sv> expected{sv("1"), sv("2")};
    EXPECT_CALL(service, f0(testutils::SPAN_EQ(expected)));
    const auto response = receive("07010031003200");
    EXPECT_EQ("030100", response);
}

// Decode function that returns array of strings
TEST_F(TestServer2_s1, decodeF1)
{
    etl::array<etl::string<2>, 2> retVal{"T1", "T2"};
    EXPECT_CALL(service, f1()).WillOnce(Return(retVal));
    const auto response = receive("030101");
    EXPECT_EQ("090101543100543200", response);
}

// Decode void function with optional fixed size string param
TEST_F(TestServer2_s1, decodeF2)
{
    using sv = etl::string_view;
    etl::optional<sv> expected{"T1"};
    EXPECT_CALL(service, f2(expected));
    const auto response = receive("07010201543100");
    EXPECT_EQ("030102", response);
}

// Decode void function with optional auto string param
TEST_F(TestServer2_s1, decodeF3)
{
    using sv = etl::string_view;
    etl::optional<sv> expected{"T1"};
    EXPECT_CALL(service, f3(expected));
    const auto response = receive("07010301543100");
    EXPECT_EQ("030103", response);
}

// Decode function that returns optional string
TEST_F(TestServer2_s1, decodeF4)
{
    etl::optional<etl::string<2>> expected{"T1"};
    EXPECT_CALL(service, f4()).WillOnce(Return(expected));
    const auto response = receive("030104");
    EXPECT_EQ("07010401543100", response);
}

// Decode function that takes custom struct argument
TEST_F(TestServer2_s1, decodeF5)
{
    StringStruct expected;
    expected.aa = "T1";
    expected.b = {"T2", "T3"};
    expected.c = "T4";

    EXPECT_CALL(service, f5(expected));
    const auto response = receive("10010554310054320054330001543400");
    EXPECT_EQ("030105", response);
}

// Decode function that returns custom struct
TEST_F(TestServer2_s1, decodeF6)
{
    StringStruct retVal;
    retVal.aa = "T1";
    retVal.b = {"T2", "T3"};
    retVal.c = "T4";

    EXPECT_CALL(service, f6()).WillOnce(Return(retVal));
    const auto response = receive("030106");
    EXPECT_EQ("10010654310054320054330001543400", response);
}

// Decode function that takes auto string argument and returns fixed size string
TEST_F(TestServer2_s1, decodeF7)
{
    etl::string<5> retVal{"T1234"};
    etl::string_view expected{"T0"};
    EXPECT_CALL(service, f7(expected)).WillOnce(Return(retVal));
    const auto response = receive("060107543000");
    EXPECT_EQ("090107543132333400", response);
}

// Decode void function with array of auto strings param
TEST_F(TestServer2_s1, decodeF8)
{
    using sv = etl::string_view;
    std::vector<sv> expected{sv("T1"), sv("T2")};
    EXPECT_CALL(service, f8(testutils::SPAN_EQ(expected)));
    const auto response = receive("090108543100543200");
    EXPECT_EQ("030108", response);
}

// Decode function that takes custom struct argument
TEST_F(TestServer2_s1, decodeF9)
{
    StringStruct2 expected;
    expected.aa = "T1";
    expected.b = {"T2", "T3"};
    expected.c = "T4";

    EXPECT_CALL(service, f9(expected));
    const auto response = receive("10010954310054320054330001543400");
    EXPECT_EQ("030109", response);
}

// Decode function that returns custom struct
TEST_F(TestServer2_s1, decodeF10)
{
    StringStruct2 retVal;
    retVal.aa = "T1";
    retVal.b = {"T2", "T3"};
    retVal.c = "T4";

    EXPECT_CALL(service, f10()).WillOnce(Return(retVal));
    const auto response = receive("03010A");
    EXPECT_EQ("10010A54310054320054330001543400", response);
}