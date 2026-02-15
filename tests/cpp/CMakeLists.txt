set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 11)
set(BUILD_GMOCK ON)
set(gtest_force_shared_crt on)

if(MSVC)
  add_compile_options(/fsanitize=address /Zi)
add_link_options(/fsanitize=address)
else()
  add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
add_link_options(-fsanitize=address -static-libasan)
endif()

include(GoogleTest)
mark_as_advanced(
    BUILD_GMOCK BUILD_GTEST
    gmock_build_tests gtest_build_samples gtest_build_tests
    gtest_disable_pthreads
    gtest_hide_internal_symbols
)

add_subdirectory(../../external/gtest External/gtest EXCLUDE_FROM_ALL)

set(LRPC_IS_BUILT ${CMAKE_BINARY_DIR}/lrpc_is_built)
file(GLOB_RECURSE LRPC_PY_SRC_FILES ${CMAKE_SOURCE_DIR}/src/lrpc/*.py
                                    ${CMAKE_SOURCE_DIR}/**/lotusrpc-schema.json
                                    ${CMAKE_SOURCE_DIR}/**/meta.lrpc.yaml)

add_custom_command(OUTPUT ${LRPC_IS_BUILT}
                  COMMAND pip install --upgrade --no-deps --force-reinstall ${CMAKE_SOURCE_DIR}
                  COMMAND ${CMAKE_COMMAND} -E touch ${LRPC_IS_BUILT}
                  COMMENT "Build LRPC Python package"
                  DEPENDS ${LRPC_PY_SRC_FILES})

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/core/lrpccore/EtlRwExtensions.hpp
                  COMMENT "Generate LRPC server core"
                  DEPENDS ${LRPC_IS_BUILT}
                  COMMAND lrpcg cppcore -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/core)


function(generate_lrpc server_name)
  set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated/${server_name})
  set(LRPC_SERVER_HEADER ${LRPC_OUT_DIR}/${server_name}.hpp)
  set(LRPC_DEF ${CMAKE_SOURCE_DIR}/tests/testdata/Test${server_name}.lrpc.yaml)

  add_custom_command(OUTPUT ${LRPC_SERVER_HEADER}
                  COMMENT "Generate Test${server_name} LRPC files"
                  DEPENDS ${LRPC_DEF} ${LRPC_IS_BUILT}
                  COMMAND lrpcg cpp -d ${LRPC_DEF} -o ${LRPC_OUT_DIR} -w)

endfunction()

generate_lrpc(Server1)
generate_lrpc(Server2)
generate_lrpc(Server3)
generate_lrpc(Server4)
generate_lrpc(Server5)
generate_lrpc(Bytearray)
generate_lrpc(RetrieveDefinition)

set_directory_properties(PROPERTIES ADDITIONAL_CLEAN_FILES ${CMAKE_CURRENT_SOURCE_DIR}/generated)

add_executable(UnitTests
                TestEtlRwExtensions.cpp ${CMAKE_CURRENT_SOURCE_DIR}/generated/core/lrpccore/EtlRwExtensions.hpp
                TestServer1.cpp         ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1/Server1.hpp
                TestServer2_s0.cpp      ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2/Server2.hpp
                TestServer2_s1.cpp
                TestServer3.cpp         ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3/Server3.hpp
                TestServer4.cpp         ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4/Server4.hpp
                TestServer5.cpp         ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server5/Server5.hpp
                TestBytearray_char.cpp  ${CMAKE_CURRENT_SOURCE_DIR}/generated/Bytearray/Bytearray.hpp
                TestBytearray_char8_t.cpp
                TestBytearray_signed_char.cpp
                TestBytearray_unsigned_char.cpp
                TestBytearray_int8_t.cpp
                TestBytearray_uint8_t.cpp
                TestRetrieveDefinition.cpp ${CMAKE_CURRENT_SOURCE_DIR}/generated/RetrieveDefinition/RetrieveDefinition.hpp
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
