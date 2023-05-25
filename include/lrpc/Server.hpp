#pragma once
#include "Service.hpp"
#include <etl/vector.h>

namespace lrpc
{
class Server
{
public:
    void registerService(Service &service)
    {
        services[service.id()] = &service;
    }

    void decode(uint8_t byte)
    {
        receiveBuffer.push_back(byte);

        if (messageIsComplete())
        {
            invokeFunction();
            receiveBuffer.clear();
        }
    }

private:
    etl::vector<uint8_t, 256> receiveBuffer;
    etl::vector<uint8_t, 256> sendBuffer;

    bool
    messageIsComplete() const
    {
        return receiveBuffer.size() == receiveBuffer.at(0);
    }

    void invokeFunction()
    {
        using Reader = Service::Reader;
        using Writer = Service::Writer;

        Reader reader(receiveBuffer.begin(), receiveBuffer.end(), etl::endian::little);
        Writer writer(sendBuffer.begin(), sendBuffer.end(), etl::endian::little);
        reader.skip<uint8_t>(1); // message size
        auto interfaceId = reader.read_unchecked<uint8_t>();
        services.at(interfaceId)->decode(reader, writer);
    }

    etl::vector<Service *, 2> services{
        nullptr,
        nullptr,
    };
};

}