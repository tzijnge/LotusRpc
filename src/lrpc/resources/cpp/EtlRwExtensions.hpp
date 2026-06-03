#pragma once
#include <algorithm>
#include <limits>
#include <type_traits>

#include <etl/byte_stream.h>

#include "LrpcByteTypes.hpp"
#include "LrpcTypes.hpp"

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

    template <typename T>
    struct is_optional : public std::false_type
    {
    };

    template <typename T>
    struct is_optional<lrpc::optional<T>> : public std::true_type
    {
    };

    template <typename T>
    struct is_string_n : public std::false_type
    {
    };

    template <>
    struct is_string_n<tags::string_n> : public std::true_type
    {
    };

    template <typename T>
    struct is_array_n : public std::false_type
    {
    };

    template <typename T>
    struct is_array_n<tags::array_n<T>> : public std::true_type
    {
    };

    template <typename T>
    struct optional_type
    {
    };

    template <typename T>
    struct optional_type<lrpc::optional<T>>
    {
        using type = T;
    };

    // optional param/return type
    template <typename T>
    struct optional_pr_type
    {
    };

    template <typename T>
    struct optional_pr_type<lrpc::optional<T>>
    {
        using type = lrpc::optional<T>;
    };

    template <>
    struct optional_pr_type<lrpc::optional<tags::string_auto>>
    {
        using type = lrpc::optional<lrpc::string_view>;
    };

    template <>
    struct optional_pr_type<lrpc::optional<tags::string_n>>
    {
        using type = lrpc::optional<lrpc::string_view>;
    };

    template <>
    struct optional_pr_type<lrpc::optional<tags::bytearray_auto>>
    {
        using type = lrpc::optional<bytearray>;
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
        using type = lrpc::span<const typename array_n_type<typename tags::array_n<T>>::type>;
    };

    template <>
    struct array_param_type<tags::array_n<tags::string_auto>>
    {
        using type = lrpc::span<const lrpc::string_view>;
    };

    template <>
    struct array_param_type<tags::array_n<tags::string_n>>
    {
        using type = lrpc::span<const lrpc::string_view>;
    };

    template <>
    struct array_param_type<tags::array_n<tags::bytearray_auto>>
    {
        using type = lrpc::span<const bytearray>;
    };

    template <typename T>
    struct array_outparam_type
    {
    };

    template <typename T>
    struct array_outparam_type<tags::array_n<T>>
    {
        using type = lrpc::span<typename array_n_type<typename tags::array_n<T>>::type>;
    };

    template <>
    struct array_outparam_type<tags::array_n<tags::string_auto>>
    {
        using type = lrpc::span<lrpc::string_view>;
    };

    template <>
    struct array_outparam_type<tags::array_n<tags::string_n>>
    {
        using type = lrpc::span<lrpc::string_view>;
    };

    template <>
    struct array_outparam_type<tags::array_n<tags::bytearray_auto>>
    {
        using type = lrpc::span<bytearray>;
    };

    template <typename T>
    using array_n_type_is_string_n = std::is_same<typename array_n_type<T>::type, tags::string_n>;

    template <typename T>
    using is_optional_string_n = std::is_same<T, lrpc::optional<tags::string_n>>;

    // deleted read function to allow specializations for custom structs
    template <typename T>
    typename std::enable_if_t<
        (!std::is_arithmetic<T>::value) && (!std::is_enum<T>::value) && (!is_optional<T>::value) &&
            (!is_array_n<T>::value) && (!std::is_same<T, tags::string_auto>::value) &&
            (!std::is_same<T, tags::string_n>::value) && (!std::is_same<T, tags::bytearray_auto>::value),
        T>
    read_unchecked(etl::byte_stream_reader& reader) = delete;

    // Arithmetic types
    template <typename T>
    using enable_for_arithmetic = std::enable_if_t<std::is_arithmetic<T>::value, T>;

    template <typename T>
    enable_for_arithmetic<T> read_unchecked(etl::byte_stream_reader& reader)
    {
        return reader.read_unchecked<T>();
    };

    // Enum
    template <typename T>
    using enable_for_enum = std::enable_if_t<std::is_enum<T>::value, T>;

    template <typename T>
    enable_for_enum<T> read_unchecked(etl::byte_stream_reader& reader)
    {
        return static_cast<T>(reader.read_unchecked<uint8_t>());
    }

    // Auto string
    template <typename T>
    using enable_for_auto_string = std::enable_if_t<std::is_same<T, tags::string_auto>::value, lrpc::string_view>;

    template <typename T>
    enable_for_auto_string<T> read_unchecked(etl::byte_stream_reader& reader)
    {
        size_t stringSize{0};
        size_t skipSize{0};

        const auto fd = reader.free_data();
        const auto* const found = std::find(fd.begin(), fd.end(), '\0');

        if (found != fd.end())
        {
            stringSize = static_cast<size_t>(std::distance(fd.begin(), found));
            skipSize = stringSize + 1;
        }
        else
        {
            stringSize = reader.available_bytes();
            skipSize = stringSize;
        }

        const lrpc::string_view readValue{reader.end(), stringSize};
        (void)reader.read_unchecked<uint8_t>(skipSize);
        return readValue;
    };

    // Fixed size string
    template <typename T>
    using enable_for_fixed_size_string = std::enable_if_t<std::is_same<T, tags::string_n>::value, lrpc::string_view>;

    template <typename T>
    enable_for_fixed_size_string<T> read_unchecked(etl::byte_stream_reader& reader, const size_t definitionStringSize)
    {
        size_t actualStringSize{reader.available_bytes()};

        const auto fd = reader.free_data();
        const auto* const found = std::find(fd.begin(), fd.end(), '\0');

        if (found != fd.end())
        {
            actualStringSize = static_cast<size_t>(std::distance(fd.begin(), found));
        }

        actualStringSize = std::min(actualStringSize, definitionStringSize);

        const auto fixedSlotSize = definitionStringSize + 1;
        const auto skipSize = std::min(reader.available_bytes(), fixedSlotSize);
        const lrpc::string_view readValue{reader.end(), actualStringSize};

        (void)reader.skip<uint8_t>(skipSize);

        return readValue;
    }

    // auto bytearray
    template <typename T>
    using enable_for_bytearray = std::enable_if_t<std::is_same<T, tags::bytearray_auto>::value, bytearray>;

    template <typename T>
    enable_for_bytearray<T> read_unchecked(etl::byte_stream_reader& reader)
    {
        size_t readSize = reader.read_unchecked<uint8_t>();
        const auto streamSize = reader.available_bytes();

        readSize = std::min(readSize, streamSize);

        const auto ba = reader.free_data().take<const lrpc::byte>(readSize);
        (void)reader.skip<lrpc::byte>(readSize);
        return ba;
    };

    // Optional, but not of fixed size string
    template <typename T>
    using enable_for_optional = std::enable_if_t<is_optional<T>::value && (!is_optional_string_n<T>::value),
                                                 typename optional_pr_type<T>::type>;

    template <typename T>
    enable_for_optional<T> read_unchecked(etl::byte_stream_reader& reader)
    {
        const auto hasValue = etl::read_unchecked<bool>(reader);
        if (hasValue)
        {
            return lrpc::read_unchecked<typename optional_type<T>::type>(reader);
        }

        return {};
    };

    // Optional of fixed size string. Read as an optional of lrpc::string_view
    template <typename T>
    using enable_for_optional_string_n =
        std::enable_if_t<is_optional_string_n<T>::value, lrpc::optional<lrpc::string_view>>;

    template <typename T>
    enable_for_optional_string_n<T> read_unchecked(etl::byte_stream_reader& reader, const size_t definitionStringSize)
    {
        const auto hasValue = etl::read_unchecked<bool>(reader);
        if (hasValue)
        {
            return lrpc::read_unchecked<tags::string_n>(reader, definitionStringSize);
        }

        return {};
    };

    // Array, but not of fixed size string
    template <typename T>
    using enable_for_array = std::enable_if_t<is_array_n<T>::value && (!array_n_type_is_string_n<T>::value), void>;

    template <typename T>
    enable_for_array<T> read_unchecked(etl::byte_stream_reader& reader, typename array_outparam_type<T>::type dest,
                                       const size_t definitionArraySize)
    {
        const auto size = std::min(dest.size(), definitionArraySize);
        for (size_t i{0}; i < size; ++i)
        {
            dest.at(i) = lrpc::read_unchecked<typename array_n_type<T>::type>(reader);
        }

        if (size >= definitionArraySize)
        {
            return;
        }

        for (size_t i{0}; i < (definitionArraySize - size); ++i)
        {
            // discard elements that dont fit in the destination
            (void)lrpc::read_unchecked<typename array_n_type<T>::type>(reader);
        }
    };

    // Array of fixed size string. Read as an array of lrpc::string_view
    template <typename T>
    using enable_for_array_of_string_n =
        std::enable_if_t<is_array_n<T>::value && array_n_type_is_string_n<T>::value, void>;

    template <typename T>
    enable_for_array_of_string_n<T> read_unchecked(etl::byte_stream_reader& reader,
                                                   typename array_outparam_type<T>::type dest,
                                                   const size_t definitionArraySize, const size_t definitionStringSize)
    {
        const auto size = std::min(dest.size(), definitionArraySize);
        for (size_t i{0}; i < size; ++i)
        {
            dest.at(i) = lrpc::read_unchecked<tags::string_n>(reader, definitionStringSize);
        }

        if (size < definitionArraySize)
        {
            reader.skip<uint8_t>((definitionArraySize - size) * (definitionStringSize + 1));
        }
    };

    // deleted write function to allow specializations for custom structs
    template <typename T,
              typename std::enable_if_t<
                  (!std::is_arithmetic<T>::value) && (!std::is_enum<T>::value) && (!is_optional<T>::value) &&
                      (!is_array_n<T>::value) && (!std::is_same<T, tags::string_auto>::value) &&
                      (!std::is_same<T, tags::string_n>::value) && (!std::is_same<T, tags::bytearray_auto>::value),
                  bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, const T& value) = delete;

    // arithmetic
    template <typename ARI, typename std::enable_if_t<std::is_arithmetic<ARI>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, const ARI& value)
    {
        writer.write_unchecked<ARI>(value);
    };

    // Enum
    template <typename ENUM, typename std::enable_if_t<std::is_enum<ENUM>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, const ENUM& value)
    {
        writer.write_unchecked<uint8_t>(static_cast<uint8_t>(value));
    };

    // auto string
    template <typename T, typename std::enable_if_t<std::is_same<T, tags::string_auto>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, const lrpc::string_view& value)
    {
        for (const char character : value)
        {
            writer.write_unchecked<char>(character);
        }

        // final null terminator
        writer.write_unchecked<char>('\0');
    };

    // fixed size string
    template <typename T, typename std::enable_if_t<std::is_same<T, tags::string_n>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, const lrpc::string_view& value,
                         const size_t definitionStringSize)
    {
        const size_t writeSize = std::min<size_t>(definitionStringSize, value.size());

        for (size_t i = 0; i < writeSize; ++i)
        {
            writer.write_unchecked<char>(value.at(i));
        }

        // fill remainder with null terminators
        for (auto i = value.size(); i < definitionStringSize; ++i)
        {
            writer.write_unchecked<char>('\0');
        }

        // final null terminator
        writer.write_unchecked<char>('\0');
    };

    // auto bytearray
    template <typename T, typename std::enable_if_t<std::is_same<T, tags::bytearray_auto>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, const bytearray& value)
    {
        constexpr size_t baMaxSize{std::numeric_limits<uint8_t>::max()};
        const size_t ba_size = std::min<size_t>(baMaxSize, value.size());

        writer.write_unchecked<uint8_t>(static_cast<uint8_t>(ba_size));

        const size_t writeSize = std::min(writer.available_bytes(), ba_size);
        for (size_t i = 0; i < writeSize; ++i)
        {
            lrpc::write_unchecked<lrpc::byte>(writer, value.at(i));
        }
    };

    // optional, but not of fixed size string
    template <typename OPT,
              typename std::enable_if_t<is_optional<OPT>::value && (!is_optional_string_n<OPT>::value), bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, const typename optional_pr_type<OPT>::type& value)
    {
        writer.write_unchecked<bool>(value.has_value());
        if (value.has_value())
        {
            lrpc::write_unchecked<typename optional_type<OPT>::type>(writer, value.value());
        }
    };

    // optional fixed size string
    template <typename OPT, typename std::enable_if_t<is_optional_string_n<OPT>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, lrpc::optional<lrpc::string_view> value,
                         const size_t definitionStringSize)
    {
        writer.write_unchecked<bool>(value.has_value());
        if (value.has_value())
        {
            lrpc::write_unchecked<tags::string_n>(writer, value.value(), definitionStringSize);
        }
    };

    // array but not of fixed size string
    template <typename ARR,
              typename std::enable_if_t<is_array_n<ARR>::value && (!array_n_type_is_string_n<ARR>::value), bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, typename array_param_type<ARR>::type value,
                         const size_t definitionArraySize)
    {
        const auto size = std::min(value.size(), definitionArraySize);
        for (size_t i{0}; i < size; ++i)
        {
            lrpc::write_unchecked<typename array_n_type<ARR>::type>(writer, value.at(i));
        }

        if (size >= definitionArraySize)
        {
            return;
        }

        for (size_t i{0}; i < (definitionArraySize - size); ++i)
        {
            lrpc::write_unchecked<typename array_n_type<ARR>::type>(writer, {});
        }
    };

    // array of fixed size string
    // NOLINTBEGIN(bugprone-easily-swappable-parameters)
    template <typename ARR,
              typename std::enable_if_t<is_array_n<ARR>::value && array_n_type_is_string_n<ARR>::value, bool> = true>
    void write_unchecked(etl::byte_stream_writer& writer, typename array_param_type<ARR>::type value,
                         const size_t definitionArraySize, const size_t definitionStringSize)
    // NOLINTEND(bugprone-easily-swappable-parameters)
    {
        const auto size = std::min(value.size(), definitionArraySize);
        for (size_t i{0}; i < size; ++i)
        {
            lrpc::write_unchecked<tags::string_n>(writer, value.at(i), definitionStringSize);
        }

        if (size >= definitionArraySize)
        {
            return;
        }

        for (size_t i{0}; i < (definitionArraySize - size); ++i)
        {
            lrpc::write_unchecked<tags::string_n>(writer, {}, definitionStringSize);
        }
    };
}