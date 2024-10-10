#include "generated/Server1/Server1.hpp"
#include "generated/Server1/s0_ServiceShim.hpp"
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <tuple>

using ::testing::Return;

MATCHER_P(SPAN_EQ, e, "Equality matcher for etl::span")
{
    if (e.size() != arg.size())
    {
        return false;
    }
    for (size_t i = 0; i < e.size(); ++i)
    {
        if (e[i] != arg[i])
        {
            return false;
        }
    }
    return true;
}

class MockS0Service : public ts1::s0ServiceShim
{
public:
    MOCK_METHOD(void, f0, (), (override));
    MOCK_METHOD(void, f1, (), (override));
    MOCK_METHOD(void, f2, (uint8_t a), (override));
    MOCK_METHOD(void, f3, (uint16_t a), (override));
    MOCK_METHOD(void, f4, (float a), (override));
    MOCK_METHOD(void, f5, ((const etl::span<const uint16_t>)&a), (override));
    MOCK_METHOD(void, f6, (const etl::string_view &a), (override));
    MOCK_METHOD(void, f7, (const ts1::CompositeData &a), (override));
    MOCK_METHOD(void, f8, (ts1::MyEnum a), (override));
    MOCK_METHOD(void, f9, ((const etl::span<const ts1::CompositeData2>)&a), (override));
    MOCK_METHOD(void, f10, (const ts1::CompositeData3 &a), (override));
    MOCK_METHOD(void, f11, (uint8_t a, uint8_t b), (override));
    MOCK_METHOD(uint8_t, f12, (), (override));
    MOCK_METHOD(uint16_t, f13, (), (override));
    MOCK_METHOD(float, f14, (), (override));
    MOCK_METHOD((etl::array<uint16_t, 2>), f15, (), (override));
    MOCK_METHOD(etl::string<20>, f16, (), (override));
    MOCK_METHOD(ts1::CompositeData, f17, (), (override));
    MOCK_METHOD(ts1::MyEnum, f18, (), (override));
    MOCK_METHOD((etl::array<ts1::CompositeData2, 2>), f19, (), (override));
    MOCK_METHOD(ts1::CompositeData3, f20, (), (override));
    MOCK_METHOD((std::tuple<uint8_t, uint8_t>), f21, (), (override));
    MOCK_METHOD((std::tuple<etl::string<4>, etl::string<4>>), f22, (const etl::string_view &s1, const etl::string_view &s2), (override));
};

class TestServer1 : public ::testing::Test
{
public:
    MockS0Service s0Service;

    etl::span<uint8_t> receive(const std::vector<uint8_t> &bytes)
    {
        const etl::span<const uint8_t> s(bytes.begin(), bytes.end());

        lrpc::Service::Reader reader(s.begin(), s.end(), etl::endian::little);
        lrpc::Service::Writer writer(responseBuffer.begin(), responseBuffer.end(), etl::endian::little);
        s0Service.invoke(reader, writer);

        return {responseBuffer.begin(), writer.size_bytes()};
    }

    void EXPECT_RESPONSE(const std::vector<uint8_t> &expected, const etl::span<uint8_t> actual)
    {
        std::vector<uint8_t> actualVec{actual.begin(), actual.end()};
        EXPECT_EQ(expected, actualVec);
    }

private:
    etl::array<uint8_t, 256> responseBuffer;
};

static_assert(std::is_same<ts1::Server1, lrpc::Server<0, 100, 200>>::value, "RX and/or TX buffer size are unequal to the definition file");

// Decode void function f0. Make sure f1 is not called
TEST_F(TestServer1, decodeF0)
{
    EXPECT_CALL(s0Service, f0()).Times(1);
    EXPECT_CALL(s0Service, f1()).Times(0);

    auto response = receive({0});
    EXPECT_RESPONSE({0}, response);
}

// Decode void function f1. Make sure f0 is not called
TEST_F(TestServer1, decodeF1)
{
    EXPECT_CALL(s0Service, f0()).Times(0);
    EXPECT_CALL(s0Service, f1()).Times(1);

    auto response = receive({1});
    EXPECT_RESPONSE({1}, response);
}

