#pragma once
#include "Service.hpp"
#include <etl/array.h>
#include <etl/vector.h>

namespace lrpc
{
    template <size_t MAX_SERVICE_ID, typename META_SERVICE, size_t RX_SIZE = 256, size_t TX_SIZE = RX_SIZE>
    class Server : public IServer
    {
    private:
        class ServiceNotFoundService : public Service
        {
        public:
            uint8_t id() const override { return 0; };
            void invoke(Service::Reader &r, Service::Writer &) override
            {
                const auto data = r.data();
                const auto serviceId = data.at(1);
                const auto functionOrStreamId = data.at(2);
                server->error(LrpcMetaError::UnknownService, serviceId, functionOrStreamId, 0);
            };
        };

    public:
        Server()
        {
            services.fill(&serviceNotFound);
            serviceNotFound.linkServer(*this);
            registerService(metaService);
        }

        Writer getWriter() override
        {
            return Writer{sendBuffer.begin(), sendBuffer.end(), etl::endian::little};
        }

        void transmit(const Writer &w) override
        {
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

        void error(const LrpcMetaError type, const uint8_t p1 = 0, const uint8_t p2 = 0, const int32_t p3 = 0, const OptionalMessage &message = {}) override
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

            if (serviceId < services.size())
            {
                return services.at(serviceIndex);
            }

            return &serviceNotFound;
        }

        void invokeService()
        {
            Reader reader{receiveBuffer.begin(), receiveBuffer.end(), etl::endian::little};
            Writer writer{sendBuffer.begin(), sendBuffer.end(), etl::endian::little};

            reader.skip<uint8_t>(1); // message size

            const auto serviceId = reader.read_unchecked<uint8_t>();

            service(serviceId)->invoke(reader, writer);

            transmit(writer);
        }
    };

}