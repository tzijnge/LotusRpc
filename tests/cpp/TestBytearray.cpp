#include "generated/Bytearray/Bytearray.hpp"
#include "TestUtils.hpp"

using ::testing::Return;

namespace
{
    class Bytearrayservice : public test_ba::bytearray_shim
    {
    public:
        MOCK_METHOD((lrpc::bytearray_t), param_return, (lrpc::bytearray_t), (override));
        MOCK_METHOD((std::tuple<lrpc::bytearray_t, lrpc::bytearray_t>), param_return_multiple, (lrpc::bytearray_t p0, lrpc::bytearray_t), (override));
        MOCK_METHOD((etl::optional<lrpc::bytearray_t>), optional, (etl::optional<lrpc::bytearray_t>), (override));
        MOCK_METHOD((etl::span<const lrpc::bytearray_t>), array, (etl::span<const lrpc::bytearray_t>), (override));
        MOCK_METHOD(test_ba::BytearrayStruct, custom, (const test_ba::BytearrayStruct &), (override));

        // client streams
        MOCK_METHOD(void, client_single, (lrpc::bytearray_t), (override));
        MOCK_METHOD(void, client_multiple, (lrpc::bytearray_t, lrpc::bytearray_t), (override));
        MOCK_METHOD(void, client_optional, (etl::optional<lrpc::bytearray_t>), (override));
        MOCK_METHOD(void, client_array, (etl::span<const lrpc::bytearray_t>), (override));
        MOCK_METHOD(void, client_custom, (const test_ba::BytearrayStruct &), (override));

        // server streams
        MOCK_METHOD(void, server_single, (), (override));
        MOCK_METHOD(void, server_single_stop, (), (override));
        MOCK_METHOD(void, server_multiple, (), (override));
        MOCK_METHOD(void, server_multiple_stop, (), (override));
        MOCK_METHOD(void, server_optional, (), (override));
        MOCK_METHOD(void, server_optional_stop, (), (override));
        MOCK_METHOD(void, server_array, (), (override));
        MOCK_METHOD(void, server_array_stop, (), (override));
        MOCK_METHOD(void, server_custom, (), (override));
        MOCK_METHOD(void, server_custom_stop, (), (override));
    };
}

using TestBytearray = testutils::TestServerBase<test_ba::Bytearray, Bytearrayservice>;

TEST_F(TestBytearray, param_return)
{
    const std::vector<uint8_t> p0{0x11, 0x22, 0x33};
    const std::vector<uint8_t> r0{0x44, 0x55, 0x66};
    EXPECT_CALL(service, param_return(testutils::SPAN_EQ(p0))).WillOnce(Return(r0));
    const auto response = receive("07000003112233");
    EXPECT_EQ("07000003445566", response);
}

TEST_F(TestBytearray, param_return_multiple)
{
    const std::vector<uint8_t> p0{0x11, 0x22, 0x33};
    const std::vector<uint8_t> p1{0x44, 0x55};
    const std::vector<uint8_t> r0{0x66, 0x77, 0x88};
    const std::vector<uint8_t> r1{0x99, 0xAA};
    EXPECT_CALL(service,
                param_return_multiple(testutils::SPAN_EQ(p0), testutils::SPAN_EQ(p1)))
        .WillOnce(Return(std::tuple<lrpc::bytearray_t, lrpc::bytearray_t>{r0, r1}));
    const auto response = receive("0A000103112233024455");
    EXPECT_EQ("0A0001036677880299AA", response);
}

TEST_F(TestBytearray, optional)
{
    etl::array<uint8_t, 3> data0{0x11, 0x22, 0x33};
    const etl::optional<lrpc::bytearray_t> p0{data0};
    etl::array<uint8_t, 3> data1{0x44, 0x55, 0x66};
    const etl::optional<lrpc::bytearray_t> r0{data1};
    EXPECT_CALL(service, optional(testutils::OPT_SPAN_EQ(p0))).WillOnce(Return(r0));
    const auto response = receive("0800020103112233");
    EXPECT_EQ("0800020103445566", response);
}

