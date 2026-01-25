#include "TestUtils.hpp"
#include "generated/Bytearray/Bytearray.hpp"

using ::testing::Return;

class TEST_BYTEARRY_SERVICE : public test_ba::bytearray_shim
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

namespace
{
    template <typename... Ts>
    std::vector<LRPC_BYTE_TYPE> makeBytes(Ts &&...args) noexcept
    {
        return {static_cast<LRPC_BYTE_TYPE>(std::forward<Ts>(args))...};
    }
}

using TEST_BYTEARRAY_CLASS = testutils::TestServerBase<test_ba::Bytearray, TEST_BYTEARRY_SERVICE>;

TEST_F(TEST_BYTEARRAY_CLASS, param_return)
{
    const auto p0 = makeBytes(0x11, 0x22, 0x33);
    const auto r0 = makeBytes(0x44, 0x55, 0x66);
    EXPECT_CALL(service, param_return(testutils::SPAN_EQ(p0))).WillOnce(Return(r0));
    const auto response = receive("07000003112233");
    EXPECT_EQ("07000003445566", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, param_return_multiple)
{
    const auto p0 = makeBytes(0x11, 0x22, 0x33);
    const auto p1 = makeBytes(0x44, 0x55);
    const auto r0 = makeBytes(0x61, 0x62, 0x63);
    const auto r1 = makeBytes(0x64, 0x65);
    EXPECT_CALL(service,
                param_return_multiple(testutils::SPAN_EQ(p0), testutils::SPAN_EQ(p1)))
        .WillOnce(Return(std::tuple<lrpc::bytearray_t, lrpc::bytearray_t>{r0, r1}));
    const auto response = receive("0A000103112233024455");
    EXPECT_EQ("0A000103616263026465", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, optional)
{
    const auto data0 = makeBytes(0x11, 0x22, 0x33);
    const etl::optional<lrpc::bytearray_t> p0{data0};
    const auto data1 = makeBytes(0x44, 0x55, 0x66);
    const etl::optional<lrpc::bytearray_t> r0{data1};
    EXPECT_CALL(service, optional(testutils::OPT_SPAN_EQ(p0))).WillOnce(Return(r0));
    const auto response = receive("0800020103112233");
    EXPECT_EQ("0800020103445566", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, array)
{
    const auto ba0 = makeBytes(0x71, 0x72);
    const auto ba1 = makeBytes(0x73, 0x74, 0x75);
    const std::vector<lrpc::bytearray_t> r0{ba0, ba1};

    const auto handler = [r0](etl::span<const lrpc::bytearray_t> ba)
    {
        EXPECT_EQ(2, ba.size());
        EXPECT_EQ(3, ba.at(0).size());
        EXPECT_EQ(0x11, ba.at(0).at(0));
        EXPECT_EQ(0x22, ba.at(0).at(1));
        EXPECT_EQ(0x33, ba.at(0).at(2));
        EXPECT_EQ(2, ba.at(1).size());
        EXPECT_EQ(0x44, ba.at(1).at(0));
        EXPECT_EQ(0x55, ba.at(1).at(1));

        return etl::span<const lrpc::bytearray_t>{r0};
    };

    EXPECT_CALL(service, array(testing::_)).WillOnce(testing::Invoke(handler));
    const auto response = receive("0A000303112233024455");
    EXPECT_EQ("0A000302717203737475", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, custom)
{
    const auto ba4 = makeBytes(0x71, 0x72, 0x73);
    const auto ba5 = makeBytes(0x74, 0x75);
    const auto ba6 = makeBytes(0x76, 0x77);
    const auto ba7 = makeBytes(0x78);

    const auto handler = [ba4, ba5, ba6, ba7](const test_ba::BytearrayStruct &bas)
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
        EXPECT_EQ(0x78, bas.f2.at(1).at(1));

        return test_ba::BytearrayStruct{ba4, etl::optional<lrpc::bytearray_t>{ba5}, {ba6, ba7}};
    };

    EXPECT_CALL(service, custom(testing::_)).WillOnce(testing::Invoke(handler));
    const auto response = receive("10000402112201033344550166027778");
    EXPECT_EQ("10000403717273010274750276770178", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, client_single)
{
    const auto p0 = makeBytes(0x11, 0x22, 0x33);
    EXPECT_CALL(service, client_single(testutils::SPAN_EQ(p0)));

    const auto response = receive("07000503112233");
    EXPECT_EQ("", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, client_multiple)
{
    const auto p0 = makeBytes(0x11, 0x22, 0x33);
    const auto p1 = makeBytes(0x44, 0x55);
    EXPECT_CALL(service, client_multiple(testutils::SPAN_EQ(p0), testutils::SPAN_EQ(p1)));

    const auto response = receive("0A000603112233024455");
    EXPECT_EQ("", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, client_optional)
{
    const auto data0 = makeBytes(0x11, 0x22, 0x33);
    const etl::optional<lrpc::bytearray_t> p0{data0};
    EXPECT_CALL(service, client_optional(testutils::OPT_SPAN_EQ(p0)));
    const auto response = receive("0800070103112233");
    EXPECT_EQ("", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, client_array)
{
    const auto handler = [](etl::span<const lrpc::bytearray_t> ba)
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

TEST_F(TEST_BYTEARRAY_CLASS, client_custom)
{
    const auto handler = [](const test_ba::BytearrayStruct &bas)
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
        EXPECT_EQ(0x78, bas.f2.at(1).at(1));
    };

    EXPECT_CALL(service, client_custom(testing::_)).WillOnce(testing::Invoke(handler));
    const auto response = receive("10000902112201033344550166027778");
    EXPECT_EQ("", response);
}

TEST_F(TEST_BYTEARRAY_CLASS, server_single)
{
    const auto p0 = makeBytes(0x11, 0x22, 0x33);
    service.server_single_response(p0);
    EXPECT_EQ("07000A03112233", response());
}

TEST_F(TEST_BYTEARRAY_CLASS, server_multiple)
{
    const auto p0 = makeBytes(0x11, 0x22, 0x33);
    const auto p1 = makeBytes(0x44, 0x55);
    service.server_multiple_response(p0, p1);
    EXPECT_EQ("0A000B03112233024455", response());
}

TEST_F(TEST_BYTEARRAY_CLASS, server_optional)
{
    const auto p0 = makeBytes(0x11, 0x22, 0x33);
    service.server_optional_response({p0});
    EXPECT_EQ("08000C0103112233", response());
}

TEST_F(TEST_BYTEARRAY_CLASS, server_array)
{
    const auto a0 = makeBytes(0x11, 0x22, 0x33);
    const auto a1 = makeBytes(0x44, 0x55);
    const std::vector<lrpc::bytearray_t> p0{a0, a1};
    service.server_array_response(p0);
    EXPECT_EQ("0A000D03112233024455", response());
}

TEST_F(TEST_BYTEARRAY_CLASS, server_custom)
{
    const auto ba4 = makeBytes(0x71, 0x72, 0x73);
    const auto ba5 = makeBytes(0x74, 0x75);
    const auto ba6 = makeBytes(0x76, 0x77);
    const auto ba7 = makeBytes(0x78);

    service.server_custom_response(test_ba::BytearrayStruct{ba4, etl::optional<lrpc::bytearray_t>{ba5}, {ba6, ba7}});
    EXPECT_EQ("10000E03717273010274750276770178", response());
}