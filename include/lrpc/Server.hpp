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

    void decode(uint8_t byte)
    {
        receiveBuffer.push_back(byte);

        if (messageIsComplete())
        {
            invokeService();
            receiveBuffer.clear();
        }
    }

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
        auto serviceId = reader.read_unchecked<uint8_t>();
        for (auto& service : services)
        {
            if (service.id() == serviceId)
            {
                service.decode(reader, writer);
            }
        }
    }
};

}