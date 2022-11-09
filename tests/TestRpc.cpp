#include <etl/byte_stream.h>
#include <etl/string.h>
#include <etl/string_view.h>
#include <etl/vector.h>
#include <gmock/gmock.h>
#include <gtest/gtest.h>

struct CompositeData
{
    etl::array<uint16_t, 2> a;
    uint8_t b;
    bool c;
};

bool operator==(const CompositeData &first, const CompositeData &second)
{
    return false;
}

class LotusRpc
{
public:
    void decode(uint8_t byte)
    {
        messageBuffer.push_back(byte);

        if (messageIsComplete())
        {
            invokeFunction();
            messageBuffer.clear();
        }
    }

    virtual void f0() = 0;
    virtual void f1() = 0;
    virtual void f2(uint8_t a) = 0;
    virtual void f3(uint16_t a) = 0;
    virtual void f4(float a) = 0;
    virtual void f5(const etl::array<uint16_t, 2>& a) = 0;
    virtual void f6(const etl::string_view &a) = 0;
    virtual void f7(const CompositeData &a) = 0;

private:
    etl::vector<uint8_t, 256> messageBuffer;
    inline static const etl::vector<uint8_t, 256> messageSizes{1, 1, 2, 3, 5, 5, 5, 7};

    bool messageIsComplete() const
    {
        auto messageId = messageBuffer.at(0);
        auto messageSize = messageSizes.at(messageId);

        return messageBuffer.size() == messageSize;
    }

    void invokeFunction()
    {
        auto messageId = messageBuffer.at(0);
        ((this)->*(invokers.at(messageId)))();
    }

    void invokeF0()
    {
        f0();
    }

    void invokeF1()
    {
        f1();
    }

    void invokeF2()
    {
        f2(messageBuffer.at(1));
    }

    void invokeF3()
    {
        etl::byte_stream_reader stream(messageBuffer.begin(), messageBuffer.end(), etl::endian::little);
        stream.skip<uint8_t>(1);
        auto a = stream.read_unchecked<uint16_t>();
        f3(a);
    }

    void invokeF4()
    {
        etl::byte_stream_reader stream(messageBuffer.begin(), messageBuffer.end(), etl::endian::little);
        stream.skip<uint8_t>(1);
        auto a = stream.read_unchecked<float>();
        f4(a);
    }

    void invokeF5()
    {
        etl::byte_stream_reader stream(messageBuffer.begin(), messageBuffer.end(), etl::endian::little);
        stream.skip<uint8_t>(1);
        etl::array<uint16_t, 2> arr;
        stream.read_unchecked<uint16_t>(arr);
        f5(arr);
    }

    void invokeF6()
    {
        etl::string_view sv(reinterpret_cast<char *>(&messageBuffer[1]), 4);
        f6(sv);
    }

    void invokeF7()
    {
        CompositeData cd;
        etl::byte_stream_reader stream(messageBuffer.begin(), messageBuffer.end(), etl::endian::little);
        stream.skip<uint8_t>(1);
        stream.read_unchecked<uint16_t>(cd.a);
        cd.b = stream.read_unchecked<uint8_t>();
        cd.c = stream.read_unchecked<uint8_t>();
        f7(cd);
    }

    using Invoker = void (LotusRpc::*)();
    inline static const etl::vector<Invoker, 256> invokers{
        &LotusRpc::invokeF0,
        &LotusRpc::invokeF1,
        &LotusRpc::invokeF2,
        &LotusRpc::invokeF3,
        &LotusRpc::invokeF4,
        &LotusRpc::invokeF5,
        &LotusRpc::invokeF6,
        &LotusRpc::invokeF7,
    };
};

class MockLotusRpc : public LotusRpc
{
public:
    MOCK_METHOD(void, f0, (), (override));
    MOCK_METHOD(void, f1, (), (override));
    MOCK_METHOD(void, f2, (uint8_t a), (override));
    MOCK_METHOD(void, f3, (uint16_t a), (override));
    MOCK_METHOD(void, f4, (float a), (override));
    MOCK_METHOD(void, f5, ((const etl::array<uint16_t, 2>) &a), (override));
    MOCK_METHOD(void, f6, (const etl::string_view &a), (override));
    MOCK_METHOD(void, f7, (const CompositeData &a), (override));
};

class TestRpc : public ::testing::Test
{
public:
    MockLotusRpc rpc;
};

TEST_F(TestRpc, decodeF0)
{
    EXPECT_CALL(rpc, f0()).Times(1);
    EXPECT_CALL(rpc, f1()).Times(0);
    
    rpc.decode(0);
}

TEST_F(TestRpc, decodeF1)
{
    EXPECT_CALL(rpc, f0()).Times(0);
    EXPECT_CALL(rpc, f1()).Times(1);

    rpc.decode(1);
}

TEST_F(TestRpc, decodeF2)
{
    EXPECT_CALL(rpc, f2(123));
    rpc.decode(2);
    rpc.decode(123);
}

TEST_F(TestRpc, decodeF1AndF2)
{
    EXPECT_CALL(rpc, f1());
    EXPECT_CALL(rpc, f2(123));
    rpc.decode(1);
    rpc.decode(2);
    rpc.decode(123);
}

TEST_F(TestRpc, decodeF3)
{
    EXPECT_CALL(rpc, f3(0xCDAB));
    rpc.decode(3);
    rpc.decode(0xAB);
    rpc.decode(0xCD);
}

TEST_F(TestRpc, decodeF4)
{
    EXPECT_CALL(rpc, f4(123.456));
    rpc.decode(4);
    rpc.decode(0x79);
    rpc.decode(0xE9);
    rpc.decode(0xF6);
    rpc.decode(0x42);
}

TEST_F(TestRpc, decodeF5)
{
    EXPECT_CALL(rpc, f5(etl::array<uint16_t, 2>{0xBBAA, 0xDDCC}));
    rpc.decode(5);
    rpc.decode(0xAA);
    rpc.decode(0xBB);
    rpc.decode(0xCC);
    rpc.decode(0xDD);
}

TEST_F(TestRpc, decodeF6)
{
    EXPECT_CALL(rpc, f6(etl::string_view("Test")));
    rpc.decode(6);
    rpc.decode('T');
    rpc.decode('e');
    rpc.decode('s');
    rpc.decode('t');
}

TEST_F(TestRpc, decodeF7)
{
    CompositeData expected{{0xBBAA, 0xDDCC}, 123, true};
    EXPECT_CALL(rpc, f7(expected));
    rpc.decode(7);
    rpc.decode(0xAA);
    rpc.decode(0xBB);
    rpc.decode(0xCC);
    rpc.decode(0xDD);
    rpc.decode(123);
    rpc.decode(1);
}
