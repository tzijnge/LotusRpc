#pragma once
#include "Decoder.hpp"
#include <etl/vector.h>

class Server
{
public:
    void registerDecoder(Decoder &decoder)
    {
        interfaces[decoder.id()] = &decoder;
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
        using Reader = Decoder::Reader;
        using Writer = Decoder::Writer;

        Reader reader(receiveBuffer.begin(), receiveBuffer.end(), etl::endian::little);
        Writer writer(sendBuffer.begin(), sendBuffer.end(), etl::endian::little);
        reader.skip<uint8_t>(1); // message size
        auto interfaceId = reader.read_unchecked<uint8_t>();
        interfaces.at(interfaceId)->decode(reader, writer);
    }

    etl::vector<Decoder *, 2> interfaces{
        nullptr,
        nullptr,
    };
};