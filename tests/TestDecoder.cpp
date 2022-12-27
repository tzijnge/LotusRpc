#include <etl/byte_stream.h>
#include <etl/string.h>
#include <etl/string_view.h>
#include <etl/vector.h>
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "Decoder.hpp"
#include <tuple>

using ::testing::Return;

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

struct CompositeData3
{
    bool operator==(const CompositeData3 &other) const = default;
    bool operator!=(const CompositeData3 &other) const
    {
        return !(*this == other);
    }

    CompositeData2 a;
};

MATCHER_P(SPAN_EQ, e, "Equality matcher for etl::span")
{
    if (e.size() != arg.size())
    {
        return false;
    }
    for (auto i = 0; i < e.size(); ++i)
    {
        if (e[i] != arg[i])
        {
            return false;
        }
    }
    return true;

}

enum class MyEnum {
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

    template <>
    CompositeData3 read_unchecked<CompositeData3>(etl::byte_stream_reader &stream)
    {
        CompositeData3 cd3;
        cd3.a = etl::read_unchecked<CompositeData2>(stream);
        return cd3;
    }

    template <>
    MyEnum read_unchecked<MyEnum>(etl::byte_stream_reader &stream)
    {
        return static_cast<MyEnum>(etl::read_unchecked<uint8_t>(stream));
    }

    template <>
    void write_unchecked<etl::string_view>(etl::byte_stream_writer &stream, const etl::string_view& sv)
    {
        for (auto c : sv)
        {
            stream.write_unchecked(c);
        }
        stream.write_unchecked('\0');
    }
}

class I0Decoder : public Decoder
{
public:
    uint32_t id() const override { return 0; }
    void decode(Reader &reader, Writer& writer) override
    {
        auto messageId = reader.read_unchecked<uint8_t>();
        ((this)->*(invokers.at(messageId)))(reader, writer);
    }

protected:
    virtual void f0() = 0;
    virtual void f1() = 0;
    virtual void f2(uint8_t a) = 0;
    virtual void f3(uint16_t a) = 0;
    virtual void f4(float a) = 0;
    virtual void f5(const etl::span<uint16_t> &a) = 0;
    virtual void f6(const etl::string_view &a) = 0;
    virtual void f7(const CompositeData &a) = 0;
    virtual void f8(MyEnum a) = 0;
    virtual void f9(const etl::span<CompositeData2> &a) = 0;
    virtual void f10(const CompositeData3 &a) = 0;
    virtual void f11(uint8_t a, uint8_t b) = 0;
    virtual uint8_t f12() = 0;
    virtual uint16_t f13() = 0;
    virtual float f14() = 0;
    virtual etl::span<uint16_t> f15() = 0;
    virtual etl::string_view f16() = 0;
    virtual CompositeData f17() = 0;
    virtual MyEnum f18() = 0;
    virtual etl::span<CompositeData2> f19() = 0;
    virtual CompositeData3 f20() = 0;
    virtual std::tuple<uint8_t, uint8_t> f21() = 0;

private:
    using Reader = etl::byte_stream_reader;

    void invokeF0(Reader &r, Writer &w)
    {
        f0();
    }

    void invokeF1(Reader &r, Writer &w)
    {
        f1();
    }

    void invokeF2(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint8_t>(r);
        f2(a);
    }

    void invokeF3(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint16_t>(r);
        f3(a);
    }

    void invokeF4(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<float>(r);
        f4(a);
    }

    void invokeF5(Reader &r, Writer &w)
    {
        etl::array<uint16_t, 2> arr;
        for (auto &element : arr)
        {
            element = etl::read_unchecked<uint16_t>(r);
        }
        f5(arr);
    }

    void invokeF6(Reader &r, Writer &w)
    {
        etl::string_view sv(r.end());
        f6(sv);
    }

    void invokeF7(Reader &r, Writer &w)
    {
        const auto cd = etl::read_unchecked<CompositeData>(r);
        f7(cd);
    }

    void invokeF8(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<MyEnum>(r);
        f8(a);
    }

    void invokeF9(Reader &r, Writer &w)
    {
        etl::array<CompositeData2, 2> arr;
        for (auto &element : arr)
        {
            element = etl::read_unchecked<CompositeData2>(r);
        }
        f9(arr);
    }

    void invokeF10(Reader &r, Writer &w)
    {
        const auto cd3 = etl::read_unchecked<CompositeData3>(r);
        f10(cd3);
    }

    void invokef11(Reader &r, Writer &w)
    {
        const auto a = etl::read_unchecked<uint8_t>(r);
        const auto b = etl::read_unchecked<uint8_t>(r);
        f11(a, b);
    }

    void invokef12(Reader &r, Writer &w)
    {
        const auto response = f12();
        etl::write_unchecked<uint8_t>(w, response);
    }

    void invokef13(Reader &r, Writer &w)
    {
        const auto response = f13();
        etl::write_unchecked<uint16_t>(w, response);
    }

