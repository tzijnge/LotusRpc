#pragma once

namespace lrpc
{
    enum class LrpcMetaError
    {
        UnknownService = 0,
        UnknownFunctionOrStream = 1,
    };
}