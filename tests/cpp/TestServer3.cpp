#include <cstdint>
#include <iomanip>
#include <ios>
#include <sstream>
#include <type_traits>

#include <gtest/gtest.h>

#include "TestUtils.hpp"
#include "generated/Server3/Server3.hpp"

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServer3S00 : public srv3::srv0_shim
{
public:
    uint8_t f0(const uint8_t p0) override { return p0; }
};

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
class MockServer3S01 : public srv3::srv1_shim
{
public:
    uint16_t f0(const uint16_t p0) override { return p0; }
};

// NOLINTNEXTLINE(misc-use-anonymous-namespace)
// NOLINTNEXTLINE(misc-multiple-inheritance)
class TestServer3 : public ::testing::Test, public srv3::Server3
{
public:
    TestServer3()
    {
        registerService(service00);
        registerService(service01);
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

    // NOLINTNEXTLINE(misc-non-private-member-variables-in-classes)
    std::string transmitted;
    // NOLINTNEXTLINE(misc-non-private-member-variables-in-classes)
    MockServer3S00 service00;
    // NOLINTNEXTLINE(misc-non-private-member-variables-in-classes)
    MockServer3S01 service01;
};

static_assert(std::is_same<srv3::Server3, lrpc::Server<6, srv3::LrpcMeta_service, 256, 256>>::value,
              "RX and/or TX buffer size are unequal to the definition file");

TEST_F(TestServer3, decodeI0)
{
    receive("030000AA");
    EXPECT_EQ("030000AA", transmitted);
}

TEST_F(TestServer3, decodeI0AndI5)
{
    receive("030000BB040508CCDD");
    EXPECT_EQ("030000BB040508CCDD", transmitted);
}

namespace meta = srv3::lrpc_meta;
static_assert(meta::DefinitionVersion.empty(), "");
static_assert(std::is_same<decltype(meta::DefinitionVersion), const lrpc::string_view>::value, "");

static_assert(meta::DefinitionHash.size() == 20, "");
static_assert(std::is_same<decltype(meta::DefinitionHash), const lrpc::string_view>::value, "");

static_assert(!meta::LrpcVersion.empty(), "");
static_assert(std::is_same<decltype(meta::LrpcVersion), const lrpc::string_view>::value, "");

TEST_F(TestServer3, versionInfo)
{
    const auto version = srv3::LrpcMeta_service().version();
    EXPECT_TRUE(std::get<0>(version).empty());
    EXPECT_EQ(std::get<1>(version).size(), 20);
    EXPECT_FALSE(std::get<2>(version).empty());
}