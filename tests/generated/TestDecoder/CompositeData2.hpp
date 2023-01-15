#pragma once
#include <stdint.h>
#include <etl/byte_stream.h>

struct CompositeData2
{
    bool operator==(const CompositeData2 &other) const
    {
        return this->a == other.a &&
               this->b == other.b;
    };
    bool operator!=(const CompositeData2 &other) const
    {
        return !(*this == other);
    }

    uint8_t a;
    uint8_t b;
};

namespace etl
{
    template <>
    inline CompositeData2 read_unchecked<CompositeData2>(byte_stream_reader &stream)
    {
        CompositeData2 cd2;
        cd2.a = read_unchecked<uint8_t>(stream);
        cd2.b = read_unchecked<uint8_t>(stream);
        return cd2;
    }

    template <>
    inline void write_unchecked<CompositeData2>(byte_stream_writer &stream, const CompositeData2 &cd)
    {
        write_unchecked<uint8_t>(stream, cd.a);
        write_unchecked<uint8_t>(stream, cd.b);
    }
}