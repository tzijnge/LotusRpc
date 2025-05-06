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

class TestServerErrors : public ::testing::Test, public srv3::Server3
{
public:
    TestServerErrors()
    {
        registerService(service00);
        // service 5 is intentionally not registered
    }

    void receive(const std::vector<uint8_t> &bytes)
    {
        lrpcReceive(bytes);
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


TEST_F(TestServerErrors, decodeUnknownServiceLessThanMaxServiceId)
{
    // Non-existing service 0x02 (smaller than MAX_SERVICE_ID), function ID 0xAB and no additional bytes
    receive({0x03, 0x02, 0xAB});
    EXPECT_VECTOR_EQ({0x14, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, transmitted);
}

TEST_F(TestServerErrors, decodeUnknownServiceGreaterThanMaxServiceId)
{
    // Non-existing service 0x77 (greater than MAX_SERVICE_ID), function ID 0 and two additional bytes
    receive({0x05, 0x77, 0x00, 0x00, 0x00});
    EXPECT_VECTOR_EQ({0x14, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, transmitted);
}

TEST_F(TestServerErrors, decodeUnregistereredService)
{
    receive({0x05, 0x05, 0x08, 0xCC, 0xDD});
    EXPECT_VECTOR_EQ({0x14, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, transmitted);
}

TEST_F(TestServerErrors, decodeUnknownFunction)
{
    // register service s01 (ID 5) and call non-existing function with ID 0xAB and two additional bytes
    registerService(service01);
    receive({0x05, 0x05, 0xAB, 0xCC, 0xDD});
    EXPECT_VECTOR_EQ({0x14, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, transmitted);
}

