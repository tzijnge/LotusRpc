#include "generated/Server1/Server1.hpp"
#include "TestUtils.hpp"

using ::testing::Return;
namespace
{
class Mockservice : public ts1::s0ServiceShim
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
    MOCK_METHOD(etl::string<8>, f16, (), (override));
    MOCK_METHOD(ts1::CompositeData, f17, (), (override));
    MOCK_METHOD(ts1::MyEnum, f18, (), (override));
    MOCK_METHOD((etl::array<ts1::CompositeData2, 2>), f19, (), (override));
    MOCK_METHOD(ts1::CompositeData3, f20, (), (override));
    MOCK_METHOD((std::tuple<uint8_t, uint8_t>), f21, (), (override));
    MOCK_METHOD((std::tuple<etl::string<4>, etl::string<4>>), f22, (const etl::string_view &s1, const etl::string_view &s2), (override));
    MOCK_METHOD(etl::string_view, f23, (), (override));
    MOCK_METHOD((std::tuple<etl::string_view, etl::string_view>), f24, (), (override));
    MOCK_METHOD((etl::optional<etl::string_view>), f25, (), (override));
    MOCK_METHOD((etl::array<etl::string_view, 3>), f26, (), (override));
};
}

using TestServer1 = testutils::TestServerBase<ts1::Server1, Mockservice>;

static_assert(std::is_same<ts1::Server1, lrpc::Server<0, 100, 200>>::value, "RX and/or TX buffer size are unequal to the definition file");

// Decode void function f0. Make sure f1 is not called
TEST_F(TestServer1, decodeF0)
{
    EXPECT_CALL(service, f0()).Times(1);
    EXPECT_CALL(service, f1()).Times(0);

    const auto response = receive("030000");
    EXPECT_EQ("030000", response);
}

// Decode void function f1. Make sure f0 is not called
TEST_F(TestServer1, decodeF1)
{
    EXPECT_CALL(service, f0()).Times(0);
    EXPECT_CALL(service, f1()).Times(1);

    const auto response = receive("030001");
    EXPECT_EQ("030001", response);
}

// Decode function f2 with uint8_t arg
TEST_F(TestServer1, decodeF2)
{
    EXPECT_CALL(service, f2(0x7B));
    const auto response = receive("0400027B");
    EXPECT_EQ("030002", response);
}

// Decode function f3 with uint16_t arg
TEST_F(TestServer1, decodeF3)
{
    EXPECT_CALL(service, f3(0xCDAB));
    const auto response = receive("050003ABCD");
    EXPECT_EQ("030003", response);
}

// Decode function f4 with float arg
TEST_F(TestServer1, decodeF4)
{
    EXPECT_CALL(service, f4(123.456F));
    const auto response = receive("07000479E9F642");
    EXPECT_EQ("030004", response);
}

// Decode function f5 with array of uint16_t arg
TEST_F(TestServer1, decodeF5)
{
    std::vector<uint16_t> expected{0xBBAA, 0xDDCC};
    EXPECT_CALL(service, f5(testutils::SPAN_EQ(expected)));
    const auto response = receive("070005AABBCCDD");
    EXPECT_EQ("030005", response);
}

// Decode function f6 with string arg
TEST_F(TestServer1, decodeF6)
{
    EXPECT_CALL(service, f6(etl::string_view("Test")));
    const auto response = receive("0800065465737400");
    EXPECT_EQ("030006", response);
}

// Decode function f6 with string arg and missing terminator
TEST_F(TestServer1, decodeF6WithMissingStringTerminator)
{
    EXPECT_CALL(service, f6(etl::string_view("Test")));
    const auto response = receive("07000654657374");
    EXPECT_EQ("030006", response);
}

// Decode function f7 with custom type
TEST_F(TestServer1, decodeF7)
{
    ts1::CompositeData expected{{0xBBAA, 0xDDCC}, 123, true};
    EXPECT_CALL(service, f7(expected));
    const auto response = receive("090007AABBCCDD7B01");
    EXPECT_EQ("030007", response);
}

// Decode function f8 with custom enum
TEST_F(TestServer1, decodeF8)
{
    EXPECT_CALL(service, f8(ts1::MyEnum::V3));
    const auto response = receive("04000803");
    EXPECT_EQ("030008", response);
}

