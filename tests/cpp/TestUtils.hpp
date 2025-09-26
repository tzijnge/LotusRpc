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

inline std::string bytesToHex(const etl::span<const uint8_t> bytes)
{
    std::stringstream ss;
    ss << std::hex << std::setfill('0') << std::uppercase;

    for (const auto b : bytes)
    {
        ss << std::setw(2) << static_cast<uint32_t>(b);
    }

    return ss.str();
}

template <typename Server, typename Service>
class TestServerBase : public Server, public ::testing::Test
{
public:
    void SetUp() final
    {
        Server::registerService(service);
    }

    void lrpcTransmit(etl::span<const uint8_t> bytes) override
    {
        responseBuffer = bytes;
    }

    std::string receive(const etl::string_view hex)
    {
        Server::lrpcReceive(testutils::hexToBytes(hex));
        return response();
    }

    std::string response() const
    {
        return testutils::bytesToHex(responseBuffer);
    }

    etl::span<const uint8_t> responseBuffer;

    Service service;
};
}