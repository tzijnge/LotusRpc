#pragma once
#include "Service.hpp"
#include <etl/vector.h>

namespace lrpc
{

template <size_t RXSIZE = 256, size_t TXSIZE = RXSIZE>
class Server
{
public:
    void registerService(Service &service)
    {
        services.push_front(service);
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
    using ServiceList = etl::intrusive_forward_list<Service, ServiceListItem>;

    etl::vector<uint8_t, RXSIZE> receiveBuffer;
    etl::vector<uint8_t, TXSIZE> sendBuffer;
    ServiceList services;

    bool messageIsComplete() const
    {
        return receiveBuffer.size() == receiveBuffer.at(0);
    }

    void invokeService()
    {
        Service::Reader reader(receiveBuffer.begin(), receiveBuffer.end(), etl::endian::little);
        Service::Writer writer(sendBuffer.begin(), sendBuffer.end(), etl::endian::little);

        reader.skip<uint8_t>(1); // message size
        writer.write_unchecked<uint8_t>(0); // placeholder for message size

        auto serviceId = reader.read_unchecked<uint8_t>();
        writer.write_unchecked<uint8_t>(serviceId);

        for (auto& service : services)
        {
            if (service.id() == serviceId)
            {
                service.invoke(reader, writer);
            }
        }

        sendBuffer[0] = writer.size_bytes();

        const auto b = reinterpret_cast<const uint8_t *>(writer.cbegin());
        const auto e = reinterpret_cast<const uint8_t *>(writer.cend());
        lrpcTransmit({b, e});
    }
};

}