    void invokef14(Reader &r, Writer &w)
    {
        const auto response = f14();
        etl::write_unchecked<float>(w, response);
    }

    void invokef15(Reader &r, Writer &w)
    {
        etl::span<uint16_t> response = f15();
        w.write_unchecked<uint16_t>(response);
    }

    void invokef16(Reader &r, Writer &w)
    {
        const auto response = f16();
        etl::write_unchecked<etl::string_view>(w, response);
    }

    void invokef17(Reader &r, Writer &w)
    {
    }

    void invokef18(Reader &r, Writer &w)
    {
    }

    void invokef19(Reader &r, Writer &w)
    {
    }

    void invokef20(Reader &r, Writer &w)
    {
    }

    void invokef21(Reader &r, Writer &w)
    {
    }

    using Invoker = void (I0Decoder::*)(Reader &reader, Writer& writer);
    inline static const etl::vector<Invoker, 22> invokers{
        &I0Decoder::invokeF0,
        &I0Decoder::invokeF1,
        &I0Decoder::invokeF2,
        &I0Decoder::invokeF3,
        &I0Decoder::invokeF4,
        &I0Decoder::invokeF5,
        &I0Decoder::invokeF6,
        &I0Decoder::invokeF7,
        &I0Decoder::invokeF8,
        &I0Decoder::invokeF9,
        &I0Decoder::invokeF10,
        &I0Decoder::invokef11,
        &I0Decoder::invokef12,
        &I0Decoder::invokef13,
        &I0Decoder::invokef14,
        &I0Decoder::invokef15,
        &I0Decoder::invokef16,
        &I0Decoder::invokef17,
        &I0Decoder::invokef18,
        &I0Decoder::invokef19,
        &I0Decoder::invokef20,
        &I0Decoder::invokef21,
    };
};

class MockI0Decoder : public I0Decoder
{
public:
    MOCK_METHOD(void, f0, (), (override));
    MOCK_METHOD(void, f1, (), (override));
    MOCK_METHOD(void, f2, (uint8_t a), (override));
    MOCK_METHOD(void, f3, (uint16_t a), (override));
    MOCK_METHOD(void, f4, (float a), (override));
    MOCK_METHOD(void, f5, ((const etl::span<uint16_t>)&a), (override));
    MOCK_METHOD(void, f6, (const etl::string_view &a), (override));
    MOCK_METHOD(void, f7, (const CompositeData &a), (override));
    MOCK_METHOD(void, f8, (MyEnum a), (override));
    MOCK_METHOD(void, f9, ((const etl::span<CompositeData2>)&a), (override));
    MOCK_METHOD(void, f10, (const CompositeData3 &a), (override));
    MOCK_METHOD(void, f11, (uint8_t a, uint8_t b), (override));
    MOCK_METHOD(uint8_t, f12, (), (override));
    MOCK_METHOD(uint16_t, f13, (), (override));
    MOCK_METHOD(float, f14, (), (override));
    MOCK_METHOD((etl::span<uint16_t>), f15, (), (override));
    MOCK_METHOD(etl::string_view, f16, (), (override));
    MOCK_METHOD(CompositeData, f17, (), (override));
    MOCK_METHOD(MyEnum, f18, (), (override));
    MOCK_METHOD((etl::span<CompositeData2>), f19, (), (override));
    MOCK_METHOD(CompositeData3, f20, (), (override));
    MOCK_METHOD((std::tuple<uint8_t, uint8_t>), f21, (), (override));
};

class TestDecoder : public ::testing::Test
{
public:
    MockI0Decoder i0Decoder;

    etl::span<uint8_t> decode(const std::vector<uint8_t> &bytes)
    {
        const etl::span<const uint8_t> s(bytes.begin(), bytes.end());

        Decoder::Reader reader(s.begin(), s.end(), etl::endian::little);
        Decoder::Writer writer(response.begin(), response.end(), etl::endian::little);
        i0Decoder.decode(reader, writer);

        return { response.begin(), writer.size_bytes()};
    }

    void EXPECT_RESPONSE(const std::vector<uint8_t> &expected, const etl::span<uint8_t> actual)
    {
        std::vector<uint8_t> actualVec {actual.begin(), actual.end()};
        EXPECT_EQ(expected, actualVec);
    }

private:
    etl::array<uint8_t, 256> response;
};

// Decode void function f0. Make sure f1 is not called
TEST_F(TestDecoder, decodeF0)
{
    EXPECT_CALL(i0Decoder, f0()).Times(1);
    EXPECT_CALL(i0Decoder, f1()).Times(0);

    auto response = decode({0});
    EXPECT_TRUE(response.empty());
}

// Decode void function f1. Make sure f0 is not called
TEST_F(TestDecoder, decodeF1)
{
    EXPECT_CALL(i0Decoder, f0()).Times(0);
    EXPECT_CALL(i0Decoder, f1()).Times(1);

    auto response = decode({1});
    EXPECT_TRUE(response.empty());
}

