#pragma once
#include <stdint.h>

class Decoder
{
public:
    virtual void decode(uint8_t byte) = 0;
};