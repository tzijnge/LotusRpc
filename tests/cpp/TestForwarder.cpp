#include <cstdint>
#include <vector>

#include <gtest/gtest.h>

#include "TestUtils.hpp"
#include "generated/Server3/Server3.hpp"
#include "generated/core/lrpccore/LrpcTypes.hpp"

class TestServer : public srv3::Server3
{
public:
    // NOLINTNEXTLINE(misc-include-cleaner)
    void lrpcTransmit(const lrpc::span<const uint8_t> bytes) override
    {
        capturedBytes.assign(bytes.begin(), bytes.end());
    }

    std::vector<uint8_t> capturedBytes;
};

class Forwarder : public srv3::srv0_forwarder
{
public:
    void forwardToServer(const lrpc::span<const uint8_t> data) override
    {
        capturedBytes.assign(data.begin(), data.end());
    }

    std::vector<uint8_t> capturedBytes;
};

class TestForwarder : public ::testing::Test
{
public:
    TestServer server;
    Forwarder forwarder;

protected:
    void SetUp() override { server.registerService(forwarder); }
};

TEST_F(TestForwarder, messageForOtherServiceNotForwarded)
{
    server.lrpcReceive(testutils::hexToBytes("040508AABB"));
    EXPECT_TRUE(forwarder.capturedBytes.empty());
}

TEST_F(TestForwarder, forwardCompleteMessage)
{
    server.lrpcReceive(testutils::hexToBytes("030000AA"));
    EXPECT_EQ(forwarder.capturedBytes, (std::vector<uint8_t>{0x03, 0x00, 0x00, 0xAA}));

    forwarder.capturedBytes.clear();
    server.lrpcReceive(testutils::hexToBytes("030000BB"));
    EXPECT_EQ(forwarder.capturedBytes, (std::vector<uint8_t>{0x03, 0x00, 0x00, 0xBB}));
}

TEST_F(TestForwarder, forwardToClientSingleByte)
{
    forwarder.forwardToClient(uint8_t{0xAA});

    EXPECT_EQ(server.capturedBytes, (std::vector<uint8_t>{0xAA}));
}

TEST_F(TestForwarder, forwardToClientSpan)
{
    // NOLINTNEXTLINE(misc-include-cleaner)
    const lrpc::array<uint8_t, 4> data{0xAA, 0xBB, 0xCC, 0xDD};
    forwarder.forwardToClient(lrpc::span<const uint8_t>{data});

    EXPECT_EQ(server.capturedBytes, (std::vector<uint8_t>{0xAA, 0xBB, 0xCC, 0xDD}));
}

TEST_F(TestForwarder, forwardToClientContainer)
{
    const auto data = std::vector<uint8_t>{0xAA, 0xBB, 0xCC, 0xDD};
    forwarder.forwardToClient(data);

    EXPECT_EQ(server.capturedBytes, (std::vector<uint8_t>{0xAA, 0xBB, 0xCC, 0xDD}));
}
