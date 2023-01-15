#pragma once
#include <etl/array.h>
#include <etl/byte_stream.h>
#include <etl/string_view.h>

// ETL read/write extensions
namespace etl
{
    template <class T, size_t N>
    array<T, N> read_unchecked(byte_stream_reader &stream)
    {
        array<T, N> a;
        for (auto &element : a)
        {
            element = etl::read_unchecked<T>(stream);
        }
        return a;
    }

    template <class T>
    void write_unchecked(byte_stream_writer &stream, const span<T> &s)
    {
        for (auto v : s)
        {
            write_unchecked(stream, v);
        }
    }

    template <>
    string_view read_unchecked(byte_stream_reader &stream);

    template <>
    void write_unchecked<string_view>(byte_stream_writer &stream, const string_view &sv);
}