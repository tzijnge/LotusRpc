#pragma once
#include <etl/array.h>
#include <etl/byte_stream.h>
#include <etl/string_view.h>

namespace lrpc
{
    // intentionally incomplete types that are only used as tags
    // for other types. They are never instantiated
    namespace tags
    {
        struct string_auto;
        struct string_n;
        struct bytearray_auto;

        template <typename T>
        struct array_n;
    };

    using bytearray_t = etl::span<const uint8_t>;

    template <typename T>
    struct is_etl_optional : public etl::false_type
    {
    };

    template <typename T>
    struct is_etl_optional<etl::optional<T>> : public etl::true_type
    {
    };

    template <typename T>
    struct is_string_n : public etl::false_type
    {
    };

    template <>
    struct is_string_n<tags::string_n> : public etl::true_type
    {
    };

    template <typename T>
    struct is_array_n : public etl::false_type
    {
    };

    template <typename T>
    struct is_array_n<tags::array_n<T>> : public etl::true_type
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

    // optional param/return type
    template <typename T>
    struct etl_optional_pr_type
    {
    };

    template <typename T>
    struct etl_optional_pr_type<etl::optional<T>>
    {
        using type = etl::optional<T>;
    };

    template <>
    struct etl_optional_pr_type<etl::optional<tags::string_auto>>
    {
        using type = etl::optional<etl::string_view>;
    };

    template <>
    struct etl_optional_pr_type<etl::optional<tags::string_n>>
    {
        using type = etl::optional<etl::string_view>;
    };

    template <>
    struct etl_optional_pr_type<etl::optional<tags::bytearray_auto>>
    {
        using type = etl::optional<bytearray_t>;
    };

    template <typename T>
    struct array_n_type
    {
    };

    template <typename T>
    struct array_n_type<tags::array_n<T>>
    {
        using type = T;
    };

    template <typename T>
    struct array_param_type
    {
    };

    template <typename T>
    struct array_param_type<tags::array_n<T>>
    {
        using type = etl::span<const typename array_n_type<typename tags::array_n<T>>::type>;
    };

    template <>
    struct array_param_type<tags::array_n<tags::string_auto>>
    {
        using type = etl::span<const etl::string_view>;
    };

    template <>
    struct array_param_type<tags::array_n<tags::bytearray_auto>>
    {
        using type = etl::span<const bytearray_t>;
    };

    template <typename T>
    struct array_outparam_type
    {
    };

    template <typename T>
    struct array_outparam_type<tags::array_n<T>>
    {
        using type = etl::span<typename array_n_type<typename tags::array_n<T>>::type>;
    };

    template <>
    struct array_outparam_type<tags::array_n<tags::string_auto>>
    {
        using type = etl::span<etl::string_view>;
    };

    template <>
    struct array_outparam_type<tags::array_n<tags::bytearray_auto>>
    {
        using type = etl::span<bytearray_t>;
    };

    template <typename T>
    using array_n_type_is_string_n = etl::is_same<typename array_n_type<T>::type, tags::string_n>;

    template <typename T>
    using array_n_type_is_string_auto = etl::is_same<typename array_n_type<T>::type, tags::string_auto>;

    template <typename T>
    using is_optional_string_n = etl::is_same<T, etl::optional<tags::string_n>>;

    // deleted read function to allow specializations for custom structs
    template <typename T>
    typename etl::enable_if_t<(!etl::is_arithmetic<T>::value) &&
                                  (!etl::is_enum<T>::value) &&
                                  (!is_etl_optional<T>::value) &&
                                  (!is_array_n<T>::value) &&
                                  (!etl::is_same<T, tags::string_auto>::value) &&
                                  (!etl::is_same<T, tags::string_n>::value) &&
                                  (!etl::is_same<T, tags::bytearray_auto>::value),
                              T>
    read_unchecked(etl::byte_stream_reader &stream) = delete;

    // Arithmetic types
    template <typename T>
    using enable_for_arithmetic = etl::enable_if_t<etl::is_arithmetic<T>::value, T>;

    template <typename T>
    typename enable_for_arithmetic<T>
    read_unchecked(etl::byte_stream_reader &stream)
    {
        return stream.read_unchecked<T>();
    };

    // Enum
    template <typename T>
    using enable_for_enum = etl::enable_if_t<etl::is_enum<T>::value, T>;

    template <typename T>
    typename enable_for_enum<T>
    read_unchecked(etl::byte_stream_reader &stream)
    {
        return static_cast<T>(stream.read_unchecked<uint8_t>());
    }

