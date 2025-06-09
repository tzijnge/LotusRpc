#include "generated/Server5/Server5.hpp"
#include "TestUtils.hpp"

namespace ts5
{
    class MockService0 : public srv0ServiceShim
    {
    public:
        MOCK_METHOD(void, s0, (uint16_t, uint8_t), (override));
        MOCK_METHOD(void, s1, (bool, DoorState), (override));
    };

    class MockService1 : public srv1ServiceShim
    {
    public:
        MOCK_METHOD(void, s0, (), (override));
        MOCK_METHOD(void, f0, (), (override));
    };

    class MockService2 : public srv2ServiceShim
    {
    public:
        MOCK_METHOD(void, s0_requestStop, (), (override));
    };
}

using TestServer5Srv0 = testutils::TestServerBase<Server5, ts5::MockService0>;
using TestServer5Srv1 = testutils::TestServerBase<Server5, ts5::MockService1>;
using TestServer5Srv2 = testutils::TestServerBase<Server5, ts5::MockService2>;

static_assert(std::is_same<Server5, lrpc::Server<67>>::value, "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer5Srv0, decodeS0)
{
    EXPECT_CALL(service, s0(0x1234, 0x56));

    const auto response = receive("060000341256");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv0, s0_requestStop)
{
    service.s0_requestStop();
    EXPECT_EQ("030000", response());
}

TEST_F(TestServer5Srv0, decodeS1)
{
    EXPECT_CALL(service, s1(true, DoorState::Closed));

    const auto response = receive("0500370101");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv0, s1_requestStop)
{
    service.s1_requestStop();
    EXPECT_EQ("030037", response());
}

TEST_F(TestServer5Srv1, decodeS0)
{
    EXPECT_CALL(service, s0());

    const auto response = receive("034200");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, s0_requestStop)
{
    service.s0_requestStop();
    EXPECT_EQ("034200", response());
}

TEST_F(TestServer5Srv1, decodeF0)
{
    EXPECT_CALL(service, f0());

    const auto response = receive("034201");
    EXPECT_EQ("034201", response);
}

TEST_F(TestServer5Srv2, decodeS0_requestStop)
{
    EXPECT_CALL(service, s0_requestStop());

    const auto response = receive("034300");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, s0)
{
    service.s0(0x1234, 0x56);
    EXPECT_EQ("064300341256", response());
}