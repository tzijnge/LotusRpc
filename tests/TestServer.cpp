#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "Server.hpp"

class DecoderMock : public Decoder
{
public:
    void decode(Reader & reader, Writer& writer) override
    {
        while (true)
        {
            auto b = reader.read<uint8_t>();
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

class I0DecoderMock : public DecoderMock
{
public:
    uint32_t id() const override { return 0; }
};

class I1DecoderMock : public DecoderMock
{
public:
    uint32_t id() const override { return 1; }
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

    Server server;
    I0DecoderMock i0Decoder;
    I1DecoderMock i1Decoder;
};

TEST_F(TestServer, registerDecoder)
{
    server.registerDecoder(i0Decoder);
}

TEST_F(TestServer, decodeI0)
{
    server.registerDecoder(i0Decoder);
    decode({0x04, 0x00, 0xAA, 0xBB});

    EXPECT_VECTOR_EQ({0xAA, 0xBB}, i0Decoder.received);
}

TEST_F(TestServer, decodeI0AndI1)
{
    server.registerDecoder(i0Decoder);
    server.registerDecoder(i1Decoder);
    decode({0x04, 0x00, 0xAA, 0xBB, 0x04, 0x01, 0xCC, 0xDD});

    EXPECT_VECTOR_EQ({0xAA, 0xBB}, i0Decoder.received);
    EXPECT_VECTOR_EQ({0xCC, 0xDD}, i1Decoder.received);
}