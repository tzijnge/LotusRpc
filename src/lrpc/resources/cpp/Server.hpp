#pragma once
#include "Service.hpp"
#include <etl/array.h>
#include <etl/vector.h>

namespace lrpc
{
    constexpr size_t RxTxSizeMax{256};

    template <size_t MAX_SERVICE_ID, typename META_SERVICE, size_t RX_SIZE = RxTxSizeMax, size_t TX_SIZE = RX_SIZE>
    class Server : public IServer
    {
        static_assert(RX_SIZE <= RxTxSizeMax, "Rx buffer size must not exceed 256 bytes");
        static_assert(TX_SIZE <= RxTxSizeMax, "Tx buffer size must not exceed 256 bytes");

        class ServiceNotFoundService : public Service
        {
        public:
            uint8_t id() const override { return 0; };
            void invoke(Service::Reader &reader) override
            {
                const auto data = reader.data();
                const auto serviceId = data.at(1);
                const auto functionOrStreamId = data.at(2);
                server().error(LrpcMetaError::UnknownService, serviceId, functionOrStreamId);
            };
        };

    public:
        Server()
        {
            services.fill(&serviceNotFound);
            serviceNotFound.linkServer(*this);
            registerService(metaService);
        }

        void transmit(const uint8_t serviceId, const uint8_t functionOrStreamId) override
        {
            static const auto cb = [](Writer &) {};
            transmit(serviceId, functionOrStreamId, cb);
        }

        void transmit(const uint8_t serviceId, const uint8_t functionOrStreamId, const ParamWriter writeParams) override
        {
            auto w = Writer{sendBuffer.begin(), sendBuffer.end(), etl::endian::little};

            createHeader(w, serviceId, functionOrStreamId);
            writeParams(w);
            updateHeaderMessageSize(w);

            const auto b = reinterpret_cast<const uint8_t *>(w.cbegin());
            const auto e = reinterpret_cast<const uint8_t *>(w.cend());
            lrpcTransmit({b, e});
        }

        void registerService(Service &service)
        {
            // TODO: check for out of bounds service

            // integer overflow for meta service intended
            services.at(static_cast<uint8_t>(service.id() + 1U)) = &service;
            service.linkServer(*this);
        }

        void lrpcReceive(etl::span<const uint8_t> bytes)
        {
            for (const auto b : bytes)
            {
                lrpcReceive(b);
            }
        }

        void lrpcReceive(const uint8_t byte)
        {
            receiveBuffer.push_back(byte);

            if (messageIsComplete())
            {
                invokeService();
                receiveBuffer.clear();
            }
        }

        void error(const LrpcMetaError type, const uint8_t p1 = 0, const uint8_t p2 = 0, const int32_t p3 = 0, const etl::string_view &message = {}) override
        {
            metaService.error_response(type, p1, p2, p3, message);
        }

        virtual void lrpcTransmit(etl::span<const uint8_t> bytes) = 0;

    private:
        etl::vector<uint8_t, RX_SIZE> receiveBuffer;
        etl::array<uint8_t, TX_SIZE> sendBuffer;

        // +2 to allocate space for all regular services and the meta service
        etl::array<Service *, MAX_SERVICE_ID + 2U> services;
        META_SERVICE metaService;
        ServiceNotFoundService serviceNotFound;

        bool messageIsComplete() const
        {
            return receiveBuffer.size() == receiveBuffer.at(0);
        }

        Service *service(const uint8_t serviceId)
        {
            // integer overflow for meta service intended
            const uint8_t serviceIndex = static_cast<uint8_t>(serviceId + 1U);

            if (serviceIndex < services.size())
            {
                return services.at(serviceIndex);
            }

            return &serviceNotFound;
        }

        void invokeService()
        {
            Reader reader{receiveBuffer.begin(), receiveBuffer.end(), etl::endian::little};

            reader.skip<uint8_t>(1); // message size

            const auto serviceId = reader.read_unchecked<uint8_t>();

            service(serviceId)->invoke(reader);
        }

        static void createHeader(Writer &w, const uint8_t serviceId, const uint8_t functionOrStreamId)
        {
            w.write_unchecked<uint8_t>(0);         // placeholder for message size
            w.write_unchecked<uint8_t>(serviceId); // service ID
            w.write_unchecked<uint8_t>(functionOrStreamId);
        }

        static void updateHeaderMessageSize(Writer &w)
        {
            const auto s = w.size_bytes();
            if (s != 0)
            {
                *w.begin() = static_cast<uint8_t>(s);
            }
        }
    };

}