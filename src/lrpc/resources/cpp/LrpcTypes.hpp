
#pragma once

$byte_include
#include <cstdint>

#include <etl/span.h>

#include "LrpcBaseTypes.hpp"

namespace lrpc
{
    using byte = $byte_type;
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;
}