// Decode function f2 with uint8_t arg
TEST_F(TestServer1, decodeF2)
{
    EXPECT_CALL(s0Service, f2(123));
    auto response = receive({2, 123});
    EXPECT_RESPONSE({2}, response);
}

// Decode function f3 with uint16_t arg
TEST_F(TestServer1, decodeF3)
{
    EXPECT_CALL(s0Service, f3(0xCDAB));
    auto response = receive({3, 0xAB, 0xCD});
    EXPECT_RESPONSE({3}, response);
}

// Decode function f4 with float arg
TEST_F(TestServer1, decodeF4)
{
    EXPECT_CALL(s0Service, f4(123.456F));
    auto response = receive({4, 0x79, 0xE9, 0xF6, 0x42});
    EXPECT_RESPONSE({4}, response);
}

// Decode function f5 with array of uint16_t arg
TEST_F(TestServer1, decodeF5)
{
    std::vector<uint16_t> expected{0xBBAA, 0xDDCC};
    EXPECT_CALL(s0Service, f5(SPAN_EQ(expected)));
    auto response = receive({5, 0xAA, 0xBB, 0xCC, 0xDD});
    EXPECT_RESPONSE({5}, response);
}

// Decode function f6 with string arg
TEST_F(TestServer1, decodeF6)
{
    EXPECT_CALL(s0Service, f6(etl::string_view("Test")));
    auto response = receive({6, 'T', 'e', 's', 't', '\0'});
    EXPECT_RESPONSE({6}, response);
}

// Decode function f7 with custom type
TEST_F(TestServer1, decodeF7)
{
    ts1::CompositeData expected{{0xBBAA, 0xDDCC}, 123, true};
    EXPECT_CALL(s0Service, f7(expected));
    auto response = receive({7, 0xAA, 0xBB, 0xCC, 0xDD, 123, 1});
    EXPECT_RESPONSE({7}, response);
}

// Decode function f8 with custom enum
TEST_F(TestServer1, decodeF8)
{
    EXPECT_CALL(s0Service, f8(ts1::MyEnum::V3));
    auto response = receive({8, 0x03});
    EXPECT_RESPONSE({8}, response);
}

