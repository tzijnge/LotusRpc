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

protected:
    static void writeMessageHeader(Reader &r, Writer &w, uint8_t serviceId)
    {
        w.write_unchecked<uint8_t>(0); // placeholder for message size
        w.write_unchecked<uint8_t>(serviceId);
        const auto functionId = r.read_unchecked<uint8_t>(); // message ID
        w.write_unchecked<uint8_t>(functionId);
    }

    static void updateMessageSize(Writer &w)
    {
        *w.begin() = static_cast<uint8_t>(w.size_bytes());
    }
};

}