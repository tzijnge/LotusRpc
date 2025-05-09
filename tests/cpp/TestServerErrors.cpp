#include "generated/Server3/Server3.hpp"
#include "TestUtils.hpp"
#include <sstream>

namespace
{
class S00Service : public srv3::s00ServiceShim
{
public:
    uint8_t f0(const uint8_t p1) override
    {
        return p1;
    }
};

class S01Service : public srv3::s01ServiceShim
{
public:
    uint16_t f0(const uint16_t p1) override
    {
        return p1;
    }
};

class TestServerErrors : public ::testing::Test, public srv3::Server3
{
public:
    TestServerErrors()
    {
        registerService(service00);
        // service 5 is intentionally not registered
    }

    void receive(const etl::string_view hex)
    {
        lrpcReceive(testutils::hexToBytes(hex));
    }

    void lrpcTransmit(const etl::span<const uint8_t> bytes) override
    {
        std::stringstream stream;
        for (const auto b : bytes)
        {
            stream << std::hex << std::setw(2) << std::uppercase << std::setfill('0') << static_cast<uint32_t>(b);
        }
        transmitted += stream.str();
    }

    std::string transmitted;
    S00Service service00;
    S01Service service01;
};
}

TEST_F(TestServerErrors, decodeUnknownServiceLessThanMaxServiceId)
{
    // Non-existing service 0x02 (smaller than MAX_SERVICE_ID), function ID 0xAB and no additional bytes
    receive("0302AB");
    EXPECT_EQ("14FF000000000000000000000000000000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnknownServiceGreaterThanMaxServiceId)
{
    // Non-existing service 0x77 (greater than MAX_SERVICE_ID), function ID 0 and two additional bytes
    receive("0577000000");
    EXPECT_EQ("14FF000000000000000000000000000000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnregistereredService)
{
    receive("050508CCDD");
    EXPECT_EQ("14FF000000000000000000000000000000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnknownFunction)
{
    // register service s01 (ID 5) and call non-existing function with ID 0xAB and two additional bytes
    registerService(service01);
    receive("0505ABCCDD");
    EXPECT_EQ("14FF000000000000000000000000000000000000", transmitted);
}
