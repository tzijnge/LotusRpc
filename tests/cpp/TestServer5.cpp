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
        MOCK_METHOD(void, s0_requestStop, (), (override));
        MOCK_METHOD(void, s1_requestStop, (), (override));
    };

    class MockService2 : public srv2ServiceShim
    {
    public:
        MOCK_METHOD(void, s0, (DoorState), (override));
        MOCK_METHOD(void, s1_requestStop, (), (override));
        MOCK_METHOD(void, f0, (DoorState), (override));
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

TEST_F(TestServer5Srv1, decodeS0_requestStop)
{
    EXPECT_CALL(service, s0_requestStop());

    const auto response = receive("034200");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, s0_response)
{
    service.s0_response(0x1234, 0x56);
    EXPECT_EQ("064200341256", response());
}

TEST_F(TestServer5Srv1, decodeS1_requestStop)
{
    EXPECT_CALL(service, s1_requestStop());

    const auto response = receive("034221");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, s1_response)
{
    service.s1_response(true, DoorState::Open);
    EXPECT_EQ("0542210100", response());
}

TEST_F(TestServer5Srv2, decodeS0)
{
    EXPECT_CALL(service, s0(DoorState::Open));

    const auto response = receive("04430000");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, s0_requestStop)
{
    service.s0_requestStop();
    EXPECT_EQ("034300", response());
}

TEST_F(TestServer5Srv2, decodeS1_requestStop)
{
    EXPECT_CALL(service, s1_requestStop());

    const auto response = receive("034301");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, s1_response)
{
    service.s1_response(DoorState::Closed);
    EXPECT_EQ("04430101", response());
}

TEST_F(TestServer5Srv2, decodeF0)
{
    EXPECT_CALL(service, f0(DoorState::Closed));

    const auto response = receive("04430201");
    EXPECT_EQ("034302", response);
}