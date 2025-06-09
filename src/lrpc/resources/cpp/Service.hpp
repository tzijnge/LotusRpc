#pragma once
#include <etl/byte_stream.h>
#include <cstdint>

namespace lrpc
{
    class IServer
    {
    public:
        using Reader = etl::byte_stream_reader;
        using Writer = etl::byte_stream_writer;

        virtual Writer getWriter() = 0;
        virtual void transmit(const Writer &w) = 0;
    };

    class Service
    {
    public:
        virtual ~Service() = default;

        using Reader = IServer::Reader;
        using Writer = IServer::Writer;

        virtual uint8_t id() const = 0;
        virtual bool invoke(Reader &reader, Writer &writer) = 0;

        void linkServer(IServer &s) { server = &s; }

    protected:
        IServer *server{nullptr};

        void writeMessageHeader(Reader &r, Writer &w) const
        {
            w.write_unchecked<uint8_t>(0);                       // placeholder for message size
            w.write_unchecked<uint8_t>(id());                    // service ID
            const auto functionId = r.read_unchecked<uint8_t>(); // message ID
            w.write_unchecked<uint8_t>(functionId);
        }

        static void updateMessageSize(Writer &w)
        {
            *w.begin() = static_cast<uint8_t>(w.size_bytes());
        }

        void requestStop(const uint8_t streamId)
        {
            if (server != nullptr)
            {
                constexpr uint8_t messageSize{3};
                auto w = server->getWriter();
                w.write_unchecked<uint8_t>(messageSize);
                w.write_unchecked<uint8_t>(id());
                w.write_unchecked<uint8_t>(streamId);
                server->transmit(w);
            }
        }
    };

}