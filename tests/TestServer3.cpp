#include "generated/Server3/Server3.hpp"
#include <gtest/gtest.h>

static_assert(etl::is_same_v<Server3, lrpc::Server<256, 256>>);

class TestServer3 : public ::testing::Test
{
};

TEST_F(TestServer3, construct)
{
    Server3 server3;
    server3.decode({});
}