// Decode function f2 with uint8_t arg
TEST_F(TestDecoder, decodeF2)
{
    EXPECT_CALL(i0Decoder, f2(123));
    auto response = decode({2, 123});
    EXPECT_TRUE(response.empty());
}

// Decode function f3 with uint16_t arg
TEST_F(TestDecoder, decodeF3)
{
    EXPECT_CALL(i0Decoder, f3(0xCDAB));
    auto response = decode({3, 0xAB, 0xCD});
    EXPECT_TRUE(response.empty());
}

// Decode function f4 with float arg
TEST_F(TestDecoder, decodeF4)
{
    EXPECT_CALL(i0Decoder, f4(123.456));
    auto response = decode({4, 0x79, 0xE9, 0xF6, 0x42});
    EXPECT_TRUE(response.empty());
}

// Decode function f5 with array of uint16_t arg
TEST_F(TestDecoder, decodeF5)
{
    std::vector<uint16_t> expected {0xBBAA, 0xDDCC};
    EXPECT_CALL(i0Decoder, f5(SPAN_EQ(expected)));
    auto response = decode({5, 0xAA, 0xBB, 0xCC, 0xDD});
    EXPECT_TRUE(response.empty());
}

// Decode function f6 with string arg
TEST_F(TestDecoder, decodeF6)
{
    EXPECT_CALL(i0Decoder, f6(etl::string_view("Test")));
    auto response = decode({6, 'T', 'e', 's', 't', '\0'});
    EXPECT_TRUE(response.empty());
}

// Decode function f7 with custom type
TEST_F(TestDecoder, decodeF7)
{
    CompositeData expected{{0xBBAA, 0xDDCC}, 123, true};
    EXPECT_CALL(i0Decoder, f7(expected));
    auto response = decode({7, 0xAA, 0xBB, 0xCC, 0xDD, 123, 1});
    EXPECT_TRUE(response.empty());
}

// Decode function f8 with custom enum
TEST_F(TestDecoder, decodeF8)
{
    EXPECT_CALL(i0Decoder, f8(MyEnum::V3));
    auto response = decode({8, 0x03});
    EXPECT_TRUE(response.empty());
}

// Decode function f9 with array of custom type
TEST_F(TestDecoder, decodeF9)
{
    std::vector<CompositeData2> expected{
        CompositeData2{0xAA, 0xBB},
        CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(i0Decoder, f9(SPAN_EQ(expected)));
    auto response = decode({9, 0xAA, 0xBB, 0xCC, 0xDD});
    EXPECT_TRUE(response.empty());
}

// Decode function f10 with nested custom types
TEST_F(TestDecoder, decodeF10)
{
    CompositeData3 expected{{0xAA, 0xBB}};
    EXPECT_CALL(i0Decoder, f10(expected));
    auto response = decode({10, 0xAA, 0xBB});
    EXPECT_TRUE(response.empty());
}

// Decode function f11 with two uint8_t args
TEST_F(TestDecoder, decodef11)
{
    EXPECT_CALL(i0Decoder, f11(123, 111));
    auto response = decode({11, 123, 111});
    EXPECT_TRUE(response.empty());
}

// Decode function f12 which returns uint8_t
TEST_F(TestDecoder, decodef12)
{
    EXPECT_CALL(i0Decoder, f12()).WillOnce(Return(0xAB));
    auto response = decode({12});
    EXPECT_RESPONSE({0xAB}, response);
}

// Decode function f13 which returns uint16_t
TEST_F(TestDecoder, decodef13)
{
    EXPECT_CALL(i0Decoder, f13()).WillOnce(Return(0xABCD));
    auto response = decode({13});
    EXPECT_RESPONSE({0xCD, 0xAB}, response);
}

// Decode function f14 which returns float
TEST_F(TestDecoder, decodeF14)
{
    EXPECT_CALL(i0Decoder, f14()).WillOnce(Return(123.456));
    auto response = decode({14});
    EXPECT_RESPONSE({0x79, 0xE9, 0xF6, 0x42}, response);
}

// Decode function f15 which return array of uint16_t
TEST_F(TestDecoder, decodeF15)
{
    std::vector<uint16_t> expected{0xBBAA, 0xDDCC};
    EXPECT_CALL(i0Decoder, f15()).WillOnce(Return(etl::span<uint16_t>(expected)));
    auto response = decode({15});
    EXPECT_RESPONSE({0xAA, 0xBB, 0xCC, 0xDD}, response);
}

// Decode function f16 which returns a string
TEST_F(TestDecoder, decodeF16)
{
    EXPECT_CALL(i0Decoder, f16()).WillOnce(Return(etl::string_view("Test")));
    auto response = decode({16});
    EXPECT_RESPONSE({'T', 'e', 's', 't', '\0'}, response);
}
