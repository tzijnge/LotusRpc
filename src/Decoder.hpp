#pragma once
#include <etl/byte_stream.h>
#include <stdint.h>

class Decoder
{
public:
    using Reader = etl::byte_stream_reader;
    using Writer = etl::byte_stream_writer;

    virtual uint32_t id() const = 0;
    virtual void decode(Reader &reader, Writer &writer) = 0;

protected:
    constexpr void nullInvoker(Reader &reader, Writer &writer) const {}
};