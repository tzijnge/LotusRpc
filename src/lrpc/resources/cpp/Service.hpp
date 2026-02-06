#pragma once
#include <etl/byte_stream.h>
#include <etl/delegate.h>
#include <etl/string_view.h>
#include <cstdint>
#include "MetaError.hpp"

namespace lrpc
{
    class IServer
    {
    public:
        using Reader = etl::byte_stream_reader;
        using Writer = etl::byte_stream_writer;

        using ParamWriter = etl::delegate<void(Writer &)>;

        virtual void transmit(const uint8_t serviceId, const uint8_t functionOrStreamId) = 0;
        virtual void transmit(const uint8_t serviceId, const uint8_t functionOrStreamId, const ParamWriter writeParams) = 0;

        virtual void error(const LrpcMetaError type, const uint8_t p1 = 0, const uint8_t p2 = 0, const int32_t p3 = 0, const etl::string_view &message = {}) = 0;
    };

    class NullServer : public IServer
    {
    public:
        virtual ~NullServer() = default;

        void transmit(const uint8_t, const uint8_t) final
        {
            // LRPC_ASSERT();
        }
        void transmit(const uint8_t, const uint8_t, const ParamWriter) final
        {
            // LRPC_ASSERT();
        }
        void error(const LrpcMetaError, const uint8_t, const uint8_t, const int32_t, const etl::string_view &) final
        {
            // LRPC_ASSERT();
        }
    };

    class Service
    {
    public:
        virtual ~Service() = default;

        using Reader = IServer::Reader;
        using Writer = IServer::Writer;

        virtual uint8_t id() const = 0;
        virtual void invoke(Reader &reader) = 0;

        void linkServer(IServer &s) { linkedServer = &s; }

    protected:
        IServer &server() const { return *linkedServer; };

        void requestStop(const uint8_t streamId) const
        {
            server().transmit(id(), streamId);
        }

    private:
        NullServer nullServer;
        IServer *linkedServer{&nullServer};
    };
}