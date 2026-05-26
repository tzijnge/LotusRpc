
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include <etl/optional.h>
#include <etl/span.h>
#include <etl/string_view.h>

namespace lrpc
{
    using string_view = etl::string_view;

    template <typename T>
    using span = etl::span<T>;

    template <typename T, size_t N>
    using array = std::array<T, N>;

    template <typename T>
    using optional = etl::optional<T>;
}
