#pragma once
#include "decoder.hpp"

class Server
{
public:
    void registerDecoder(Decoder &decoder) { mDecoder = &decoder; }
    void decode(uint8_t byte) { mDecoder->decode(byte); }

private:
    Decoder *mDecoder{nullptr};
};