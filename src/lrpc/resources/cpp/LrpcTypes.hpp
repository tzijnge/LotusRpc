#pragma once

#include <array>
#include <etl/optional.h>
#include <etl/span.h>
#include <etl/string_view.h>

namespace lrpc
{
    // Define the fundamental byte type used throughout LRPC.
    // Can be overridden by defining LRPC_BYTE_TYPE before including this header.
    // Must be exactly 1 byte in size.
#ifndef LRPC_BYTE_TYPE
#define LRPC_BYTE_TYPE uint8_t
#endif

    static_assert(sizeof(LRPC_BYTE_TYPE) == 1, "sizeof(LRPC_BYTE_TYPE) must be exactly 1");

    using bytearray = etl::span<const LRPC_BYTE_TYPE>;

    using string_view = etl::string_view;

    template <typename T>
    using span = etl::span<T>;

    template <typename T, size_t N>
    using array = std::array<T, N>;

    template <typename T>
    using optional = etl::optional<T>;
}
