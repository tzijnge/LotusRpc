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

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/TestDecoder/TestDecoder.hpp
                  COMMENT "Generate TestDecoder LRPC files"
                  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/TestDecoder.lrpc.yaml
                  COMMAND python ${CMAKE_SOURCE_DIR}/generator/lotusrpc.py ${CMAKE_CURRENT_SOURCE_DIR}/TestDecoder.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/TestDecoder)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/TestDecoder2/TestDecoder2.hpp
                  COMMENT "Generate TestDecoder2 LRPC files"
                  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/TestDecoder2.lrpc.yaml
                  COMMAND python ${CMAKE_SOURCE_DIR}/generator/lotusrpc.py ${CMAKE_CURRENT_SOURCE_DIR}/TestDecoder2.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/TestDecoder2)

set_directory_properties(PROPERTIES ADDITIONAL_CLEAN_FILES ${CMAKE_CURRENT_SOURCE_DIR}/generated)

add_executable(UnitTests
                TestEtlRwExtensions.cpp
                TestDecoder.cpp
                TestDecoder2_s0.cpp
                TestDecoder2_s1.cpp
                TestServer.cpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/TestDecoder/TestDecoder.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/TestDecoder2/TestDecoder2.hpp)

target_include_directories(UnitTests PRIVATE ../src)
target_include_directories(UnitTests PRIVATE ../external/etl/include)

target_link_libraries(
  UnitTests
  gtest
  gmock
  gtest_main
)

gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults)

