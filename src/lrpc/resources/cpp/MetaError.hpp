#pragma once
#include <cstdint>

namespace lrpc
{
    enum class LrpcMetaError : uint8_t
    {
        UnknownService = 0,
        UnknownFunctionOrStream = 1,
    };
}