#include "generated/Server2/Server2.hpp"
#include "TestUtils.hpp"

using ::testing::Return;

class MockS00Service : public s00ServiceShim
{
public:
    MOCK_METHOD(void, f0, (bool p0, const etl::string_view &p1), (override));
    MOCK_METHOD(void, f1, (const etl::string_view &p0, bool p1), (override));
    MOCK_METHOD(void, f2, (const etl::string_view &p0, const etl::string_view &p1), (override));
};

using TestServer2 = testutils::TestServerBase<MockS00Service>;

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