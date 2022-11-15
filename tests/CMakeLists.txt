project(UnitTests VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)
set(BUILD_GMOCK ON)

include(GoogleTest)
mark_as_advanced(
    BUILD_GMOCK BUILD_GTEST
    gmock_build_tests gtest_build_samples gtest_build_tests
    gtest_disable_pthreads gtest_force_shared_crt
    gtest_hide_internal_symbols
)

add_subdirectory(../external/gtest External/gtest EXCLUDE_FROM_ALL)

add_executable(UnitTests
                TestDecoder.cpp
                TestServer.cpp)

target_include_directories(UnitTests PRIVATE ../src)
target_include_directories(UnitTests PRIVATE ../external/etl/include)

target_link_libraries(
  UnitTests
  gtest
  gmock
  gtest_main
)

gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults)
