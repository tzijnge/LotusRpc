#pragma once
#include "Service.hpp"
#include <etl/array.h>
#include <etl/vector.h>

namespace lrpc
{
    template <size_t MAX_SERVICE_ID, size_t RX_SIZE = 256, size_t TX_SIZE = RX_SIZE>
    class Server : public IServer
    {
    private:
    public:
        Server()
        {
            services.fill(&nullService);
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
            services[service.id()] = &service;
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

        virtual void lrpcTransmit(etl::span<const uint8_t> bytes) = 0;

    private:
        etl::vector<uint8_t, RX_SIZE> receiveBuffer;
        etl::array<uint8_t, TX_SIZE> sendBuffer;
        etl::array<Service *, MAX_SERVICE_ID + 1> services;
        NullService nullService;

        bool messageIsComplete() const
        {
            return receiveBuffer.size() == receiveBuffer.at(0);
        }

        Service *service(const uint8_t serviceId)
        {
            if (serviceId < services.size())
            {
                return services.at(serviceId);
            }

            return &nullService;
        }

        void invokeService()
        {

            Reader reader{receiveBuffer.begin(), receiveBuffer.end(), etl::endian::little};
            Writer writer{sendBuffer.begin(), sendBuffer.end(), etl::endian::little};

            reader.skip<uint8_t>(1); // message size

            auto serviceId = reader.read_unchecked<uint8_t>();

            service(serviceId)->invoke(reader, writer);

            transmit(writer);
        }
    };

}