// Decode function f9 with array of custom type
TEST_F(TestServer1, decodeF9)
{
    std::vector<ts1::CompositeData2> expected{
        ts1::CompositeData2{0xAA, 0xBB},
        ts1::CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(s0Service, f9(SPAN_EQ(expected)));
    auto response = receive({9, 0xAA, 0xBB, 0xCC, 0xDD});
    EXPECT_RESPONSE({9}, response);
}

// Decode function f10 with nested custom types
TEST_F(TestServer1, decodeF10)
{
    ts1::CompositeData3 expected{{0xAA, 0xBB}, ts1::MyEnum::V1};
    EXPECT_CALL(s0Service, f10(expected));
    auto response = receive({10, 0xAA, 0xBB, 0x01});
    EXPECT_RESPONSE({10}, response);
}

// Decode function f11 with two uint8_t args
TEST_F(TestServer1, decodef11)
{
    EXPECT_CALL(s0Service, f11(123, 111));
    auto response = receive({11, 123, 111});
    EXPECT_RESPONSE({11}, response);
}

// Decode function f12 which returns uint8_t
TEST_F(TestServer1, decodef12)
{
    EXPECT_CALL(s0Service, f12()).WillOnce(Return(0xAB));
    auto response = receive({12});
    EXPECT_RESPONSE({12, 0xAB}, response);
}

// Decode function f13 which returns uint16_t
TEST_F(TestServer1, decodef13)
{
    EXPECT_CALL(s0Service, f13()).WillOnce(Return(0xABCD));
    auto response = receive({13});
    EXPECT_RESPONSE({13, 0xCD, 0xAB}, response);
}

// Decode function f14 which returns float
TEST_F(TestServer1, decodeF14)
{
    EXPECT_CALL(s0Service, f14()).WillOnce(Return(123.456));
    auto response = receive({14});
    EXPECT_RESPONSE({14, 0x79, 0xE9, 0xF6, 0x42}, response);
}

// Decode function f15 which return array of uint16_t
TEST_F(TestServer1, decodeF15)
{
    etl::array<uint16_t, 2> expected{0xBBAA, 0xDDCC};
    EXPECT_CALL(s0Service, f15()).WillOnce(Return(expected));
    auto response = receive({15});
    EXPECT_RESPONSE({15, 0xAA, 0xBB, 0xCC, 0xDD}, response);
}

// Decode function f16 which returns a string
TEST_F(TestServer1, decodeF16)
{
    EXPECT_CALL(s0Service, f16()).WillOnce(Return(etl::string<20>("Test")));
    auto response = receive({16});
    EXPECT_RESPONSE({16, 'T', 'e', 's', 't', '\0'}, response);
}

// Decode function f17 which returns custom type
TEST_F(TestServer1, decodeF17)
{
    EXPECT_CALL(s0Service, f17()).WillOnce(Return(ts1::CompositeData{{0xBBAA, 0xDDCC}, 123, true}));
    auto response = receive({17});
    EXPECT_RESPONSE({17, 0xAA, 0xBB, 0xCC, 0xDD, 123, 1}, response);
}

// Decode function f18 which returns custom enum
TEST_F(TestServer1, decodeF18)
{
    EXPECT_CALL(s0Service, f18()).WillOnce(Return(ts1::MyEnum::V3));
    auto response = receive({18});
    EXPECT_RESPONSE({18, 0x03}, response);
}

// Decode function f19 which returns array of custom type
TEST_F(TestServer1, decodeF19)
{
    etl::array<ts1::CompositeData2, 2> expected{
        ts1::CompositeData2{0xAA, 0xBB},
        ts1::CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(s0Service, f19()).WillOnce(Return(expected));
    auto response = receive({19});
    EXPECT_RESPONSE({19, 0xAA, 0xBB, 0xCC, 0xDD}, response);
}

// Decode function f20 which returns nested custom types
TEST_F(TestServer1, decodeF20)
{
    EXPECT_CALL(s0Service, f20()).WillOnce(Return(ts1::CompositeData3{{0xAA, 0xBB}, ts1::MyEnum::V2}));
    auto response = receive({20});
    EXPECT_RESPONSE({20, 0xAA, 0xBB, 0x02}, response);
}

// Decode function f21 which return two uint8_t args
TEST_F(TestServer1, decodef21)
{
    EXPECT_CALL(s0Service, f21()).WillOnce(Return(std::tuple<uint8_t, uint8_t>{123, 111}));
    auto response = receive({21});
    EXPECT_RESPONSE({21, 123, 111}, response);
}

// Decode function f22 that takes two string arguments and returns two strings
TEST_F(TestServer1, decodef22)
{
    etl::string_view arg1{"arg1"};
    etl::string_view arg2{"arg2"};
    etl::string<4> ret1{"ret1"};
    etl::string<4> ret2{"ret2"};

    EXPECT_CALL(s0Service, f22(arg1, arg2)).WillOnce(Return(std::tuple<etl::string<4>, etl::string<4>>{ret1, ret2}));
    auto response = receive({22, 'a', 'r', 'g', '1', '\0', 'a', 'r', 'g', '2', '\0'});
    EXPECT_RESPONSE({
                        22,
                        'r',
                        'e',
                        't',
                        '1',
                        '\0',
                        'r',
                        'e',
                        't',
                        '2',
                        '\0',
                    },
                    response);
}

// Decode function f6 with string arg
TEST_F(TestServer1, decodeF6WithMissingStringTerminator)
{
    EXPECT_CALL(s0Service, f6(etl::string_view("Test")));
    auto response = receive({6, 'T', 'e', 's', 't'});
    EXPECT_RESPONSE({6}, response);
}
