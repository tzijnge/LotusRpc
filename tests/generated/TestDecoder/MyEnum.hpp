#pragma once

enum class MyEnum
{
    V0,
    V1,
    V2,
    V3
};

namespace etl
{
    template <>
    MyEnum read_unchecked<MyEnum>(byte_stream_reader &stream)
    {
        return static_cast<MyEnum>(read_unchecked<uint8_t>(stream));
    }

    template <>
    void write_unchecked<MyEnum>(byte_stream_writer &stream, const MyEnum &me)
    {
        write_unchecked<uint8_t>(stream, static_cast<uint8_t>(me));
    }
}