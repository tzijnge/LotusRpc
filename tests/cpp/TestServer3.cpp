#include "generated/Server3/Server3.hpp"
#include <sstream>
#include "TestUtils.hpp"

namespace
{
    class S00Service : public srv3::s00_shim
    {
    public:
        uint8_t f0(uint8_t p1) override
        {
            return p1;
        }
    };

    class S01Service : public srv3::s01_shim
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

static_assert(std::is_same<srv3::Server3, lrpc::Server<6, srv3::LrpcMeta_service, 256, 256>>::value, "RX and/or TX buffer size are unequal to the definition file");

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

namespace meta = srv3::lrpc_meta;
static_assert(meta::DefinitionVersion.empty(), "");
static_assert(std::is_same<decltype(meta::DefinitionVersion), const etl::string_view>::value, "");

static_assert(meta::DefinitionHash.size() == 20, "");
static_assert(std::is_same<decltype(meta::DefinitionHash), const etl::string_view>::value, "");

static_assert(!meta::LrpcVersion.empty(), "");
static_assert(std::is_same<decltype(meta::LrpcVersion), const etl::string_view>::value, "");

TEST_F(TestServer3, versionInfo)
{
    const auto version = srv3::LrpcMeta_service().version();
    EXPECT_TRUE(std::get<0>(version).empty());
    EXPECT_EQ(std::get<1>(version).size(), 20);
    EXPECT_FALSE(std::get<2>(version).empty());
}