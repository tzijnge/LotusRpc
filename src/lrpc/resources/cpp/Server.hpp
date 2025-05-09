#pragma once
#include "Service.hpp"
#include <etl/array.h>
#include <etl/vector.h>

namespace lrpc
{

template <size_t MAX_SERVICE_ID, size_t RX_SIZE = 256, size_t TX_SIZE = RX_SIZE>
class Server
{
private:
    class NullService : public Service
    {
    public:
        uint8_t id() const override { return 0; };
        bool invoke(Reader&, Writer& writer) override
        {
            writer.write_unchecked<uint8_t>(0xFF); // service ID
            writer.write_unchecked<uint8_t>(0); // function ID
            writer.write_unchecked<uint8_t>(0); // error type
            writer.write_unchecked<int32_t>(0); // p0
            writer.write_unchecked<int32_t>(0); // p1
            writer.write_unchecked<int32_t>(0); // p2
            writer.write_unchecked<int32_t>(0); // p3

            return true;
        };
    };

public:
    Server()
    {
        static NullService nullService;
        services.fill(&nullService);
    }

    void registerService(Service &service)
    {
        services[service.id()] = &service;
    }

    void lrpcReceive(etl::span<const uint8_t> bytes)
    {
        for (const auto b : bytes)
        {
            lrpcReceive(b);
        }
    }

    void lrpcReceive(uint8_t byte)
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
    etl::vector<uint8_t, TX_SIZE> sendBuffer;
    etl::array<Service*, MAX_SERVICE_ID + 1> services;

    bool messageIsComplete() const
    {
        return receiveBuffer.size() == receiveBuffer.at(0);
    }

    void invokeService()
    {
        static NullService nullService;

        Service::Reader reader(receiveBuffer.begin(), receiveBuffer.end(), etl::endian::little);
        Service::Writer writer(sendBuffer.begin(), sendBuffer.end(), etl::endian::little);

        reader.skip<uint8_t>(1); // message size
        writer.write_unchecked<uint8_t>(0); // placeholder for message size

        auto serviceId = reader.read_unchecked<uint8_t>();

        bool serviceOk = serviceId < services.size();
        if (serviceOk)
        {
            serviceOk = services.at(serviceId)->invoke(reader, writer);
        }

        if (!serviceOk)
        {
            nullService.invoke(reader, writer);
        }

        sendBuffer[0] = static_cast<uint8_t>(writer.size_bytes());

        const auto b = reinterpret_cast<const uint8_t *>(writer.cbegin());
        const auto e = reinterpret_cast<const uint8_t *>(writer.cend());
        lrpcTransmit({b, e});
    }
};

}