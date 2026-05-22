#pragma once
#include <cstdint>

// Testing the default value is part of the test this is used in
// NOLINTNEXTLINE(readability-enum-initial-value)
enum class MyEnum3 : uint8_t
{
    V0,
    V55 = 55,
    V200 = 200,
};