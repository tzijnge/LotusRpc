#pragma once
#include "CompositeData2.hpp"
#include <etl/byte_stream.h>

struct CompositeData3
{
    bool operator==(const CompositeData3 &other) const
    {
        return this->a == other.a;
    };
    bool operator!=(const CompositeData3 &other) const
    {
        return !(*this == other);
    }

    CompositeData2 a;
};

namespace etl
{
    template <>
    inline CompositeData3 read_unchecked<CompositeData3>(byte_stream_reader &stream)
    {
        CompositeData3 cd3;
        cd3.a = read_unchecked<CompositeData2>(stream);
        return cd3;
    }

    template <>
    inline void write_unchecked<CompositeData3>(byte_stream_writer &stream, const CompositeData3 &cd)
    {
        write_unchecked<CompositeData2>(stream, cd.a);
    }
}