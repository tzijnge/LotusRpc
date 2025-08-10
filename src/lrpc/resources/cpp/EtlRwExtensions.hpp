#pragma once
#include <etl/array.h>
#include <etl/byte_stream.h>
#include <etl/string_view.h>
#include <etl/string.h>

namespace lrpc
{
    template <typename T>
    struct is_etl_optional : public etl::false_type
    {
    };

    template <typename T>
    struct is_etl_optional<etl::optional<T>> : public etl::true_type
    {
    };

    template <typename T>
    struct is_etl_string : public etl::false_type
    {
    };

    template <size_t N>
    struct is_etl_string<etl::string<N>> : public etl::true_type
    {
    };

    template <typename T>
    struct is_etl_array : public etl::false_type
    {
    };

    template <typename T, size_t N>
    struct is_etl_array<etl::array<T, N>> : public etl::true_type
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
    struct etl_array_size<etl::array<T, N>> : public etl::integral_constant<size_t, N>
    {
    };

    template <typename T>
    struct etl_string_size
    {
    };

    template <size_t N>
    struct etl_string_size<etl::string<N>> : public etl::integral_constant<size_t, N>
    {
    };

    template <typename T>
    using etl_sv_array = etl::array<etl::string_view, etl_array_size<T>::value>;

    template <typename T>
    using etl_array_type_is_string = is_etl_string<typename etl_array_type<T>::type>;

    template <typename T>
    using etl_optional_type_is_string = is_etl_string<typename etl_optional_type<T>::type>;

    // deleted read function to allow specializations for custom structs
    template <typename T>
    typename etl::enable_if<(!etl::is_arithmetic<T>::value) &&
                                (!etl::is_enum<T>::value) &&
                                (!is_etl_optional<T>::value) &&
                                (!is_etl_array<T>::value) &&
                                (!etl::is_same<T, etl::string_view>::value) &&
                                (!is_etl_string<T>::value),
                            T>::type
    read_unchecked(etl::byte_stream_reader &stream) = delete;

    // Arithmetic types
    template <typename T>
    using enable_for_arithmetic = etl::enable_if<etl::is_arithmetic<T>::value, T>;