// Decode function f9 with array of custom type
TEST_F(TestServer1, decodeF9)
{
    std::vector<ts1::CompositeData2> expected{
        ts1::CompositeData2{0xAA, 0xBB},
        ts1::CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(service, f9(testutils::SPAN_EQ(expected)));
    const auto response = receive("070009AABBCCDD");
    EXPECT_EQ("030009", response);
}

// Decode function f10 with nested custom types
TEST_F(TestServer1, decodeF10)
{
    ts1::CompositeData3 expected{{0xAA, 0xBB}, ts1::MyEnum::V1};
    EXPECT_CALL(service, f10(expected));
    const auto response = receive("06000AAABB01");
    EXPECT_EQ("03000A", response);
}

// Decode function f11 with two uint8_t args
TEST_F(TestServer1, decodef11)
{
    EXPECT_CALL(service, f11(0x7B, 0x6F));
    const auto response = receive("05000B7B6F");
    EXPECT_EQ("03000B", response);
}

// Decode function f12 which returns uint8_t
TEST_F(TestServer1, decodef12)
{
    EXPECT_CALL(service, f12()).WillOnce(Return(0xAB));
    const auto response = receive("03000C");
    EXPECT_EQ("04000CAB", response);
}

// Decode function f13 which returns uint16_t
TEST_F(TestServer1, decodef13)
{
    EXPECT_CALL(service, f13()).WillOnce(Return(0xABCD));
    const auto response = receive("03000D");
    EXPECT_EQ("05000DCDAB", response);
}

// Decode function f14 which returns float
TEST_F(TestServer1, decodeF14)
{
    EXPECT_CALL(service, f14()).WillOnce(Return(123.456));
    const auto response = receive("03000E");
    EXPECT_EQ("07000E79E9F642", response);
}

// Decode function f15 which return array of uint16_t
TEST_F(TestServer1, decodeF15)
{
    etl::array<uint16_t, 2> expected{0xBBAA, 0xDDCC};
    EXPECT_CALL(service, f15()).WillOnce(Return(expected));
    const auto response = receive("03000F");
    EXPECT_EQ("07000FAABBCCDD", response);
}

// Decode function f16 which returns a string
TEST_F(TestServer1, decodeF16)
{
    EXPECT_CALL(service, f16()).WillOnce(Return(etl::string<8>("Test")));
    const auto response = receive("030010");
    EXPECT_EQ("0C0010546573740000000000", response);
}

// Decode function f17 which returns custom type
TEST_F(TestServer1, decodeF17)
{
    EXPECT_CALL(service, f17()).WillOnce(Return(ts1::CompositeData{{0xBBAA, 0xDDCC}, 0x7B, true}));
    const auto response = receive("030011");
    EXPECT_EQ("090011AABBCCDD7B01", response);
}

// Decode function f18 which returns custom enum
TEST_F(TestServer1, decodeF18)
{
    EXPECT_CALL(service, f18()).WillOnce(Return(ts1::MyEnum::V3));
    const auto response = receive("030012");
    EXPECT_EQ("04001203", response);
}

// Decode function f19 which returns array of custom type
TEST_F(TestServer1, decodeF19)
{
    etl::array<ts1::CompositeData2, 2> expected{
        ts1::CompositeData2{0xAA, 0xBB},
        ts1::CompositeData2{0xCC, 0xDD}};
    EXPECT_CALL(service, f19()).WillOnce(Return(expected));
    const auto response = receive("030013");
    EXPECT_EQ("070013AABBCCDD", response);
}

// Decode function f20 which returns nested custom types
TEST_F(TestServer1, decodeF20)
{
    EXPECT_CALL(service, f20()).WillOnce(Return(ts1::CompositeData3{{0xAA, 0xBB}, ts1::MyEnum::V2}));
    const auto response = receive("030014");
    EXPECT_EQ("060014AABB02", response);
}

// Decode function f21 which return two uint8_t args
TEST_F(TestServer1, decodef21)
{
    EXPECT_CALL(service, f21()).WillOnce(Return(std::tuple<uint8_t, uint8_t>{0x7B, 0x6F}));
    const auto response = receive("030015");
    EXPECT_EQ("0500157B6F", response);
}

// Decode function f22 that takes two string arguments and returns two strings
TEST_F(TestServer1, decodef22)
{
    etl::string_view arg1{"arg1"};
    etl::string_view arg2{"arg2"};
    etl::string<4> ret1{"ret1"};
    etl::string<4> ret2{"ret2"};

    EXPECT_CALL(service, f22(arg1, arg2)).WillOnce(Return(std::tuple<etl::string<4>, etl::string<4>>{ret1, ret2}));
    const auto response = receive("0D001661726731006172673200");
    EXPECT_EQ("0D001672657431007265743200", response);
}

// Decode function that returns auto string
TEST_F(TestServer1, decodef23)
{
    EXPECT_CALL(service, f23()).WillOnce(Return(etl::string_view("Test")));
    const auto response = receive("030017");
    EXPECT_EQ("0800175465737400", response);
}

// Decode function that returns two auto strings
TEST_F(TestServer1, decodef24)
{
    EXPECT_CALL(service, f24()).WillOnce(Return(std::tuple<etl::string_view, etl::string_view>{"T1", "T2"}));
    const auto response = receive("030018");
    EXPECT_EQ("090018543100543200", response);
}

// Decode function that returns optional auto string
TEST_F(TestServer1, decodef25)
{
    EXPECT_CALL(service, f25()).WillOnce(Return(etl::optional<etl::string_view>{"T1"}));
    auto response = receive("030019");
    EXPECT_EQ("07001901543100", response);

    EXPECT_CALL(service, f25()).WillOnce(Return(etl::optional<etl::string_view>{}));
    response = receive("030019");
    EXPECT_EQ("04001900", response);
}

// Decode function that returns array of auto string
TEST_F(TestServer1, decodef26)
{
    EXPECT_CALL(service, f26()).WillOnce(Return(etl::array<etl::string_view, 3>{"Test1", "T2", "T3"}));
    const auto response = receive("03001A");
    EXPECT_EQ("0F001A546573743100543200543300", response);
}
