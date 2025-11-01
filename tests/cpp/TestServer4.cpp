#include "generated/Server4/Server4.hpp"
#include <gtest/gtest.h>
#include <type_traits>

static_assert(srv4::c0 == 111, "");
static_assert(std::is_same<decltype(srv4::c0), const int32_t>::value, "");

static_assert(srv4::c1 == 123, "");
static_assert(std::is_same<decltype(srv4::c1), const uint8_t>::value, "");
static_assert(srv4::c2 == -123, "");
static_assert(std::is_same<decltype(srv4::c2), const int8_t>::value, "");

static_assert(srv4::c3 == 1234, "");
static_assert(std::is_same<decltype(srv4::c3), const uint16_t>::value, "");
static_assert(srv4::c4 == -1234, "");
static_assert(std::is_same<decltype(srv4::c4), const int16_t>::value, "");

static_assert(srv4::c5 == 123456, "");
static_assert(std::is_same<decltype(srv4::c5), const uint32_t>::value, "");
static_assert(srv4::c6 == -123456, "");
static_assert(std::is_same<decltype(srv4::c6), const int32_t>::value, "");

static_assert(srv4::c7 == 111222333444, "");
static_assert(std::is_same<decltype(srv4::c7), const uint64_t>::value, "");
static_assert(srv4::c8 == -111222333444, "");
static_assert(std::is_same<decltype(srv4::c8), const int64_t>::value, "");

constexpr float testc9{111.222F};
static_assert(srv4::c9 == testc9, "");
static_assert(std::is_same<decltype(srv4::c9), const float>::value, "");

constexpr float testc10{222.333F};
static_assert(srv4::c10 == testc10, "");
static_assert(std::is_same<decltype(srv4::c10), const float>::value, "");

constexpr double testc11{333.444};
static_assert(srv4::c11 == testc11, "");
static_assert(std::is_same<decltype(srv4::c11), const double>::value, "");

static_assert(srv4::c12 == true, "");
static_assert(std::is_same<decltype(srv4::c12), const bool>::value, "");

static_assert(srv4::c13 == true, "");
static_assert(std::is_same<decltype(srv4::c13), const bool>::value, "");

static_assert(srv4::c14 == false, "");
static_assert(std::is_same<decltype(srv4::c14), const bool>::value, "");

static_assert(srv4::c15 == true, "");
static_assert(std::is_same<decltype(srv4::c15), const bool>::value, "");

static_assert(srv4::c16 == false, "");
static_assert(std::is_same<decltype(srv4::c16), const bool>::value, "");

constexpr double testc17{2.3e-5};
static_assert(srv4::c17 == testc17, "");
static_assert(std::is_same<decltype(srv4::c17), const double>::value, "");

static_assert(srv4::c18 == "This is an implicit string constant", "");
static_assert(std::is_same<decltype(srv4::c18), const etl::string_view>::value, "");

static_assert(srv4::c19 == "This is an explicit string constant", "");
static_assert(std::is_same<decltype(srv4::c19), const etl::string_view>::value, "");

static_assert(srv4::c20 == "333.444", "");
static_assert(std::is_same<decltype(srv4::c20), const etl::string_view>::value, "");

static_assert(srv4::c21 == "444.444", "");
static_assert(std::is_same<decltype(srv4::c21), const etl::string_view>::value, "");

static_assert(static_cast<int>(srv4::MyEnum::V0) == 0, "");
static_assert(static_cast<int>(srv4::MyEnum::V1) == 1, "");
static_assert(static_cast<int>(srv4::MyEnum::V2) == 2, "");
static_assert(static_cast<int>(srv4::MyEnum::V3) == 3, "");

static_assert(static_cast<int>(srv4::MyEnum4::f1) == 0, "");
static_assert(static_cast<int>(srv4::MyEnum4::f2) == 1, "");
static_assert(static_cast<int>(srv4::MyEnum4::f3) == 222, "");
static_assert(static_cast<int>(srv4::MyEnum4::f4) == 223, "");

static_assert(srv4::meta::DefinitionVersion == "11.22.33.44", "");
static_assert(std::is_same<decltype(srv4::meta::DefinitionVersion), const etl::string_view>::value, "");

static_assert(!srv4::meta::LrpcVersion.empty(), "");
static_assert(std::is_same<decltype(srv4::meta::LrpcVersion), const etl::string_view>::value, "");