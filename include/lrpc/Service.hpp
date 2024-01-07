#pragma once
#include <etl/byte_stream.h>
#include <stdint.h>

namespace lrpc
{
class Service
{
public:
    using Reader = etl::byte_stream_reader;
    using Writer = etl::byte_stream_writer;

    virtual uint32_t id() const = 0;
    virtual void invoke(Reader &reader, Writer &writer) = 0;
};

}