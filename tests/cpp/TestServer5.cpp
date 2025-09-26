#include "generated/Server5/Server5.hpp"
#include "TestUtils.hpp"

namespace ts5
{
    class MockService0 : public srv0ServiceShim
    {
    public:
        MOCK_METHOD(void, client_infinite, (uint16_t, uint8_t), (override));
        MOCK_METHOD(void, client_finite, (bool, DoorState, bool), (override));
    };

    class MockService1 : public srv1ServiceShim
    {
    public:
        MOCK_METHOD(void, server_infinite, (), (override));
        MOCK_METHOD(void, server_infinite_stop, (), (override));
        MOCK_METHOD(void, server_finite, (), (override));
        MOCK_METHOD(void, server_finite_stop, (), (override));
    };

    class MockService2 : public srv2ServiceShim
    {
    public:
        MOCK_METHOD(void, client_infinite, (DoorState), (override));
        MOCK_METHOD(void, server_infinite, (), (override));
        MOCK_METHOD(void, server_infinite_stop, (), (override));
        MOCK_METHOD(void, f0, (DoorState), (override));
    };
}

using TestServer5Srv0 = testutils::TestServerBase<Server5, ts5::MockService0>;
using TestServer5Srv1 = testutils::TestServerBase<Server5, ts5::MockService1>;
using TestServer5Srv2 = testutils::TestServerBase<Server5, ts5::MockService2>;

static_assert(std::is_same<Server5, lrpc::Server<67>>::value, "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer5Srv0, client_infinite)
{
    EXPECT_CALL(service, client_infinite(0x1234, 0x56));

    const auto response = receive("060000341256");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv0, client_infinite_requestStop)
{
    service.client_infinite_requestStop();
    EXPECT_EQ("030000", response());
}

TEST_F(TestServer5Srv0, client_finite)
{
    EXPECT_CALL(service, client_finite(true, DoorState::Closed, false));

    const auto response = receive("07003701010000");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv0, client_finite_requestStop)
{
    service.client_finite_requestStop();
    EXPECT_EQ("030037", response());
}

TEST_F(TestServer5Srv1, server_infinite_stop)
{
    EXPECT_CALL(service, server_infinite_stop());

    const auto response = receive("04420000");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_infinite)
{
    EXPECT_CALL(service, server_infinite());

    const auto response = receive("04420001");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_infinite_response)
{
    service.server_infinite_response(0x1234, 0x56);
    EXPECT_EQ("064200341256", response());
}

TEST_F(TestServer5Srv1, server_finite)
{
    EXPECT_CALL(service, server_finite());

    const auto response = receive("04422101");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_finite_stop)
{
    EXPECT_CALL(service, server_finite_stop());

    const auto response = receive("04422100");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_finite_response)
{
    service.server_finite_response(true, DoorState::Open, true);
    EXPECT_EQ("064221010001", response());
}

TEST_F(TestServer5Srv2, client_infinite)
{
    EXPECT_CALL(service, client_infinite(DoorState::Open));

    const auto response = receive("04430000");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, client_infinite_requestStop)
{
    service.client_infinite_requestStop();
    EXPECT_EQ("034300", response());
}

TEST_F(TestServer5Srv2, server_infinite)
{
    EXPECT_CALL(service, server_infinite());

    const auto response = receive("04430101");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, server_infinite_stop)
{
    EXPECT_CALL(service, server_infinite_stop());

    const auto response = receive("04430100");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, server_infinite_response)
{
    service.server_infinite_response(DoorState::Closed, Color::Magenta);
    EXPECT_EQ("0543010102", response());
}

TEST_F(TestServer5Srv2, decodeF0)
{
    EXPECT_CALL(service, f0(DoorState::Closed));

    const auto response = receive("04430201");
    EXPECT_EQ("034302", response);
}