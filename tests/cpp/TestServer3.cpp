#include "generated/Server3/Server3.hpp"
#include <sstream>
#include "TestServerBase.hpp"

class s00Service : public srv3::s00ServiceShim
{
public:
    uint8_t f0(uint8_t p1) override
    {
        return p1;
    }
};

class s01Service : public srv3::s01ServiceShim
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
        lrpcReceive(hexToBytes(hex));
    }

    void lrpcTransmit(etl::span<const uint8_t> bytes) override
    {
        std::stringstream stream;
        for (const auto b : bytes)
        {
            stream << std::hex << std::setw(2) << std::uppercase << std::setfill('0') << static_cast<int>(b);
        }
        transmitted += stream.str();
    }

    void EXPECT_VECTOR_EQ(const std::string &v1, const std::string &v2)
    {
        EXPECT_EQ(v1, v2);
    }

    std::string transmitted;

    s00Service service00;
    s01Service service01;
};

static_assert(std::is_same<srv3::Server3, lrpc::Server<6, 256, 256>>::value, "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer3, decodeI0)
{
    receive("040000AA");
    EXPECT_VECTOR_EQ("040000AA", transmitted);
}

TEST_F(TestServer3, decodeI0AndI5)
{
    receive("040000BB050508CCDD");
    EXPECT_VECTOR_EQ("040000BB050508CCDD", transmitted);
}