TEST_F(TestBytearray, array)
{
    etl::array<uint8_t, 2> ba0{0xA1, 0xA2};
    etl::array<uint8_t, 3> ba1{0xA3, 0xA4, 0xA5};
    etl::array<lrpc::bytearray_t, 2> r0{ba0, ba1};

    const auto handler = [&](etl::span<const lrpc::bytearray_t> ba)
    {
        EXPECT_EQ(2, ba.size());
        EXPECT_EQ(3, ba.at(0).size());
        EXPECT_EQ(0x11, ba.at(0).at(0));
        EXPECT_EQ(0x22, ba.at(0).at(1));
        EXPECT_EQ(0x33, ba.at(0).at(2));
        EXPECT_EQ(2, ba.at(1).size());
        EXPECT_EQ(0x44, ba.at(1).at(0));
        EXPECT_EQ(0x55, ba.at(1).at(1));

        return r0;
    };

    EXPECT_CALL(service, array(testing::_)).WillOnce(testing::Invoke(handler));
    const auto response = receive("0A000303112233024455");
    EXPECT_EQ("0A000302A1A203A3A4A5", response);
}

TEST_F(TestBytearray, custom)
{
    etl::array<uint8_t, 3> ba4{0xA1, 0xA2, 0xA3};
    etl::array<uint8_t, 2> ba5{0xA4, 0xA5};
    etl::array<uint8_t, 2> ba6{0xA6, 0xA7};
    etl::array<uint8_t, 1> ba7{0xA8};

    const auto handler = [&](const test_ba::BytearrayStruct &bas)
    {
        EXPECT_EQ(2, bas.f0.size());
        EXPECT_EQ(0x11, bas.f0.at(0));
        EXPECT_EQ(0x22, bas.f0.at(1));
        EXPECT_TRUE(bas.f1.has_value());
        EXPECT_EQ(0x33, bas.f1.value().at(0));
        EXPECT_EQ(0x44, bas.f1.value().at(1));
        EXPECT_EQ(0x55, bas.f1.value().at(2));
        EXPECT_EQ(2, bas.f2.size());
        EXPECT_EQ(1, bas.f2.at(0).size());
        EXPECT_EQ(0x66, bas.f2.at(0).at(0));
        EXPECT_EQ(2, bas.f2.at(1).size());
        EXPECT_EQ(0x77, bas.f2.at(1).at(0));
        EXPECT_EQ(0x88, bas.f2.at(1).at(1));

        return test_ba::BytearrayStruct{ba4, etl::optional<lrpc::bytearray_t>{ba5}, {ba6, ba7}};
    };

    EXPECT_CALL(service, custom(testing::_)).WillOnce(testing::Invoke(handler));
    const auto response = receive("10000402112201033344550166027788");
    EXPECT_EQ("10000403A1A2A30102A4A502A6A701A8", response);
}

TEST_F(TestBytearray, client_single)
{
    const std::vector<uint8_t> p0{0x11, 0x22, 0x33};
    EXPECT_CALL(service, client_single(testutils::SPAN_EQ(p0)));

    const auto response = receive("07000503112233");
    EXPECT_EQ("", response);
}

TEST_F(TestBytearray, client_multiple)
{
    const std::vector<uint8_t> p0{0x11, 0x22, 0x33};
    const std::vector<uint8_t> p1{0x44, 0x55};
    EXPECT_CALL(service, client_multiple(testutils::SPAN_EQ(p0), testutils::SPAN_EQ(p1)));

    const auto response = receive("0A000603112233024455");
    EXPECT_EQ("", response);
}

TEST_F(TestBytearray, client_optional)
{
    etl::array<uint8_t, 3> data0{0x11, 0x22, 0x33};
    const etl::optional<lrpc::bytearray_t> p0{data0};
    EXPECT_CALL(service, client_optional(testutils::OPT_SPAN_EQ(p0)));
    const auto response = receive("0800070103112233");
    EXPECT_EQ("", response);
}

