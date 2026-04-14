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

add_library(UnitTests_core INTERFACE)

target_include_directories(UnitTests_core INTERFACE .)
target_include_directories(UnitTests_core SYSTEM INTERFACE ${CMAKE_SOURCE_DIR}/external/etl/include)

if(MSVC)
  target_compile_options(UnitTests_core INTERFACE /W4)
else()
  target_compile_options(UnitTests_core  INTERFACE -Wall -Wextra)
endif()

target_link_libraries(
  UnitTests_core
  INTERFACE gtest
  gmock
  gtest_main
)

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
                  COMMAND lrpcg cppcore -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/core -b uint8_t)


function(generate_lrpc server_name)
  set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated/${server_name})
  set(LRPC_DEF ${CMAKE_SOURCE_DIR}/tests/testdata/Test${server_name}.lrpc.yaml)

  set(OVERLAY_OPTION "")
  if(ARGC GREATER 1)
    set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated/${server_name}/${ARGV1})
    set(LRPC_DEF_OVERLAY ${CMAKE_SOURCE_DIR}/tests/testdata/Test${server_name}_${ARGV1}.lrpc.yaml)
    set(OVERLAY_OPTION "-ov" "${LRPC_DEF_OVERLAY}")
  endif()

  set(LRPC_SERVER_HEADER ${LRPC_OUT_DIR}/${server_name}.hpp)

  add_custom_command(OUTPUT ${LRPC_SERVER_HEADER}
                  COMMENT "Generate Test${server_name} LRPC files"
                  DEPENDS ${LRPC_DEF} ${LRPC_IS_BUILT}
                  COMMAND lrpcg cpp -d ${LRPC_DEF} ${OVERLAY_OPTION} -o ${LRPC_OUT_DIR} -w
                  COMMAND lrpcg puml -d ${LRPC_DEF} -o ${LRPC_OUT_DIR} -w)

endfunction()

generate_lrpc(Server1)
generate_lrpc(Server2)
generate_lrpc(Server3)
generate_lrpc(Server4)
generate_lrpc(Server5)
generate_lrpc(RetrieveDefinition)

set_directory_properties(PROPERTIES ADDITIONAL_CLEAN_FILES ${CMAKE_CURRENT_SOURCE_DIR}/generated)

add_executable(UnitTests
                TestEtlRwExtensions.cpp         ${CMAKE_CURRENT_SOURCE_DIR}/generated/core/lrpccore/EtlRwExtensions.hpp
                TestServer1.cpp                 ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server1/Server1.hpp
                TestServer2_s0.cpp              ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server2/Server2.hpp
                TestServer2_s1.cpp
                TestServer3.cpp                 ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server3/Server3.hpp
                TestServer4.cpp                 ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server4/Server4.hpp
                TestServer5.cpp                 ${CMAKE_CURRENT_SOURCE_DIR}/generated/Server5/Server5.hpp
                TestRetrieveDefinition.cpp      ${CMAKE_CURRENT_SOURCE_DIR}/generated/RetrieveDefinition/RetrieveDefinition.hpp
                TestServerErrors.cpp)

target_link_libraries(
  UnitTests
  UnitTests_core
)

set_property(TARGET UnitTests PROPERTY COMPILE_WARNING_AS_ERROR ON)

gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults)

function(add_test_ba_executable byte_type)
  generate_lrpc(Bytearray ${byte_type})

  set(UNIT_TESTS_BA_EXE UnitTests_ba_${byte_type})

  add_executable(${UNIT_TESTS_BA_EXE}
                  TestBytearray_${byte_type}.cpp
                  ${CMAKE_CURRENT_SOURCE_DIR}/generated/Bytearray/${byte_type}/Bytearray.hpp
  )

  gtest_discover_tests(${UNIT_TESTS_BA_EXE} XML_OUTPUT_DIR TestResults)

  target_link_libraries(
    ${UNIT_TESTS_BA_EXE}
    UnitTests_core
  )

  set_property(TARGET ${UNIT_TESTS_BA_EXE} PROPERTY COMPILE_WARNING_AS_ERROR ON)
endfunction()


add_test_ba_executable(char)
add_test_ba_executable(etl_byte)
add_test_ba_executable(int8_t)
add_test_ba_executable(signed_char)
add_test_ba_executable(uint8_t)
add_test_ba_executable(unsigned_char)
if(CMAKE_CXX_STANDARD GREATER_EQUAL 17)
  add_test_ba_executable(std_byte)
endif()
if(CMAKE_CXX_STANDARD GREATER_EQUAL 20)
  add_test_ba_executable(char8_t)
endif()



# Copy MSVC AddressSanitizer runtime DLL to the output directory
if(MSVC)
  get_filename_component(CXX_COMPILER_DIR "${CMAKE_CXX_COMPILER}" DIRECTORY)

  if(CXX_COMPILER_DIR MATCHES "x64")
    set(ASAN_DLL_ARCH "x86_64")
  elseif(CXX_COMPILER_DIR MATCHES "ARM64")
    set(ASAN_DLL_ARCH "arm64")
  else()
    set(ASAN_DLL_ARCH "x86_64")
  endif()

  find_file(ASAN_DLL_FILE
    NAMES "clang_rt.asan_dynamic-${ASAN_DLL_ARCH}.dll"
    PATHS "${CXX_COMPILER_DIR}"
    REQUIRED
    NO_DEFAULT_PATH
  )

  add_custom_command(TARGET UnitTests POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${ASAN_DLL_FILE}" $<TARGET_FILE_DIR:UnitTests>
    COMMENT "Copying ASAN runtime DLL to test directory"
  )

  unset(ASAN_DLL_FILE CACHE)
endif()
