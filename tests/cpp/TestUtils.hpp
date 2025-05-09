#pragma once

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <etl/to_arithmetic.h>
#include <etl/array.h>
#include <etl/span.h>

namespace testutils
{

#ifdef _MSC_VER
# pragma warning(push)
# pragma warning(disable:4100)
#endif

MATCHER_P(SPAN_EQ, e, "Equality matcher for etl::span")
{
    if (e.size() != arg.size())
    {
        return false;
    }

    const auto size = e.size();
    for (size_t i = 0; i < size; ++i)
    {
        if (e[i] != arg[i])
        {
            return false;
        }
    }
    return true;
}

#ifdef _MSC_VER
# pragma warning(pop)
#endif

inline std::vector<uint8_t> hexToBytes(const etl::string_view hex)
{
    if ((hex.size() % 2) != 0)
    {
        return {};
    }

    const auto numberBytes = hex.size() / 2;

    std::vector<uint8_t> bytes;

    for (auto i = 0U; i < numberBytes; i += 1)
    {
        bytes.emplace_back(etl::to_arithmetic<uint8_t>(hex.substr(i * 2, 2), etl::hex));
    }

    return bytes;
}

template <typename Service>
class TestServerBase : public ::testing::Test
{
public:
    void SetUp() final
    {
        responseBuffer.fill(0xAA);
    }

    etl::span<uint8_t> receive(const etl::string_view hex)
    {
        return receive(testutils::hexToBytes(hex));
    }


    etl::span<uint8_t> receive(const std::vector<uint8_t> &bytes)
    {
        const etl::span<const uint8_t> s(bytes.begin(), bytes.end());

        lrpc::Service::Reader reader(s.begin(), s.end(), etl::endian::little);
        lrpc::Service::Writer writer(responseBuffer.begin(), responseBuffer.end(), etl::endian::little);
        auto invokeOk = service.invoke(reader, writer);

        EXPECT_TRUE(invokeOk);

        return {responseBuffer.begin(), writer.size_bytes()};
    }

    void EXPECT_RESPONSE(const etl::string_view expected, const etl::span<uint8_t> actual) const
    {
        const std::vector<uint8_t> actualVec{actual.begin(), actual.end()};
        EXPECT_EQ(testutils::hexToBytes(expected), actualVec);
    }

    etl::array<uint8_t, 256> responseBuffer {};

    Service service;
};
}