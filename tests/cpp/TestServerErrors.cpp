// IWYU pragma: no_include <vector>
#include <iomanip>
#include <ios>  // IWYU pragma: keep
#include <sstream>
#include <string>
#include <type_traits>

#include <gtest/gtest.h>

#include "LrpcTypes.hpp"
#include "TestUtils.hpp"
#include "generated/Server3/Server3.hpp"

class MockServerErrorsS00 : public srv3::srv0_shim
{
public:
    uint8_t f0(const uint8_t p0) override { return p0; }
};

class MockServerErrorsS01 : public srv3::srv1_shim
{
public:
    uint16_t f0(const uint16_t p0) override { return p0; }
};

// NOLINTNEXTLINE(misc-multiple-inheritance)
class TestServerErrors : public ::testing::Test, public srv3::Server3
{
public:
    TestServerErrors()
    {
        registerService(service00);
        // service 5 is intentionally not registered
    }

    // NOLINTNEXTLINE(misc-include-cleaner)
    void receive(const lrpc::string_view hex) { lrpcReceive(testutils::hexToBytes(hex)); }

    // NOLINTNEXTLINE(misc-include-cleaner)
    void lrpcTransmit(const lrpc::span<const uint8_t> bytes) override
    {
        std::stringstream stream;
        for (const auto _byte : bytes)
        {
            stream << std::hex << std::setw(2) << std::uppercase << std::setfill('0') << static_cast<uint32_t>(_byte);
        }
        transmitted += stream.str();
    }

    std::string transmitted;
    MockServerErrorsS00 service00;
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
    static_assert(std::is_same<srv3::Server3, lrpc::Server<SRV3_MAX_SERVICE_ID, srv3::LrpcMeta_service>>::value,
                  "Unexpected server properties");

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
