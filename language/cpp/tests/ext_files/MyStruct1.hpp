#pragma once

struct MyStruct1
{
    double f1;

    // Additional static members and functions are ok in an external struct, but they are ignored by LRPC 
    static int a;

    double getF1()
    {
        return f1;
    }
};