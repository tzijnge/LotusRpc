#pragma once
#include <stdint.h>
#include <etl/byte_stream.h>

class Decoder
{
public:
    using Reader = etl::byte_stream_reader;
    using Writer = etl::byte_stream_writer;

    virtual uint32_t id() const = 0;
    virtual void decode(Reader &reader, Writer &writer) = 0;
};