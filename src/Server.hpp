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
        messageBuffer.push_back(byte);

        if (messageIsComplete())
        {
            invokeFunction();
            messageBuffer.clear();
        }
    }

private:
    etl::vector<uint8_t, 256> messageBuffer;

    bool messageIsComplete() const
    {
        return messageBuffer.size() == messageBuffer.at(0);
    }

    void invokeFunction()
    {
        using Reader = etl::byte_stream_reader;

        Reader reader(messageBuffer.begin(), messageBuffer.end(), etl::endian::little);
        reader.skip<uint8_t>(1); // message size
        auto interfaceId = reader.read_unchecked<uint8_t>();
        interfaces.at(interfaceId)->decode(reader);
    }

    etl::vector<Decoder*, 2> interfaces{
        nullptr,
        nullptr,
    };
};