    template <typename T>
    typename enable_for_arithmetic<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        return stream.read_unchecked<T>();
    };

    // Enum
    template <typename T>
    using enable_for_enum = etl::enable_if<etl::is_enum<T>::value, T>;

    template <typename T>
    typename enable_for_enum<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        return static_cast<T>(stream.read_unchecked<uint8_t>());
    }

    // Auto string
    template <typename T>
    using enable_for_auto_string = etl::enable_if<etl::is_same<T, etl::string_view>::value, T>;

    template <typename T>
    typename enable_for_auto_string<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        size_t stringSize{0};
        size_t skipSize{0};

        const auto fd = stream.free_data();
        const auto found = etl::find(fd.begin(), fd.end(), '\0');

        if (found != fd.end())
        {
            stringSize = static_cast<size_t>(etl::distance(fd.begin(), found));
            skipSize = stringSize + 1;
        }
        else
        {
            stringSize = stream.available_bytes();
            skipSize = stringSize;
        }

        const etl::string_view s{stream.end(), stringSize};
        (void)stream.read_unchecked<uint8_t>(skipSize);
        return s;
    };

    // Fixed size string
    template <typename T>
    using enable_for_fixed_size_string = etl::enable_if<is_etl_string<T>::value, etl::string_view>;

    template <typename T>
    typename enable_for_fixed_size_string<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        size_t stringSize{0};
        size_t skipSize{0};

        const auto fd = stream.free_data();
        const auto found = etl::find(fd.begin(), fd.end(), '\0');

        if (found != fd.end())
        {
            stringSize = static_cast<size_t>(std::distance(fd.begin(), found));
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
        (void)stream.read_unchecked<uint8_t>(skipSize);
        return s;
    }

    // Optional, but not of fixed size string
    template <typename T>
    using enable_for_optional = etl::enable_if<is_etl_optional<T>::value && (!etl_optional_type_is_string<T>::value), T>;

    template <typename T>
    typename enable_for_optional<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        const auto hasValue = etl::read_unchecked<bool>(stream);
        if (hasValue)
        {
            return lrpc::read_unchecked<typename etl_optional_type<T>::type>(stream);
        }

        return {};
    };

    // Optional of fixed size string. Read as an optional of etl::string_view
    template <typename T>
    using enable_for_optional_string = etl::enable_if<is_etl_optional<T>::value && etl_optional_type_is_string<T>::value, etl::optional<etl::string_view>>;

    template <typename T>
    using optional_string_size = etl_string_size<typename etl_optional_type<T>::type>;

    template <typename T>
    typename enable_for_optional_string<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        const auto hasValue = etl::read_unchecked<bool>(stream);
        if (hasValue)
        {
            return lrpc::read_unchecked<etl::string<optional_string_size<T>::value>>(stream);
        }

        return {};
    };

    // Array, but not of fixed size string
    template <typename T>
    using enable_for_array = etl::enable_if<is_etl_array<T>::value && (!etl_array_type_is_string<T>::value), T>;

    template <typename T>
    typename enable_for_array<T>::type
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
    using enable_for_array_of_string = etl::enable_if<is_etl_array<T>::value && etl_array_type_is_string<T>::value, etl::array<etl::string_view, etl_array_size<T>::value>>;

    template <typename T>
    typename enable_for_array_of_string<T>::type
    read_unchecked(etl::byte_stream_reader &stream)
    {
        etl::array<etl::string_view, etl_array_size<T>::value> arr;
        for (auto &el : arr)
        {
            el = lrpc::read_unchecked<typename etl_array_type<T>::type>(stream);
        }

        return arr;
    };

    // deleted write function to allow specializations for custom structs
    template <typename T, typename etl::enable_if<(!etl::is_arithmetic<T>::value) &&
                                                      (!etl::is_enum<T>::value) &&
                                                      (!is_etl_optional<T>::value) &&
                                                      (!is_etl_array<T>::value) &&
                                                      (!is_etl_string<T>::value) &&
                                                      (!etl::is_same<T, etl::string_view>::value),
                                                  bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const T &value) = delete;

    // arithmetic
    template <typename ARI, typename etl::enable_if<etl::is_arithmetic<ARI>::value, bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const ARI &value)
    {
        stream.write_unchecked<ARI>(value);
    };

    // Enum
    template <typename ENUM, typename etl::enable_if<etl::is_enum<ENUM>::value, bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const ENUM &value)
    {
        stream.write_unchecked<uint8_t>(static_cast<uint8_t>(value));
    };

    // auto string
    template <typename T, typename etl::enable_if<etl::is_same<T, etl::string_view>::value, bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const T &value)
    {
        for (auto i = 0U; i < value.size(); ++i)
        {
            stream.write_unchecked<char>(value[i]);
        }

        // final null terminator
        stream.write_unchecked<char>('\0');
    };

    // string
    template <typename T, typename etl::enable_if<is_etl_string<T>::value, bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const T &value)
    {
        for (auto i = 0U; i < value.size(); ++i)
        {
            stream.write_unchecked<char>(value[i]);
        }

        // fill remainder with null terminators
        for (auto i = value.size(); i < value.capacity(); ++i)
        {
            stream.write_unchecked<char>('\0');
        }

        // final null terminator
        stream.write_unchecked<char>('\0');
    };

    // optional
    template <typename OPT, typename etl::enable_if<is_etl_optional<OPT>::value, bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const OPT &value)
    {
        stream.write_unchecked<bool>(value.has_value());
        if (value.has_value())
        {
            lrpc::write_unchecked<typename etl_optional_type<OPT>::type>(stream, value.value());
        }
    };

    // array
    template <typename ARR, typename etl::enable_if<is_etl_array<ARR>::value, bool>::type = true>
    void write_unchecked(etl::byte_stream_writer &stream, const ARR &value)
    {
        for (const auto &el : value)
        {
            lrpc::write_unchecked<typename etl_array_type<ARR>::type>(stream, el);
        }
    };

    // copy string
    template <typename T, typename etl::enable_if<is_etl_string<T>::value, bool>::type = true>
    void copy(const etl::string_view &source, T &destination)
    {
        destination.assign(source.begin(), source.size());
    }

    // copy array of strings
    template <typename T, typename etl::enable_if<is_etl_array<T>::value && etl_array_type_is_string<T>::value, bool>::type = true>
    void copy(const etl::array<etl::string_view, etl_array_size<T>::value> &source, T &destination)
    {
        for (size_t i = 0; i < etl_array_size<T>::value; ++i)
        {
            copy(source[i], destination[i]);
        }
    }

    // copy optional of string
    template <typename T, typename etl::enable_if<is_etl_optional<T>::value && etl_optional_type_is_string<T>::value, bool>::type = true>
    void copy(const etl::optional<etl::string_view> &source, T &destination)
    {
        if (source.has_value())
        {
            destination.emplace(source.value().begin(), source.value().size());
        }
        else
        {
            destination.reset();
        }
    }
}
