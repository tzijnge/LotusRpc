#pragma once
#include <etl/byte_stream.h>
#include <cstdint>
#include "MetaError.hpp"

namespace lrpc
{
    class IServer
    {
    public:
        using Reader = etl::byte_stream_reader;
        using Writer = etl::byte_stream_writer;

        virtual Writer getWriter() = 0;
        virtual void transmit(const Writer &w) = 0;
        virtual void error(const LrpcMetaError type, const uint8_t errorFlag1, const uint8_t errorFlag2, const int32_t errorFlag3) = 0;
    };

    class Service
    {
    public:
        virtual ~Service() = default;

        using Reader = IServer::Reader;
        using Writer = IServer::Writer;

        virtual uint8_t id() const = 0;
        virtual void invoke(Reader &reader, Writer &writer) = 0;

        void linkServer(IServer &s) { server = &s; }

    protected:
        IServer *server{nullptr};

        void writeHeader(Writer &w, const uint8_t functionId) const
        {
            w.write_unchecked<uint8_t>(0);    // placeholder for message size
            w.write_unchecked<uint8_t>(id()); // service ID
            w.write_unchecked<uint8_t>(functionId);
        }

        static void updateHeader(Writer &w)
        {
            const auto s = w.size_bytes();
            if (s != 0)
            {
                *w.begin() = static_cast<uint8_t>(s);
            }
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