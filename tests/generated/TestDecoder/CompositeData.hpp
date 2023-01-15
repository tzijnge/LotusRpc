#pragma once
#include <stdint.h>
#include <etl/array.h>
#include <etl/byte_stream.h>

struct CompositeData
{
    bool operator==(const CompositeData &other) const
    {
        return this->a == other.a &&
               this->b == other.b &&
               this->c == other.c;
    };

    etl::array<uint16_t, 2> a;
    uint8_t b;
    bool c;
};

namespace etl
{
    template <>
    inline CompositeData read_unchecked<CompositeData>(byte_stream_reader &stream)
    {
        CompositeData cd;
        stream.read_unchecked<uint16_t>(cd.a);
        cd.b = read_unchecked<uint8_t>(stream);
        cd.c = read_unchecked<bool>(stream);
        return cd;
    }

    template <>
    inline void write_unchecked<CompositeData>(byte_stream_writer &stream, const CompositeData &cd)
    {
        stream.write_unchecked<uint16_t>(cd.a.begin(), cd.a.size());
        write_unchecked<uint8_t>(stream, cd.b);
        write_unchecked<bool>(stream, cd.c);
    }
}