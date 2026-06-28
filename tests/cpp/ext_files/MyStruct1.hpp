#pragma once
#include <cstdint>

struct MyStruct1
{
    // Goal of this test is to verify that an additional member function is accepted by LotusRPC
    double f1;

    // Additional static members and functions are ok in an external struct, but they are ignored by LRPC
    static uint8_t abc;

    double getF1() const { return f1; }
};