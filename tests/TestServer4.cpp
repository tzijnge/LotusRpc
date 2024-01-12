#include "generated/Server4/Server4_Constants.hpp"
#include <gtest/gtest.h>
#include <type_traits>

static_assert(srv4::c0 == 111, "");
static_assert(std::is_same_v<decltype(srv4::c0), const int32_t>, "");

static_assert(srv4::c1 == 123, "");
static_assert(std::is_same_v<decltype(srv4::c1), const uint8_t>, "");
static_assert(srv4::c2 == -123, "");
static_assert(std::is_same_v<decltype(srv4::c2), const int8_t>, "");

static_assert(srv4::c3 == 1234, "");
static_assert(std::is_same_v<decltype(srv4::c3), const uint16_t>, "");
static_assert(srv4::c4 == -1234, "");
static_assert(std::is_same_v<decltype(srv4::c4), const int16_t>, "");

static_assert(srv4::c5 == 123456, "");
static_assert(std::is_same_v<decltype(srv4::c5), const uint32_t>, "");
static_assert(srv4::c6 == -123456, "");
static_assert(std::is_same_v<decltype(srv4::c6), const int32_t>, "");

static_assert(srv4::c7 == 111222333444, "");
static_assert(std::is_same_v<decltype(srv4::c7), const uint64_t>, "");
static_assert(srv4::c8 == -111222333444, "");
static_assert(std::is_same_v<decltype(srv4::c8), const int64_t>, "");

constexpr float testc9 {111.222};
static_assert(srv4::c9 == testc9, "");
static_assert(std::is_same_v<decltype(srv4::c9), const float>, "");

constexpr float testc10 {222.333};
static_assert(srv4::c10 == testc10, "");
static_assert(std::is_same_v<decltype(srv4::c10), const float>, "");

constexpr double testc11 {333.444};
static_assert(srv4::c11 == testc11, "");
static_assert(std::is_same_v<decltype(srv4::c11), const double>, "");

static_assert(srv4::c12 == true, "");
static_assert(std::is_same_v<decltype(srv4::c12), const bool>, "");

static_assert(srv4::c13 == true, "");
static_assert(std::is_same_v<decltype(srv4::c13), const bool>, "");

static_assert(srv4::c14 == false, "");
static_assert(std::is_same_v<decltype(srv4::c14), const bool>, "");

static_assert(srv4::c15 == true, "");
static_assert(std::is_same_v<decltype(srv4::c15), const bool>, "");

static_assert(srv4::c16 == false, "");
static_assert(std::is_same_v<decltype(srv4::c16), const bool>, "");

constexpr double testc17 {2.3e-5};
static_assert(srv4::c17 == testc17, "");
static_assert(std::is_same_v<decltype(srv4::c17), const double>, "");

static_assert(srv4::c18 == "This is an implicit string constant", "");
static_assert(std::is_same_v<decltype(srv4::c18), const etl::string_view>, "");

static_assert(srv4::c19 == "This is an explicit string constant", "");
static_assert(std::is_same_v<decltype(srv4::c19), const etl::string_view>, "");

static_assert(srv4::c20 == "333.444", "");
static_assert(std::is_same_v<decltype(srv4::c20), const etl::string_view>, "");