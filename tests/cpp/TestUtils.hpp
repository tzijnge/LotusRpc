#pragma once

#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <etl/to_arithmetic.h>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "LrpcTypes.hpp"

namespace testutils
{
    template <typename T>
    constexpr bool areClose(const T first, const T second, const T tolerance)
    {
        return ((first - second) < tolerance) && ((first - second) > -tolerance);
    }

    class InvalidHexString : public std::runtime_error
    {
    public:
        InvalidHexString()
            : runtime_error("Invalid hex string")
        {
        }
    };

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable : 4100)
#endif

    // NOLINTBEGIN(cppcoreguidelines-avoid-const-or-ref-data-members)
    MATCHER_P(SPAN_EQ, ex, "Equality matcher for lrpc::span")
    {
        if (ex.size() != arg.size())
        {
            return false;
        }

        const auto size = ex.size();
        for (size_t i = 0; i < size; ++i)
        {
            if (ex.at(i) != arg.at(i))
            {
                return false;
            }
        }
        return true;
    }
    // NOLINTEND(cppcoreguidelines-avoid-const-or-ref-data-members)

    // NOLINTBEGIN(cppcoreguidelines-avoid-const-or-ref-data-members)
    MATCHER_P(OPT_SPAN_EQ, ex, "Equality matcher for lrpc::optional of lrpc::span")
    {
        if (ex.has_value() != arg.has_value())
        {
            return false;
        }

        if (!ex.has_value())
        {
            return true;
        }

        if (ex.value().size() != arg.value().size())
        {
            return false;
        }

        const auto size = ex.value().size();
        for (size_t i = 0; i < size; ++i)
        {
            if (ex.value().at(i) != arg.value().at(i))
            {
                return false;
            }
        }
        return true;
    }
    // NOLINTEND(cppcoreguidelines-avoid-const-or-ref-data-members)

#ifdef _MSC_VER
#pragma warning(pop)
#endif

    inline std::vector<uint8_t> hexToBytes(const lrpc::string_view hex)
    {
        if ((hex.size() % 2) != 0)
        {
            throw InvalidHexString();
        }

        const auto numberBytes = hex.size() / 2;

        std::vector<uint8_t> bytes;

        for (size_t i = 0; i < numberBytes; i += 1)
        {
            const auto result = etl::to_arithmetic<uint8_t>(hex.substr(i * 2U, 2U), etl::hex);
            if (result.has_value())
            {
                bytes.emplace_back(result.value());
            }
            else
            {
                throw InvalidHexString();
            }
        }

        return bytes;
    }

    inline std::string bytesToHex(const lrpc::span<const uint8_t> bytes)
    {
        std::stringstream ss;
        ss << std::hex << std::setfill('0') << std::uppercase;

        for (const auto byteVal : bytes)
        {
            ss << std::setw(2) << static_cast<uint32_t>(byteVal);
        }

        return ss.str();
    }

    template <typename Server, typename Service, bool AutoReset = true>
    // NOLINTNEXTLINE(misc-multiple-inheritance)
    class TestServerBase : public Server, public ::testing::Test
    {
    public:
        void lrpcTransmit(lrpc::span<const uint8_t> bytes) override
        {
            if (AutoReset)
            {
                responseBuffer.clear();
            }
            (void)responseBuffer.insert(responseBuffer.end(), bytes.begin(), bytes.end());
        }

        std::string receive(const lrpc::string_view hex)
        {
            Server::lrpcReceive(testutils::hexToBytes(hex));
            return response();
        }

        std::string response() const { return testutils::bytesToHex(responseBuffer); }

        std::vector<uint8_t> responseBuffer;
        Service service;

    protected:
        void SetUp() final { Server::registerService(service); }
    };
}