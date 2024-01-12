project(UnitTests VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 11)
set(BUILD_GMOCK ON)
set(gtest_force_shared_crt on)

include(GoogleTest)
mark_as_advanced(
    BUILD_GMOCK BUILD_GTEST
    gmock_build_tests gtest_build_samples gtest_build_tests
    gtest_disable_pthreads
    gtest_hide_internal_symbols
)

add_subdirectory(../external/gtest External/gtest EXCLUDE_FROM_ALL)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1/Server1.hpp
                  COMMENT "Generate TestServer1 LRPC files"
                  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/TestServer1.lrpc.yaml
                  COMMAND python ${CMAKE_SOURCE_DIR}/generator/lotusrpc.py ${CMAKE_CURRENT_SOURCE_DIR}/TestServer1.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2/Server2.hpp
                  COMMENT "Generate TestServer2 LRPC files"
                  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/TestServer2.lrpc.yaml
                  COMMAND python ${CMAKE_SOURCE_DIR}/generator/lotusrpc.py ${CMAKE_CURRENT_SOURCE_DIR}/TestServer2.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3/Server3.hpp
                  COMMENT "Generate TestServer3 LRPC files"
                  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/TestServer3.lrpc.yaml
                  COMMAND python ${CMAKE_SOURCE_DIR}/generator/lotusrpc.py ${CMAKE_CURRENT_SOURCE_DIR}/TestServer3.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4/Server4.hpp
                  COMMENT "Generate TestServer4 LRPC files"
                  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/TestServer4.lrpc.yaml
                  COMMAND python ${CMAKE_SOURCE_DIR}/generator/lotusrpc.py ${CMAKE_CURRENT_SOURCE_DIR}/TestServer4.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4)

set_directory_properties(PROPERTIES ADDITIONAL_CLEAN_FILES ${CMAKE_CURRENT_SOURCE_DIR}/generated)

add_executable(UnitTests
                TestEtlRwExtensions.cpp
                TestServer1.cpp
                TestServer2_s0.cpp
                TestServer2_s1.cpp
                TestServer3.cpp
                TestServer4.cpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1/Server1.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2/Server2.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3/Server3.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4/Server4.hpp)

target_include_directories(UnitTests PRIVATE ../include)
target_include_directories(UnitTests PRIVATE ../external/etl/include)

target_link_libraries(
  UnitTests
  gtest
  gmock
  gtest_main
)

gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults)

