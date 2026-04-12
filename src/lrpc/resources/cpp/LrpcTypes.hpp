#pragma once

$byte_include
#include <array>
#include <cstdint>
#include <cstddef>
#include <etl/optional.h>
#include <etl/span.h>
#include <etl/string_view.h>

namespace lrpc
{
    using byte = $byte_type;
    static_assert(sizeof(byte) == 1, "sizeof(byte) must be exactly 1");

    using bytearray = etl::span<const byte>;

    using string_view = etl::string_view;

    template <typename T>
    using span = etl::span<T>;

    template <typename T, size_t N>
    using array = std::array<T, N>;

    template <typename T>
    using optional = etl::optional<T>;
}
