#pragma once
#include <cstdint>
#include <utility>

#include <etl/byte_stream.h>
#include <etl/delegate.h>

#include "LrpcTypes.hpp"
#include "MetaError.hpp"

namespace lrpc
{
    class IServer
    {
    public:
        using Reader = etl::byte_stream_reader;
        using Writer = etl::byte_stream_writer;

        using ParamWriter = etl::delegate<void(Writer&)>;

        virtual ~IServer() = default;

        // NOLINTBEGIN(readability-avoid-const-params-in-decls)
        virtual void transmit(const uint8_t serviceId, const uint8_t functionOrStreamId) = 0;
        virtual void transmit(const uint8_t serviceId, const uint8_t functionOrStreamId,
                              const ParamWriter writeParams) = 0;
        virtual void error(const LrpcMetaError type, const uint8_t p1 = 0, const uint8_t p2 = 0, const int32_t p3 = 0,
                           const lrpc::string_view& message = {}) = 0;
        // NOLINTEND(readability-avoid-const-params-in-decls)

        virtual void lrpcTransmit(lrpc::span<const uint8_t> bytes) = 0;
    };

    class NullServer : public IServer
    {
    public:
        ~NullServer() override = default;

        void transmit(const uint8_t /*serviceId*/, const uint8_t /*functionOrStreamId*/) final
        {
            // TODO: #206 Add LRPC_ASSERT
            // LRPC_ASSERT();
        }

        void transmit(const uint8_t /*serviceId*/, const uint8_t /*functionOrStreamId*/,
                      const ParamWriter /*writeParams*/) final
        {
            // TODO: #206 Add LRPC_ASSERT
            // LRPC_ASSERT();
        }

        void error(const LrpcMetaError /*type*/, const uint8_t /*p1*/, const uint8_t /*p2*/, const int32_t /*p3*/,
                   const lrpc::string_view& /*message*/) final
        {
            // TODO: #206 Add LRPC_ASSERT
            // LRPC_ASSERT();
        }

        void lrpcTransmit(lrpc::span<const uint8_t> /* bytes */) final
        {
            // intentionally not implemented
        }
    };

    class Service
    {
    public:
        virtual ~Service() = default;

        using Reader = IServer::Reader;
        using Writer = IServer::Writer;

        virtual uint8_t id() const = 0;
        virtual void invoke(Reader& reader) = 0;

        void linkServer(IServer& server) { linkedServer = &server; }

    protected:
        IServer& server() const { return *linkedServer; }

        void requestStop(const uint8_t streamId) const { server().transmit(id(), streamId); }

    private:
        NullServer nullServer;
        IServer* linkedServer{&nullServer};
    };

    template <uint8_t ServiceId>
    class ServiceForwarder : public Service
    {
    public:
        uint8_t id() const override { return ServiceId; }
        void invoke(Reader& reader) override
        {
            const auto d = reader.data().reinterpret_as<const uint8_t>();
            forwardToServer({d.data(), d.size()});
        }

        virtual void forwardToServer(lrpc::span<const uint8_t> data) = 0;

        void forwardToClient(const uint8_t byte) { server().lrpcTransmit(lrpc::span<const uint8_t>(&byte, 1)); }
        void forwardToClient(lrpc::span<const uint8_t> data) { server().lrpcTransmit(data); }

        template <typename TContainer,
                  typename = decltype(std::declval<TContainer>().data(), std::declval<TContainer>().size(), void())>
        void forwardToClient(const TContainer& data)
        {
            forwardToClient(lrpc::span<const uint8_t>(data.data(), data.size()));
        }
    };
}