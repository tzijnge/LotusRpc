#include "generated/Server3/Server3.hpp"
#include "generated/Server3/s00_ServiceShim.hpp"
#include "generated/Server3/s01_ServiceShim.hpp"
#include <gmock/gmock.h>
#include <gtest/gtest.h>

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

    void receive(const std::vector<uint8_t> &bytes)
    {
        for (const auto &b : bytes)
        {
            lrpcReceive(b);
        }
    }

    void lrpcTransmit(etl::span<const uint8_t> bytes) override
    {
        transmitted.insert(transmitted.end(), bytes.begin(), bytes.end());
    }

    void EXPECT_VECTOR_EQ(const std::vector<uint8_t> &v1, const std::vector<uint8_t> &v2)
    {
        EXPECT_EQ(v1, v2);
    }

    std::vector<uint8_t> transmitted;
    s00Service service00;
    s01Service service01;
};

static_assert(std::is_same<srv3::Server3, lrpc::Server<6, 256, 256>>::value, "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer3, decodeI0)
{
    receive({0x04, 0x00, 0x00, 0xAA});
    EXPECT_VECTOR_EQ({0x04, 0x00, 0x00, 0xAA}, transmitted);
}

TEST_F(TestServer3, decodeI0AndI5)
{
    receive({0x04, 0x00, 0x00, 0xBB, 0x05, 0x05, 0x08, 0xCC, 0xDD});
    EXPECT_VECTOR_EQ({0x04, 0x00, 0x00, 0xBB, 0x05, 0x05, 0x08, 0xCC, 0xDD}, transmitted);
}