#pragma once
#include <etl/array.h>
#include <etl/byte_stream.h>
#include <etl/string_view.h>
#include <etl/string.h>

namespace lrpc
{
    template <typename T>
    struct is_etl_optional : etl::false_type
    {
    };

    template <typename T>
    struct is_etl_optional<etl::optional<T>> : etl::true_type
    {
    };

    template <typename T>
    struct is_etl_string : etl::false_type
    {
    };

    template <size_t N>
    struct is_etl_string<etl::string<N>> : etl::true_type
    {
    };

    template <typename T>
    struct is_etl_array : etl::false_type
    {
    };

    template <typename T, size_t N>
    struct is_etl_array<etl::array<T, N>> : etl::true_type
    {
    };

    template <typename T>
    struct etl_optional_type
    {
    };

    template <typename T>
    struct etl_optional_type<etl::optional<T>>
    {
        using type = T;
    };

    template <typename T>
    struct etl_array_type
    {
    };

    template <typename T, size_t N>
    struct etl_array_type<etl::array<T, N>>
    {
        using type = T;
    };

    template <typename T>
    struct etl_array_size
    {
    };

    template <typename T, size_t N>
    struct etl_array_size<etl::array<T, N>> : etl::integral_constant<size_t, N>
    {
    };

    template <typename T>
    struct etl_string_size
    {
    };

    template <size_t N>
    struct etl_string_size<etl::string<N>> : etl::integral_constant<size_t, N>
    {
    };

    // deleted read function to allow specializations for custom structs
    template <typename T>
    typename etl::enable_if<!etl::is_arithmetic<T>::value &&
                                !is_etl_optional<T>::value &&
                                !is_etl_array<T>::value &&
                                !etl::is_same<T, etl::string_view>::value &&
                                !is_etl_string<T>::value,
                            T>::type
    read_unchecked(etl::byte_stream_reader &stream) = delete;

    // Arithmetic types
    template <typename T>
    typename etl::enable_if<etl::is_arithmetic<T>::value, T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        return stream.read_unchecked<T>();
    };

    // Optional
    template <typename T>
    typename etl::enable_if<is_etl_optional<T>::value, T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        auto has_value = etl::read_unchecked<bool>(stream);
        if (has_value)
        {
            return lrpc::read_unchecked<typename etl_optional_type<T>::type>(stream);
        }

        return {};
    };

    template <typename T>
    using etl_sv_array = etl::array<etl::string_view, etl_array_size<T>::value>;

    template <typename T>
    using etl_array_type_is_string = is_etl_string<typename etl_array_type<T>::type>;

    template <typename T>
    using array_not_of_string = etl::enable_if<is_etl_array<T>::value && !etl_array_type_is_string<T>::value, T>;

    template <typename T>
    using array_of_string = etl::enable_if<is_etl_array<T>::value && etl_array_type_is_string<T>::value, etl::array<etl::string_view, etl_array_size<T>::value>>;

    // Array, but not of fixed size string
    template <typename T>
    typename array_not_of_string<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        T arr;
        for (auto &el : arr)
        {
            el = lrpc::read_unchecked<typename etl_array_type<T>::type>(stream);
        }

        return arr;
    };

    // Array of fixed size string. Read as an array of etl::string_view
    template <typename T>
    typename array_of_string<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        etl::array<etl::string_view, etl_array_size<T>::value> arr;
        for (auto &el : arr)
        {
            el = lrpc::read_unchecked<typename etl_array_type<T>::type>(stream);
        }

        return arr;
    };

    // Auto string
    template <typename T>
    typename etl::enable_if<etl::is_same<T, etl::string_view>::value, T>::type
    read_unchecked(etl::byte_stream_reader &stream)
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

        const etl::string_view s{stream.end(), stringSize};
        stream.read_unchecked<uint8_t>(skipSize);
        return s;
    };

    // Fixed size string
    template <typename T>
    typename etl::enable_if<is_etl_string<T>::value, etl::string_view>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        auto found = reinterpret_cast<const char *>(memchr(stream.end(), '\0', stream.available_bytes()));

        size_t stringSize = 0;
        size_t skipSize = 0;
        if (found != nullptr)
        {
            stringSize = std::distance(stream.end(), found);
            stringSize = std::min(stringSize, etl_string_size<T>::value);
            skipSize = stringSize + 1;
        }
        else
        {
            stringSize = stream.available_bytes();
            stringSize = std::min(stringSize, etl_string_size<T>::value);
            skipSize = stringSize;
        }

        const etl::string_view s{stream.end(), stringSize};
        stream.read_unchecked<uint8_t>(skipSize);
        return s;
    }

    // deleted write function to allow specializations for custom structs
    template <typename T, typename etl::enable_if<!etl::is_arithmetic<T>::value &&
                                           !is_etl_optional<T>::value &&
                                           !is_etl_array<T>::value &&
                                           !etl::is_same<T, etl::string_view>::value,
                                           bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const T &value) = delete;

    template <typename ARI, typename etl::enable_if<etl::is_arithmetic<ARI>::value, bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const ARI &value)
    {
        stream.write_unchecked<ARI>(value);
    };
    
    template <typename OPT, typename = typename etl::enable_if<is_etl_optional<OPT>::value, OPT>::type>
    void write_unchecked(etl::byte_stream_writer &stream, const etl::optional<typename etl_optional_type<OPT>::type> &value)
    {
        stream.write_unchecked<bool>(value.has_value());
        if (value.has_value())
        {
            write_unchecked<typename etl_optional_type<OPT>::type>(value.value());
        }
    };

    template <typename ARR, typename = typename etl::enable_if<is_etl_array<ARR>::value, ARR>::type>
    void write_unchecked(etl::byte_stream_writer &stream, const etl::span<const typename etl_array_type<ARR>::type> &value)
    {
        for (const auto& el : value)
        {
            lrpc::write_unchecked<typename etl_array_type<ARR>::type>(stream, el);
        }
    };

    template <typename T, typename = typename etl::enable_if<etl::is_same<T, etl::istring>::value, T>::type>
    void write_unchecked(etl::byte_stream_writer &stream, const etl::istring &value)
    {
        for (auto c : value)
        {
            stream.write_unchecked<char>(c);
        }
        stream.write_unchecked<char>('\0');
    };
}
