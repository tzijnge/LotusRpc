#include "EtlRwExtensions.hpp"

namespace etl
{
    template <>
    string_view read_unchecked(byte_stream_reader &stream)
    {
        auto found = reinterpret_cast<const char *>(memchr(stream.end(), '\0', stream.available_bytes()));

        size_t stringSize = 0;
        size_t skipSize = 0;
        if (found != nullptr)
        {
            stringSize = std::distance(stream.end(), found);
            skipSize = stringSize + 1;
        }
        else
        {
            stringSize = stream.available_bytes();
            skipSize = stringSize;
        }

        const string_view s{stream.end(), stringSize};
        stream.read_unchecked<uint8_t>(skipSize);
        return s;
    }

    template <>
    void write_unchecked<string_view>(byte_stream_writer &stream, const string_view &sv)
    {
        for (auto c : sv)
        {
            write_unchecked(stream, c);
        }
        write_unchecked(stream, '\0');
    }
}