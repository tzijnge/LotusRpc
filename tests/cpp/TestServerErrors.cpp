#include "generated/Server3/Server3.hpp"
#include "TestUtils.hpp"
#include <sstream>
#include <cstdint>
#include <gtest/gtest.h>
#include <type_traits>
#include <ios>
#include <iomanip>

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServerErrorsS00 : public srv3::s00_shim
{
    public:
        uint8_t f0(const uint8_t p1) override
        {
            return p1;
        }
    };

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServerErrorsS01 : public srv3::s01_shim
{
    public:
        uint16_t f0(const uint16_t p1) override
        {
            return p1;
        }
    };

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class TestServerErrors : public ::testing::Test, public srv3::Server3
{
    public:
        TestServerErrors()
        {
            registerService(service00);
            // service 5 is intentionally not registered
        }

        void receive(const lrpc::string_view hex)
        {
            lrpcReceive(testutils::hexToBytes(hex));
        }

        void lrpcTransmit(const lrpc::span<const uint8_t> bytes) override
        {
            std::stringstream stream;
            for (const auto b : bytes)
            {
                stream << std::hex << std::setw(2) << std::uppercase << std::setfill('0') << static_cast<uint32_t>(b);
            }
            transmitted += stream.str();
        }

        // NOLINTNEXTLINE(misc-non-private-member-variables-in-classes)
        std::string transmitted;
        // NOLINTNEXTLINE(misc-non-private-member-variables-in-classes)
        MockServerErrorsS00 service00;
        // NOLINTNEXTLINE(misc-non-private-member-variables-in-classes)
        MockServerErrorsS01 service01;
    };

TEST_F(TestServerErrors, decodeUnknownServiceLessThanMaxServiceId)
{
    // Non-existing service 0x02 (smaller than MAX_SERVICE_ID), function ID 0xAB and no additional bytes
    receive("0202AB");
    EXPECT_EQ("0AFF000002AB0000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnknownServiceGreaterThanServiceId)
{
    static constexpr uint8_t SRV3_MAX_SERVICE_ID{6};
    static_assert(std::is_same<srv3::Server3, lrpc::Server<SRV3_MAX_SERVICE_ID, srv3::LrpcMeta_service>>::value, "Unexpected server properties");

    // Non-existing service 0x07 (one greater than MAX_SERVICE_ID), function ID 0xAB and no additional bytes
    receive("0207AB");
    EXPECT_EQ("0AFF000007AB0000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnknownServiceMuchGreaterThanMaxServiceId)
{
    // Non-existing service 0x77 (greater than MAX_SERVICE_ID), function ID 0 and two additional bytes
    receive("0477000000");
    EXPECT_EQ("0AFF000077000000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnregistereredService)
{
    receive("040508CCDD");
    EXPECT_EQ("0AFF000005080000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnknownFunctionSmallerThanMaxFunctionId)
{
    // register service s01 (ID 5) and call non-existing function with ID 0x00 and two additional bytes
    registerService(service01);
    receive("040500CCDD");
    EXPECT_EQ("0AFF000105000000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnknownFunctionGreaterThanMaxFunctionId)
{
    // register service s01 (ID 5) and call non-existing function with ID 0x09 and two additional bytes
    registerService(service01);
    receive("040509CCDD");
    EXPECT_EQ("0AFF000105090000000000", transmitted);
}

TEST_F(TestServerErrors, decodeUnknownFunctionMuchGreaterThanMaxFunctionId)
{
    // register service s01 (ID 5) and call non-existing function with ID 0xAB and two additional bytes
    registerService(service01);
    receive("0405ABCCDD");
    EXPECT_EQ("0AFF000105AB0000000000", transmitted);
}
