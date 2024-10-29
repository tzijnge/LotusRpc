project(UnitTests VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 14)
set(BUILD_GMOCK ON)
set(gtest_force_shared_crt on)

include(GoogleTest)
mark_as_advanced(
    BUILD_GMOCK BUILD_GTEST
    gmock_build_tests gtest_build_samples gtest_build_tests
    gtest_disable_pthreads
    gtest_hide_internal_symbols
)

add_subdirectory(../../external/gtest External/gtest EXCLUDE_FROM_ALL)

set(LRPC_IS_BUILT ${CMAKE_BINARY_DIR}/lrpc_is_built)
file(GLOB_RECURSE LRPC_PY_SRC_FILES ${CMAKE_SOURCE_DIR}/src/lrpc/*.py ${CMAKE_SOURCE_DIR}/**/lotusrpc-schema.json)

add_custom_command(OUTPUT ${LRPC_IS_BUILT}
                  COMMAND pip install --upgrade --no-deps --force-reinstall ${CMAKE_SOURCE_DIR}
                  COMMAND ${CMAKE_COMMAND} -E touch ${LRPC_IS_BUILT}
                  COMMENT "Build LRPC Python package"
                  DEPENDS ${LRPC_PY_SRC_FILES})

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1/Server1.hpp
                  COMMENT "Generate TestServer1 LRPC files"
                  DEPENDS ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer1.lrpc.yaml ${LRPC_IS_BUILT}
                  COMMAND lrpcg -w ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer1.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2/Server2.hpp
                  COMMENT "Generate TestServer2 LRPC files"
                  DEPENDS ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer2.lrpc.yaml ${LRPC_IS_BUILT}
                  COMMAND lrpcg -w ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer2.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3/Server3.hpp
                  COMMENT "Generate TestServer3 LRPC files"
                  DEPENDS ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer3.lrpc.yaml ${LRPC_IS_BUILT}
                  COMMAND lrpcg -w ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer3.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4/Server4.hpp
                  COMMENT "Generate TestServer4 LRPC files"
                  DEPENDS ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer4.lrpc.yaml ${LRPC_IS_BUILT}
                  COMMAND lrpcg -w ${CMAKE_SOURCE_DIR}/tests/testdata/TestServer4.lrpc.yaml -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4)

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

target_include_directories(UnitTests PRIVATE .)
target_include_directories(UnitTests PRIVATE ${CMAKE_SOURCE_DIR}/resources/cpp/include)
target_include_directories(UnitTests SYSTEM PRIVATE ${CMAKE_SOURCE_DIR}/external/etl/include)

if(MSVC)
  target_compile_options(UnitTests PRIVATE /W4)
else()
  target_compile_options(UnitTests  PRIVATE -Wall -Wextra)
endif()

set_property(TARGET UnitTests PROPERTY COMPILE_WARNING_AS_ERROR OFF)

target_link_libraries(
  UnitTests
  gtest
  gmock
  gtest_main
)

gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults)

