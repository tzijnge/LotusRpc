#include "generated/Server5/Server5.hpp"
#include "TestUtils.hpp"

namespace ts5
{
    class Mockservice : public srv0ServiceShim
    {
    public:
        MOCK_METHOD(void, s0, (uint16_t, uint8_t), (override));
        MOCK_METHOD(void, s1, (bool, DoorState), (override));
    };
}

using TestServer5 = testutils::TestServerBase<Server5, ts5::Mockservice>;

static_assert(std::is_same<Server5, lrpc::Server<0>>::value, "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer5, decodeS0)
{
    EXPECT_CALL(service, s0(0x1234, 0x56));

    const auto response = receive("060000341256");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5, s0_requestStop)
{
    service.s0_requestStop();
    EXPECT_EQ("030000", response());
}

TEST_F(TestServer5, decodeS1)
{
    EXPECT_CALL(service, s1(true, DoorState::Closed));

    const auto response = receive("0500370101");
    EXPECT_EQ("", response);
}

TEST_F(TestServer5, s1_requestStop)
{
    service.s1_requestStop();
    EXPECT_EQ("030037", response());
}