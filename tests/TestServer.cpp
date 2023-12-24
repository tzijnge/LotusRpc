#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "lrpc/Server.hpp"

class ServiceMock : public lrpc::Service
{
public:
    void decode(Reader & reader, Writer& writer) override
    {
        while (true)
        {
            const auto b = reader.read<uint8_t>();
            if (b)
            {
                received.push_back(b.value());
            }
            else
            {
                break;
            }
        }
    }

    std::vector<uint8_t> received;
};

class I0ServiceMock : public ServiceMock
{
public:
    uint32_t id() const override { return 0; }
};

class I5ServiceMock : public ServiceMock
{
public:
    uint32_t id() const override { return 5; }
};

class TestServer : public ::testing::Test
{
public:
    void decode(const std::vector<uint8_t> &bytes)
    {
        for (const auto& b : bytes)
        {
            server.decode(b);
        }
    }

    void EXPECT_VECTOR_EQ(const std::vector<uint8_t> &v1, const std::vector<uint8_t> &v2)
    {
        EXPECT_EQ(v1, v2);
    }

    lrpc::Server<> server;
    I0ServiceMock i0Service;
    I5ServiceMock i5Service;
};

TEST_F(TestServer, registerService)
{
    server.registerService(i0Service);
}

TEST_F(TestServer, decodeI0)
{
    server.registerService(i0Service);
    decode({0x04, 0x00, 0xAA, 0xBB});

    EXPECT_VECTOR_EQ({0xAA, 0xBB}, i0Service.received);
}

TEST_F(TestServer, decodeI0AndI5)
{
    server.registerService(i0Service);
    server.registerService(i5Service);
    decode({0x04, 0x00, 0xAA, 0xBB, 0x04, 0x05, 0xCC, 0xDD});

    EXPECT_VECTOR_EQ({0xAA, 0xBB}, i0Service.received);
    EXPECT_VECTOR_EQ({0xCC, 0xDD}, i5Service.received);
}