    // Auto string
    template <typename T>
    using enable_for_auto_string = etl::enable_if_t<etl::is_same<T, tags::string_auto>::value, etl::string_view>;

    template <typename T>
    typename enable_for_auto_string<T>
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
    using enable_for_fixed_size_string = etl::enable_if_t<etl::is_same<T, tags::string_n>::value, etl::string_view>;

    template <typename T>
    typename enable_for_fixed_size_string<T>
    read_unchecked(etl::byte_stream_reader &stream, size_t definitionStringSize)
    {
        size_t actualStringSize{0};
        size_t skipSize{0};

        const auto fd = stream.free_data();
        const auto found = etl::find(fd.begin(), fd.end(), '\0');

        if (found != fd.end())
        {
            actualStringSize = static_cast<size_t>(std::distance(fd.begin(), found));
            actualStringSize = std::min(actualStringSize, definitionStringSize);
            skipSize = actualStringSize + 1;
        }
        else
        {
            actualStringSize = stream.available_bytes();
            actualStringSize = std::min(actualStringSize, definitionStringSize);
            skipSize = actualStringSize;
        }

        const etl::string_view s{stream.end(), actualStringSize};
        (void)stream.read_unchecked<uint8_t>(skipSize);
        return s;
    }

    // Optional, but not of fixed size string
    template <typename T>
    using enable_for_optional = etl::enable_if_t<is_etl_optional<T>::value && (!is_optional_string_n<T>::value), typename etl_optional_pr_type<T>::type>;

    template <typename T>
    typename enable_for_optional<T>
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
    using enable_for_optional_string_n = etl::enable_if_t<is_optional_string_n<T>::value, etl::optional<etl::string_view>>;

    template <typename T>
    typename enable_for_optional_string_n<T>
    read_unchecked(etl::byte_stream_reader &stream, size_t definitionStringSize)
    {
        const auto hasValue = etl::read_unchecked<bool>(stream);
        if (hasValue)
        {
            return lrpc::read_unchecked<tags::string_n>(stream, definitionStringSize);
        }

        return {};
    };

    // Array, but not of fixed size string
    template <typename T>
    using enable_for_array = etl::enable_if_t<is_array_n<T>::value && (!array_n_type_is_string_n<T>::value), void>;

    template <typename T>
    typename enable_for_array<T>
    read_unchecked(etl::byte_stream_reader &stream, typename array_outparam_type<T>::type dest, size_t definitionArraySize)
    {
        const auto s = etl::min(dest.size(), definitionArraySize);
        for (size_t i{0}; i < s; ++i)
        {
            dest.at(i) = lrpc::read_unchecked<typename array_n_type<T>::type>(stream);
        }

        if (s >= definitionArraySize)
        {
            return;
        }

        for (size_t i{0}; i < (definitionArraySize - s); ++i)
        {
            // discard elements that dont fit in the destination
            (void)lrpc::read_unchecked<typename array_n_type<T>::type>(stream);
        }
    };

    // Array of fixed size string. Read as an array of etl::string_view
    template <typename T>
    using enable_for_array_of_string_n = etl::enable_if_t<is_array_n<T>::value && array_n_type_is_string_n<T>::value, void>;

    template <typename T>
    typename enable_for_array_of_string_n<T>
    read_unchecked(etl::byte_stream_reader &stream, etl::span<etl::string_view> dest, size_t definitionArraySize, size_t definitionStringSize)
    {
        const auto s = etl::min(dest.size(), definitionArraySize);
        for (size_t i{0}; i < s; ++i)
        {
            dest.at(i) = lrpc::read_unchecked<tags::string_n>(stream, definitionStringSize);
        }

        if (s < definitionArraySize)
        {
            stream.skip<uint8_t>((definitionArraySize - s) * (definitionStringSize + 1));
        }
    };

    // auto bytearray
    template <typename T>
    using enable_for_bytearray = etl::enable_if_t<etl::is_same<T, tags::bytearray_auto>::value, bytearray_t>;

    template <typename T>
    typename enable_for_bytearray<T>
    read_unchecked(etl::byte_stream_reader &stream)
    {
        size_t readSize = stream.read_unchecked<uint8_t>();
        const auto streamSize = stream.available_bytes();

        readSize = etl::min(readSize, streamSize);

        const bytearray_t ba{reinterpret_cast<const uint8_t *>(stream.end()), readSize};
        (void)stream.skip<uint8_t>(readSize);
        return ba;
    };

