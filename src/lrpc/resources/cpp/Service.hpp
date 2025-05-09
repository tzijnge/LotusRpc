#pragma once
#include <etl/byte_stream.h>
#include <stdint.h>

namespace lrpc
{
class Service
{
public:
    virtual ~Service() = default;

    using Reader = etl::byte_stream_reader;
    using Writer = etl::byte_stream_writer;

    virtual uint8_t id() const = 0;
    virtual bool invoke(Reader &reader, Writer &writer) = 0;
};

}