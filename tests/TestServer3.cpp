#include "generated/Server3/Server3.hpp"
#include <gtest/gtest.h>

static_assert(std::is_same_v<srv3::Server3, lrpc::Server<256, 256>>, "RX and/or TX buffer size are unequal to the definition file");

class TestServer3 : public ::testing::Test
{
};

TEST_F(TestServer3, construct)
{
    // Server3 server3;
    // server3.lrpcReceive({});
}