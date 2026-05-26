#include <cstdint>
#include <type_traits>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "TestUtils.hpp"
#include "generated/Server5/Server5.hpp"

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServer5Srv0 : public srv5::srv0_shim
{
public:
    MOCK_METHOD(void, client_infinite, (uint16_t, uint8_t), (override));
    MOCK_METHOD(void, client_finite, (bool, srv5::DoorState, bool), (override));
};

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServer5Srv1 : public srv5::srv1_shim
{
public:
    MOCK_METHOD(void, server_infinite, (), (override));
    MOCK_METHOD(void, server_infinite_stop, (), (override));
    MOCK_METHOD(void, server_finite, (), (override));
    MOCK_METHOD(void, server_finite_stop, (), (override));
};

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServer5Srv2 : public srv5::srv2_shim
{
public:
    MOCK_METHOD(void, client_infinite, (srv5::DoorState), (override));
    MOCK_METHOD(void, server_infinite, (), (override));
    MOCK_METHOD(void, server_infinite_stop, (), (override));
    MOCK_METHOD(void, f0, (srv5::DoorState), (override));
};

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServer5Srv3 : public srv5::srv3_shim
{
public:
    MOCK_METHOD(void, client_infinite, (lrpc::span<const uint8_t>, lrpc::span<const lrpc::string_view>), (override));
    MOCK_METHOD(void, client_finite, (lrpc::span<const uint8_t>, lrpc::span<const lrpc::string_view>, bool),
                (override));
    MOCK_METHOD(void, server_infinite, (), (override));
    MOCK_METHOD(void, server_infinite_stop, (), (override));
    MOCK_METHOD(void, server_finite, (), (override));
    MOCK_METHOD(void, server_finite_stop, (), (override));
};

using TestServer5Srv0 = testutils::TestServerBase<srv5::Server5, MockServer5Srv0>;
using TestServer5Srv1 = testutils::TestServerBase<srv5::Server5, MockServer5Srv1>;
using TestServer5Srv2 = testutils::TestServerBase<srv5::Server5, MockServer5Srv2>;

static_assert(std::is_same<srv5::Server5, lrpc::Server<68, srv5::LrpcMeta_service, 256, 256>>::value,
              "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer5Srv0, client_infinite)
{
    EXPECT_CALL(service, client_infinite(0x1234, 0x56));

    const auto response = receive("050000341256");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv0, client_infinite_requestStop)
{
    service.client_infinite_requestStop();
    EXPECT_EQ("020000", response());
}

TEST_F(TestServer5Srv0, client_finite)
{
    EXPECT_CALL(service, client_finite(true, srv5::DoorState::Closed, false));

    const auto response = receive("06003701010000");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv0, client_finite_requestStop)
{
    service.client_finite_requestStop();
    EXPECT_EQ("020037", response());
}

TEST_F(TestServer5Srv1, server_infinite_stop)
{
    EXPECT_CALL(service, server_infinite_stop());

    const auto response = receive("03420000");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_infinite)
{
    EXPECT_CALL(service, server_infinite());

    const auto response = receive("03420001");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_infinite_response)
{
    service.server_infinite_response(0x1234, 0x56);
    EXPECT_EQ("054200341256", response());
}

TEST_F(TestServer5Srv1, server_finite)
{
    EXPECT_CALL(service, server_finite());

    const auto response = receive("03422101");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_finite_stop)
{
    EXPECT_CALL(service, server_finite_stop());

    const auto response = receive("03422100");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv1, server_finite_response)
{
    service.server_finite_response(true, srv5::DoorState::Open, true);
    EXPECT_EQ("054221010001", response());
}

TEST_F(TestServer5Srv2, client_infinite)
{
    EXPECT_CALL(service, client_infinite(srv5::DoorState::Open));

    const auto response = receive("03430000");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, client_infinite_requestStop)
{
    service.client_infinite_requestStop();
    EXPECT_EQ("024300", response());
}

TEST_F(TestServer5Srv2, server_infinite)
{
    EXPECT_CALL(service, server_infinite());

    const auto response = receive("03430101");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, server_infinite_stop)
{
    EXPECT_CALL(service, server_infinite_stop());

    const auto response = receive("03430100");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5Srv2, server_infinite_response)
{
    service.server_infinite_response(srv5::DoorState::Closed, srv5::Color::Magenta);
    EXPECT_EQ("0443010102", response());
}

TEST_F(TestServer5Srv2, decodeF0)
{
    EXPECT_CALL(service, f0(srv5::DoorState::Closed));

    const auto response = receive("03430201");
    EXPECT_EQ("024302", response);
}