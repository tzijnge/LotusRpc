set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

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

add_subdirectory(../../external/gtest External/gtest EXCLUDE_FROM_ALL)

set(LRPC_IS_BUILT ${CMAKE_BINARY_DIR}/lrpc_is_built)
file(GLOB_RECURSE LRPC_PY_SRC_FILES ${CMAKE_SOURCE_DIR}/src/lrpc/*.py ${CMAKE_SOURCE_DIR}/**/lotusrpc-schema.json)

add_custom_command(OUTPUT ${LRPC_IS_BUILT}
                  COMMAND pip install --upgrade --no-deps --force-reinstall ${CMAKE_SOURCE_DIR}
                  COMMAND ${CMAKE_COMMAND} -E touch ${LRPC_IS_BUILT}
                  COMMENT "Build LRPC Python package"
                  DEPENDS ${LRPC_PY_SRC_FILES})

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/lrpccore/EtlRwExtensions.hpp
                  COMMENT "Generate LRPC server core"
                  DEPENDS ${LRPC_IS_BUILT}
                  COMMAND lrpcg cppcore -o ${CMAKE_CURRENT_SOURCE_DIR}/generated)


function(generate_lrpc server_name)
  set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated/${server_name})
  set(LRPC_SERVER_HEADER ${LRPC_OUT_DIR}/${server_name}.hpp)
  set(LRPC_DEF ${CMAKE_SOURCE_DIR}/tests/testdata/Test${server_name}.lrpc.yaml)

  add_custom_command(OUTPUT ${LRPC_SERVER_HEADER}
                  COMMENT "Generate Test${server_name} LRPC files"
                  DEPENDS ${LRPC_DEF} ${LRPC_IS_BUILT}
                  COMMAND lrpcg cpp -d ${LRPC_DEF} -o ${LRPC_OUT_DIR} -w --no-core)

endfunction()

generate_lrpc(Server1)
generate_lrpc(Server2)
generate_lrpc(Server3)
generate_lrpc(Server4)
generate_lrpc(Server5)

set_directory_properties(PROPERTIES ADDITIONAL_CLEAN_FILES ${CMAKE_CURRENT_SOURCE_DIR}/generated)

add_executable(UnitTests
                TestEtlRwExtensions.cpp
                TestServer1.cpp
                TestServer2_s0.cpp
                TestServer2_s1.cpp
                TestServer3.cpp
                TestServer4.cpp
                TestServer5.cpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1/Server1.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2/Server2.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3/Server3.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4/Server4.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server5/Server5.hpp
                ${CMAKE_CURRENT_SOURCE_DIR}/generated/lrpccore/EtlRwExtensions.hpp
                TestServerErrors.cpp)

target_include_directories(UnitTests PRIVATE .)
target_include_directories(UnitTests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/generated)
target_include_directories(UnitTests SYSTEM PRIVATE ${CMAKE_SOURCE_DIR}/external/etl/include)

if(MSVC)
  target_compile_options(UnitTests PRIVATE /W4)
else()
  target_compile_options(UnitTests  PRIVATE -Wall -Wextra)
endif()

set_property(TARGET UnitTests PROPERTY COMPILE_WARNING_AS_ERROR ON)

target_link_libraries(
  UnitTests
  gtest
  gmock
  gtest_main
)

gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults)
