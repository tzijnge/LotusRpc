#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "generated/TestDecoder/s0_DecoderShim.hpp"
#include <tuple>

using ::testing::Return;

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

class MockS0Decoder : public s0DecoderShim
{
public:
    MOCK_METHOD(void, f0, (), (override));
    MOCK_METHOD(void, f1, (), (override));
    MOCK_METHOD(void, f2, (uint8_t a), (override));
    MOCK_METHOD(void, f3, (uint16_t a), (override));
    MOCK_METHOD(void, f4, (float a), (override));
    MOCK_METHOD(void, f5, ((const etl::span<const uint16_t>)&a), (override));
    MOCK_METHOD(void, f6, (const etl::string_view &a), (override));
    MOCK_METHOD(void, f7, (const CompositeData &a), (override));
    MOCK_METHOD(void, f8, (MyEnum a), (override));
    MOCK_METHOD(void, f9, ((const etl::span<const CompositeData2>)&a), (override));
    MOCK_METHOD(void, f10, (const CompositeData3 &a), (override));
    MOCK_METHOD(void, f11, (uint8_t a, uint8_t b), (override));
    MOCK_METHOD(uint8_t, f12, (), (override));
    MOCK_METHOD(uint16_t, f13, (), (override));
    MOCK_METHOD(float, f14, (), (override));
    MOCK_METHOD((etl::array<uint16_t, 2>), f15, (), (override));
    MOCK_METHOD(etl::string<20>, f16, (), (override));
    MOCK_METHOD(CompositeData, f17, (), (override));
    MOCK_METHOD(MyEnum, f18, (), (override));
    MOCK_METHOD((etl::array<CompositeData2, 2>), f19, (), (override));
    MOCK_METHOD(CompositeData3, f20, (), (override));
    MOCK_METHOD((std::tuple<uint8_t, uint8_t>), f21, (), (override));
    MOCK_METHOD((std::tuple<etl::string<4>, etl::string<4>>), f22, (const etl::string_view &s1, const etl::string_view &s2), (override));
};

class TestDecoder : public ::testing::Test
{
public:
    MockS0Decoder s0Decoder;

