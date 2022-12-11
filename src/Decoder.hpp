#pragma once
#include <stdint.h>
#include <etl/byte_stream.h>

class Decoder
{
public:
    virtual uint32_t id() const = 0;
    virtual void decode(etl::byte_stream_reader& reader) = 0;
};