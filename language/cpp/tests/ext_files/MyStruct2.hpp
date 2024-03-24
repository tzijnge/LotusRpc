#pragma once
#include <etl/array.h>

namespace ext
{
namespace test
{
    struct MyStruct2
    {
        float f1;
        etl::array<bool, 7> f2;
    };
}
}