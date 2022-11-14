#include <etl/byte_stream.h>
#include <etl/string.h>
#include <etl/string_view.h>
#include <etl/vector.h>
#include <gmock/gmock.h>
#include <gtest/gtest.h>

struct CompositeData
{
    bool operator==(const CompositeData &other) const = default;

    etl::array<uint16_t, 2> a;
    uint8_t b;
    bool c;
};

struct CompositeData2
{
    bool operator==(const CompositeData2 &other) const = default;
    bool operator!=(const CompositeData2 &other) const
    {
        return !(*this == other);
    }

    uint8_t a;
    uint8_t b;
};

enum class MyEnum
{
    V0,
    V1,
    V2,
    V3
};

namespace etl
{
    template <>
    CompositeData read_unchecked<CompositeData>(etl::byte_stream_reader &stream)
    {
        CompositeData cd;
        stream.read_unchecked<uint16_t>(cd.a);
        cd.b = stream.read_unchecked<uint8_t>();
        cd.c = stream.read_unchecked<bool>();
        return cd;
    }

    template <>
    CompositeData2 read_unchecked<CompositeData2>(etl::byte_stream_reader &stream)
    {
        CompositeData2 cd2;
        cd2.a = stream.read_unchecked<uint8_t>();
        cd2.b = stream.read_unchecked<uint8_t>();
        return cd2;
    }
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
    virtual void f5(const etl::array<uint16_t, 2> &a) = 0;
    virtual void f6(const etl::string_view &a) = 0;
    virtual void f7(const CompositeData &a) = 0;
    virtual void f8(MyEnum a) = 0;
    virtual void f9(const etl::array<CompositeData2, 2> &a) = 0;

private:
    using Reader = etl::byte_stream_reader;
    etl::vector<uint8_t, 256> messageBuffer;
    inline static const etl::vector<uint8_t, 256> messageSizes{1, 1, 2, 3, 5, 5, 5, 7, 2, 5};

    bool messageIsComplete() const
    {
        auto messageId = messageBuffer.at(0);
        auto messageSize = messageSizes.at(messageId);

        return messageBuffer.size() == messageSize;
    }

    void invokeFunction()
    {
        Reader reader(messageBuffer.begin(), messageBuffer.end(), etl::endian::little);
        auto messageId = reader.read_unchecked<uint8_t>();
        ((this)->*(invokers.at(messageId)))(reader);
    }

    void invokeF0(Reader &reader)
    {
        f0();
    }

    void invokeF1(Reader &reader)
    {
        f1();
    }

    void invokeF2(Reader &reader)
    {
        auto a = reader.read_unchecked<uint8_t>();
        f2(a);
    }

    void invokeF3(Reader &reader)
    {
        auto a = reader.read_unchecked<uint16_t>();
        f3(a);
    }

    void invokeF4(Reader &reader)
    {
        auto a = reader.read_unchecked<float>();
        f4(a);
    }

    void invokeF5(Reader &reader)
    {
        etl::array<uint16_t, 2> arr;
        reader.read_unchecked<uint16_t>(arr);
        f5(arr);
    }

    void invokeF6(Reader &reader)
    {
        etl::string_view sv(reinterpret_cast<char *>(&messageBuffer[1]), 4);
        f6(sv);
    }

    void invokeF7(Reader &reader)
    {
        auto cd = etl::read_unchecked<CompositeData>(reader);
        f7(cd);
    }

    void invokeF8(Reader &reader)
    {
        auto a = reader.read_unchecked<uint8_t>();
        f8(static_cast<MyEnum>(a));
    }

    void invokeF9(Reader &reader)
    {
        etl::array<CompositeData2, 2> arr;
        for (auto &element : arr)
        {
            element = etl::read_unchecked<CompositeData2>(reader);
        }
        f9(arr);
    }

    using Invoker = void (LotusRpc::*)(Reader &reader);
    inline static const etl::vector<Invoker, 256> invokers{
        &LotusRpc::invokeF0,
        &LotusRpc::invokeF1,
        &LotusRpc::invokeF2,
        &LotusRpc::invokeF3,
        &LotusRpc::invokeF4,
        &LotusRpc::invokeF5,
        &LotusRpc::invokeF6,
        &LotusRpc::invokeF7,
        &LotusRpc::invokeF8,
        &LotusRpc::invokeF9,
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
    MOCK_METHOD(void, f5, ((const etl::array<uint16_t, 2>)&a), (override));
    MOCK_METHOD(void, f6, (const etl::string_view &a), (override));
    MOCK_METHOD(void, f7, (const CompositeData &a), (override));
    MOCK_METHOD(void, f8, (MyEnum a), (override));
    MOCK_METHOD(void, f9, ((const etl::array<CompositeData2, 2>)&a), (override));
};

class TestRpc : public ::testing::Test
{
public:
    MockLotusRpc rpc;

    void decode(const std::vector<uint8_t> &bytes)
    {
        for (auto b : bytes)
        {
            rpc.decode(b);
        }
    }
};

TEST_F(TestRpc, decodeF0)
{
    EXPECT_CALL(rpc, f0()).Times(1);
    EXPECT_CALL(rpc, f1()).Times(0);

    decode({0});
}

TEST_F(TestRpc, decodeF1)
{
    EXPECT_CALL(rpc, f0()).Times(0);
    EXPECT_CALL(rpc, f1()).Times(1);

    decode({1});
}

TEST_F(TestRpc, decodeF2)
{
    EXPECT_CALL(rpc, f2(123));
    decode({2, 123});
}

TEST_F(TestRpc, decodeF1AndF2)
{
    EXPECT_CALL(rpc, f1());
    EXPECT_CALL(rpc, f2(123));
    decode({1, 2, 123});
}

TEST_F(TestRpc, decodeF3)
{
    EXPECT_CALL(rpc, f3(0xCDAB));
    decode({3, 0xAB, 0xCD});
}

TEST_F(TestRpc, decodeF4)
{
    EXPECT_CALL(rpc, f4(123.456));
    decode({4, 0x79, 0xE9, 0xF6, 0x42});
}

TEST_F(TestRpc, decodeF5)
{
    EXPECT_CALL(rpc, f5(etl::array<uint16_t, 2>{0xBBAA, 0xDDCC}));
    decode({5, 0xAA, 0xBB, 0xCC, 0xDD});
}

TEST_F(TestRpc, decodeF6)
{
    EXPECT_CALL(rpc, f6(etl::string_view("Test")));
    decode({6, 'T', 'e', 's', 't'});
}

TEST_F(TestRpc, decodeF7)
{
    CompositeData expected{{0xBBAA, 0xDDCC}, 123, true};
    EXPECT_CALL(rpc, f7(expected));
    decode({7, 0xAA, 0xBB, 0xCC, 0xDD, 123, 1});
}

TEST_F(TestRpc, decodeF8)
{
    EXPECT_CALL(rpc, f8(MyEnum::V3));
    decode({8, 0x03});
}

TEST_F(TestRpc, decodeF9)
{
    etl::array<CompositeData2, 2> expected{
        CompositeData2{0xAA, 0xBB},
        CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(rpc, f9(expected));
    decode({9, 0xAA, 0xBB, 0xCC, 0xDD});
}
