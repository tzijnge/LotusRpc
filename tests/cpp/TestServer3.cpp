#include "generated/Server3/Server3.hpp"
#include <sstream>
#include "TestUtils.hpp"

namespace
{
class S00Service : public srv3::s00ServiceShim
{
public:
    uint8_t f0(uint8_t p1) override
    {
        return p1;
    }
};

class S01Service : public srv3::s01ServiceShim
{
public:
    uint16_t f0(uint16_t p1) override
    {
        return p1;
    }
};

class TestServer3 : public ::testing::Test, public srv3::Server3
{
public:
    TestServer3()
    {
        registerService(service00);
        registerService(service01);
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

static_assert(std::is_same<srv3::Server3, lrpc::Server<6, 256, 256>>::value, "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer3, decodeI0)
{
    receive("040000AA");
    EXPECT_EQ("040000AA", transmitted);
}

TEST_F(TestServer3, decodeI0AndI5)
{
    receive("040000BB050508CCDD");
    EXPECT_EQ("040000BB050508CCDD", transmitted);
}