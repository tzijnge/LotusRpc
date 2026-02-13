#pragma once

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <etl/to_arithmetic.h>
#include <etl/array.h>
#include <etl/span.h>
#include <vector>
#include <stdexcept>
#include <sstream>
#include <iomanip>
#include <string>

namespace testutils
{

    class InvalidHexString : public std::runtime_error
    {
    public:
        InvalidHexString() : runtime_error("Invalid hex string") {}
    };

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable : 4100)
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

    MATCHER_P(OPT_SPAN_EQ, e, "Equality matcher for etl::optional of etl::span")
    {
        if (e.has_value() != arg.has_value())
        {
            return false;
        }

        if (!e.has_value())
        {
            return true;
        }

        if (e.value().size() != arg.value().size())
        {
            return false;
        }

        const auto size = e.value().size();
        for (size_t i = 0; i < size; ++i)
        {
            if (e.value().at(i) != arg.value().at(i))
            {
                return false;
            }
        }
        return true;
    }

#ifdef _MSC_VER
#pragma warning(pop)
#endif

    inline std::vector<uint8_t> hexToBytes(const etl::string_view hex)
    {
        if ((hex.size() % 2) != 0)
        {
            throw InvalidHexString();
        }

        const auto numberBytes = hex.size() / 2;

        std::vector<uint8_t> bytes;

        for (auto i = 0U; i < numberBytes; i += 1)
        {
            const auto r = etl::to_arithmetic<uint8_t>(hex.substr(i * 2, 2), etl::hex);
            if (r.has_value())
            {
                bytes.emplace_back(r.value());
            }
            else
            {
                throw InvalidHexString();
            }
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

    template <typename Server, typename Service, bool AutoReset = true>
    class TestServerBase : public Server, public ::testing::Test
    {
    public:
        void SetUp() final
        {
            Server::registerService(service);
        }

        void lrpcTransmit(etl::span<const uint8_t> bytes) override
        {
            if (AutoReset)
            {
                responseBuffer.clear();
            }
            (void)responseBuffer.insert(responseBuffer.end(), bytes.begin(), bytes.end());
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

        std::vector<uint8_t> responseBuffer;

        Service service;
    };
}