    etl::span<uint8_t> decode(const std::vector<uint8_t> &bytes)
    {
        const etl::span<const uint8_t> s(bytes.begin(), bytes.end());

        Decoder::Reader reader(s.begin(), s.end(), etl::endian::little);
        Decoder::Writer writer(response.begin(), response.end(), etl::endian::little);
        s0Decoder.decode(reader, writer);

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
    EXPECT_CALL(s0Decoder, f0()).Times(1);
    EXPECT_CALL(s0Decoder, f1()).Times(0);

    auto response = decode({0});
    EXPECT_TRUE(response.empty());
}

// Decode void function f1. Make sure f0 is not called
TEST_F(TestDecoder, decodeF1)
{
    EXPECT_CALL(s0Decoder, f0()).Times(0);
    EXPECT_CALL(s0Decoder, f1()).Times(1);

    auto response = decode({1});
    EXPECT_TRUE(response.empty());
}

// Decode function f2 with uint8_t arg
TEST_F(TestDecoder, decodeF2)
{
    EXPECT_CALL(s0Decoder, f2(123));
    auto response = decode({2, 123});
    EXPECT_TRUE(response.empty());
}

// Decode function f3 with uint16_t arg
TEST_F(TestDecoder, decodeF3)
{
    EXPECT_CALL(s0Decoder, f3(0xCDAB));
    auto response = decode({3, 0xAB, 0xCD});
    EXPECT_TRUE(response.empty());
}

// Decode function f4 with float arg
TEST_F(TestDecoder, decodeF4)
{
    EXPECT_CALL(s0Decoder, f4(123.456));
    auto response = decode({4, 0x79, 0xE9, 0xF6, 0x42});
    EXPECT_TRUE(response.empty());
}

// Decode function f5 with array of uint16_t arg
TEST_F(TestDecoder, decodeF5)
{
    std::vector<uint16_t> expected {0xBBAA, 0xDDCC};
    EXPECT_CALL(s0Decoder, f5(SPAN_EQ(expected)));
    auto response = decode({5, 0xAA, 0xBB, 0xCC, 0xDD});
    EXPECT_TRUE(response.empty());
}

// Decode function f6 with string arg
TEST_F(TestDecoder, decodeF6)
{
    EXPECT_CALL(s0Decoder, f6(etl::string_view("Test")));
    auto response = decode({6, 'T', 'e', 's', 't', '\0'});
    EXPECT_TRUE(response.empty());
}

// Decode function f7 with custom type
TEST_F(TestDecoder, decodeF7)
{
    CompositeData expected{{0xBBAA, 0xDDCC}, 123, true};
    EXPECT_CALL(s0Decoder, f7(expected));
    auto response = decode({7, 0xAA, 0xBB, 0xCC, 0xDD, 123, 1});
    EXPECT_TRUE(response.empty());
}

// Decode function f8 with custom enum
TEST_F(TestDecoder, decodeF8)
{
    EXPECT_CALL(s0Decoder, f8(MyEnum::V3));
    auto response = decode({8, 0x03});
    EXPECT_TRUE(response.empty());
}

// Decode function f9 with array of custom type
TEST_F(TestDecoder, decodeF9)
{
    std::vector<CompositeData2> expected{
        CompositeData2{0xAA, 0xBB},
        CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(s0Decoder, f9(SPAN_EQ(expected)));
    auto response = decode({9, 0xAA, 0xBB, 0xCC, 0xDD});
    EXPECT_TRUE(response.empty());
}

// Decode function f10 with nested custom types
TEST_F(TestDecoder, decodeF10)
{
    CompositeData3 expected{{0xAA, 0xBB}};
    EXPECT_CALL(s0Decoder, f10(expected));
    auto response = decode({10, 0xAA, 0xBB});
    EXPECT_TRUE(response.empty());
}

// Decode function f11 with two uint8_t args
TEST_F(TestDecoder, decodef11)
{
    EXPECT_CALL(s0Decoder, f11(123, 111));
    auto response = decode({11, 123, 111});
    EXPECT_TRUE(response.empty());
}

// Decode function f12 which returns uint8_t
TEST_F(TestDecoder, decodef12)
{
    EXPECT_CALL(s0Decoder, f12()).WillOnce(Return(0xAB));
    auto response = decode({12});
    EXPECT_RESPONSE({0xAB}, response);
}

// Decode function f13 which returns uint16_t
TEST_F(TestDecoder, decodef13)
{
    EXPECT_CALL(s0Decoder, f13()).WillOnce(Return(0xABCD));
    auto response = decode({13});
    EXPECT_RESPONSE({0xCD, 0xAB}, response);
}

// Decode function f14 which returns float
TEST_F(TestDecoder, decodeF14)
{
    EXPECT_CALL(s0Decoder, f14()).WillOnce(Return(123.456));
    auto response = decode({14});
    EXPECT_RESPONSE({0x79, 0xE9, 0xF6, 0x42}, response);
}

// Decode function f15 which return array of uint16_t
TEST_F(TestDecoder, decodeF15)
{
    etl::array<uint16_t, 2> expected{0xBBAA, 0xDDCC};
    EXPECT_CALL(s0Decoder, f15()).WillOnce(Return(expected));
    auto response = decode({15});
    EXPECT_RESPONSE({0xAA, 0xBB, 0xCC, 0xDD}, response);
}

// Decode function f16 which returns a string
TEST_F(TestDecoder, decodeF16)
{
    EXPECT_CALL(s0Decoder, f16()).WillOnce(Return(etl::string<20>("Test")));
    auto response = decode({16});
    EXPECT_RESPONSE({'T', 'e', 's', 't', '\0'}, response);
}

// Decode function f17 which returns custom type
TEST_F(TestDecoder, decodeF17)
{
    EXPECT_CALL(s0Decoder, f17()).WillOnce(Return(CompositeData {{0xBBAA, 0xDDCC}, 123, true}));
    auto response = decode({17});
    EXPECT_RESPONSE({0xAA, 0xBB, 0xCC, 0xDD, 123, 1}, response);
}

// Decode function f18 which returns custom enum
TEST_F(TestDecoder, decodeF18)
{
    EXPECT_CALL(s0Decoder, f18()).WillOnce(Return(MyEnum::V3));
    auto response = decode({18});
    EXPECT_RESPONSE({0x03}, response);
}

// Decode function f19 which returns array of custom type
TEST_F(TestDecoder, decodeF19)
{
    etl::array<CompositeData2, 2> expected{
        CompositeData2{0xAA, 0xBB},
        CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(s0Decoder, f19()).WillOnce(Return(expected));
    auto response = decode({19});
    EXPECT_RESPONSE({0xAA, 0xBB, 0xCC, 0xDD}, response);
}

// Decode function f20 which returns nested custom types
TEST_F(TestDecoder, decodeF20)
{
    EXPECT_CALL(s0Decoder, f20()).WillOnce(Return(CompositeData3 {{0xAA, 0xBB}}));
    auto response = decode({20});
    EXPECT_RESPONSE({0xAA, 0xBB}, response);
}

// Decode function f21 which return two uint8_t args
TEST_F(TestDecoder, decodef21)
{
    EXPECT_CALL(s0Decoder, f21()).WillOnce(Return(std::tuple{123, 111}));
    auto response = decode({21});
    EXPECT_RESPONSE({123, 111}, response);
}

// Decode function f22 that takes two string arguments and returns two strings
TEST_F(TestDecoder, decodef22)
{
    etl::string_view arg1{"arg1"};
    etl::string_view arg2{"arg2"};
    etl::string<4> ret1{"ret1"};
    etl::string<4> ret2{"ret2"};

    EXPECT_CALL(s0Decoder, f22(arg1, arg2)).WillOnce(Return(std::tuple{ret1, ret2}));
    auto response = decode({22, 'a', 'r', 'g', '1', '\0', 'a', 'r', 'g', '2', '\0'});
    EXPECT_RESPONSE({'r','e','t','1','\0','r','e','t','2','\0',}, response);
}

// Decode function f6 with string arg
TEST_F(TestDecoder, decodeF6WithMissingStringTerminator)
{
    EXPECT_CALL(s0Decoder, f6(etl::string_view("Test")));
    auto response = decode({6, 'T', 'e', 's', 't'});
    EXPECT_TRUE(response.empty());
}