TEST_F(TestBytearray, client_array)
{
    const auto handler = [&](etl::span<const lrpc::bytearray_t> ba)
    {
        EXPECT_EQ(2, ba.size());
        EXPECT_EQ(3, ba.at(0).size());
        EXPECT_EQ(0x11, ba.at(0).at(0));
        EXPECT_EQ(0x22, ba.at(0).at(1));
        EXPECT_EQ(0x33, ba.at(0).at(2));
        EXPECT_EQ(2, ba.at(1).size());
        EXPECT_EQ(0x44, ba.at(1).at(0));
        EXPECT_EQ(0x55, ba.at(1).at(1));
    };

    EXPECT_CALL(service, client_array(testing::_)).WillOnce(testing::Invoke(handler));
    const auto response = receive("0A000803112233024455");
    EXPECT_EQ("", response);
}

TEST_F(TestBytearray, client_custom)
{
    const auto handler = [&](const test_ba::BytearrayStruct &bas)
    {
        EXPECT_EQ(2, bas.f0.size());
        EXPECT_EQ(0x11, bas.f0.at(0));
        EXPECT_EQ(0x22, bas.f0.at(1));
        EXPECT_TRUE(bas.f1.has_value());
        EXPECT_EQ(0x33, bas.f1.value().at(0));
        EXPECT_EQ(0x44, bas.f1.value().at(1));
        EXPECT_EQ(0x55, bas.f1.value().at(2));
        EXPECT_EQ(2, bas.f2.size());
        EXPECT_EQ(1, bas.f2.at(0).size());
        EXPECT_EQ(0x66, bas.f2.at(0).at(0));
        EXPECT_EQ(2, bas.f2.at(1).size());
        EXPECT_EQ(0x77, bas.f2.at(1).at(0));
        EXPECT_EQ(0x88, bas.f2.at(1).at(1));
    };

    EXPECT_CALL(service, client_custom(testing::_)).WillOnce(testing::Invoke(handler));
    const auto response = receive("10000902112201033344550166027788");
    EXPECT_EQ("", response);
}

TEST_F(TestBytearray, server_single)
{
    const std::vector<uint8_t> p0{0x11, 0x22, 0x33};
    service.server_single_response(p0);
    EXPECT_EQ("07000A03112233", response());
}

TEST_F(TestBytearray, server_multiple)
{
    const std::vector<uint8_t> p0{0x11, 0x22, 0x33};
    const std::vector<uint8_t> p1{0x44, 0x55};
    service.server_multiple_response(p0, p1);
    EXPECT_EQ("0A000B03112233024455", response());
}

TEST_F(TestBytearray, server_optional)
{
    const std::vector<uint8_t> p0{0x11, 0x22, 0x33};
    service.server_optional_response({p0});
    EXPECT_EQ("08000C0103112233", response());
}

TEST_F(TestBytearray, server_array)
{
    const std::vector<uint8_t> a0{0x11, 0x22, 0x33};
    const std::vector<uint8_t> a1{0x44, 0x55};
    const std::vector<lrpc::bytearray_t> p0{a0, a1};
    service.server_array_response(p0);
    EXPECT_EQ("0A000D03112233024455", response());
}

TEST_F(TestBytearray, server_custom)
{
    etl::array<uint8_t, 3> ba4{0xA1, 0xA2, 0xA3};
    etl::array<uint8_t, 2> ba5{0xA4, 0xA5};
    etl::array<uint8_t, 2> ba6{0xA6, 0xA7};
    etl::array<uint8_t, 1> ba7{0xA8};

    service.server_custom_response(test_ba::BytearrayStruct{ba4, ba5, {ba6, ba7}});
    EXPECT_EQ("10000E03A1A2A30102A4A502A6A701A8", response());
}