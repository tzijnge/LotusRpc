#pragma once
#include <etl/byte_stream.h>
#include <stdint.h>
#include <etl/intrusive_forward_list.h>

namespace lrpc
{
using ServiceListItem = etl::forward_link<0>;
class Service : public ServiceListItem
{
public:
    using Reader = etl::byte_stream_reader;
    using Writer = etl::byte_stream_writer;

    virtual uint32_t id() const = 0;
    virtual void decode(Reader &reader, Writer &writer) = 0;

protected:
    constexpr void nullInvoker(Reader &reader, Writer &writer) const {}
};

}