    // deleted write function to allow specializations for custom structs
    template <typename T, typename etl::enable_if_t<(!etl::is_arithmetic<T>::value) &&
                                                        (!etl::is_enum<T>::value) &&
                                                        (!is_etl_optional<T>::value) &&
                                                        (!is_array_n<T>::value) &&
                                                        (!etl::is_same<T, tags::string_auto>::value) &&
                                                        (!etl::is_same<T, tags::string_n>::value) &&
                                                        (!etl::is_same<T, tags::bytearray_auto>::value),
                                                    bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, const T &value) = delete;

    // arithmetic
    template <typename ARI, typename etl::enable_if_t<etl::is_arithmetic<ARI>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, const ARI &value)
    {
        stream.write_unchecked<ARI>(value);
    };

    // Enum
    template <typename ENUM, typename etl::enable_if_t<etl::is_enum<ENUM>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, const ENUM &value)
    {
        stream.write_unchecked<uint8_t>(static_cast<uint8_t>(value));
    };

    // auto string
    template <typename T, typename etl::enable_if_t<etl::is_same<T, tags::string_auto>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, const etl::string_view &value)
    {
        for (auto i = 0U; i < value.size(); ++i)
        {
            stream.write_unchecked<char>(value[i]);
        }

        // final null terminator
        stream.write_unchecked<char>('\0');
    };

    // fixed size string
    template <typename T, typename etl::enable_if_t<etl::is_same<T, tags::string_n>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, const etl::string_view &value, size_t definitionStringSize)
    {
        for (auto i = 0U; i < value.size(); ++i)
        {
            stream.write_unchecked<char>(value[i]);
        }

        // fill remainder with null terminators
        for (auto i = value.size(); i < definitionStringSize; ++i)
        {
            stream.write_unchecked<char>('\0');
        }

        // final null terminator
        stream.write_unchecked<char>('\0');
    };

    // auto bytearray
    template <typename T, typename etl::enable_if_t<etl::is_same<T, tags::bytearray_auto>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, const bytearray_t &value)
    {
        stream.write_unchecked<uint8_t>(static_cast<uint8_t>(value.size()));

        const size_t writeSize = etl::min(stream.available_bytes(), value.size());
        for (size_t i = 0; i < writeSize; ++i)
        {
            stream.write_unchecked<uint8_t>(value.at(i));
        }
    };

    // optional, but not of fixed size string
    template <typename OPT, typename etl::enable_if_t<is_etl_optional<OPT>::value && (!is_optional_string_n<OPT>::value), bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, const typename etl_optional_pr_type<OPT>::type &value)
    {
        stream.write_unchecked<bool>(value.has_value());
        if (value.has_value())
        {
            lrpc::write_unchecked<typename etl_optional_type<OPT>::type>(stream, value.value());
        }
    };

    // optional fixed size string
    template <typename OPT, typename etl::enable_if_t<is_optional_string_n<OPT>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, etl::optional<etl::string_view> value, size_t definitionStringSize)
    {
        stream.write_unchecked<bool>(value.has_value());
        if (value.has_value())
        {
            lrpc::write_unchecked<tags::string_n>(stream, value.value(), definitionStringSize);
        }
    };

    // array but not of fixed size string
    template <typename ARR, typename etl::enable_if_t<is_array_n<ARR>::value && (!array_n_type_is_string_n<ARR>::value), bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, typename array_param_type<ARR>::type value, size_t definitionArraySize)
    {
        const auto s = etl::min(value.size(), definitionArraySize);
        for (size_t i{0}; i < s; ++i)
        {
            lrpc::write_unchecked<typename array_n_type<ARR>::type>(stream, value.at(i));
        }

        if (s >= definitionArraySize)
        {
            return;
        }

        for (size_t i{0}; i < (definitionArraySize - s); ++i)
        {
            lrpc::write_unchecked<typename array_n_type<ARR>::type>(stream, {});
        }
    };

    // array of fixed size string
    template <typename ARR, typename etl::enable_if_t<is_array_n<ARR>::value && array_n_type_is_string_n<ARR>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer &stream, etl::span<const etl::string_view> value, size_t definitionArraySize, size_t definitionStringSize)
    {
        const auto s = etl::min(value.size(), definitionArraySize);
        for (size_t i{0}; i < s; ++i)
        {
            lrpc::write_unchecked<tags::string_n>(stream, value.at(i), definitionStringSize);
        }

        if (s >= definitionArraySize)
        {
            return;
        }

        for (size_t i{0}; i < (definitionArraySize - s); ++i)
        {
            lrpc::write_unchecked<tags::string_n>(stream, {}, definitionStringSize);
        }
    };
}