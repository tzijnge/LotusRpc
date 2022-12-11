#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "Server.hpp"

class I0DecoderMock : public Decoder
{
public:
    uint32_t id() const override { return 0; }
    void decode(etl::byte_stream_reader & reader) override
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

class I1DecoderMock : public Decoder
{
public:
    uint32_t id() const override { return 1; }

    void decode(etl::byte_stream_reader &reader) override
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

class TestServer : public ::testing::Test
{
public:
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
    server.decode(0x04);
    server.decode(0x00);
    server.decode(0xAA);
    server.decode(0xBB);

    EXPECT_EQ((std::vector<uint8_t>{0xAA, 0xBB}), i0Decoder.received);
}

TEST_F(TestServer, decodeI0AndI1)
{
    server.registerDecoder(i0Decoder);
    server.registerDecoder(i1Decoder);
    server.decode(0x04);
    server.decode(0x00);
    server.decode(0xAA);
    server.decode(0xBB);
    server.decode(0x04);
    server.decode(0x01);
    server.decode(0xCC);
    server.decode(0xDD);

    EXPECT_EQ((std::vector<uint8_t>{0xAA, 0xBB}), i0Decoder.received);
    EXPECT_EQ((std::vector<uint8_t>{0xCC, 0xDD}), i1Decoder.received);
}