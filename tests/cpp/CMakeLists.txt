if(NOT DEFINED CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 11)
endif()

option(ENABLE_ASAN "Enable AddressSanitizer" ON)

if(ENABLE_ASAN)
  if(MSVC)
    add_compile_options(/fsanitize=address /Zi)
    add_link_options(/fsanitize=address)
  else()
    add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address)
  endif()

  if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    add_link_options(-static-libasan)
  endif()
endif()

set(BUILD_GMOCK ON)
set(gtest_force_shared_crt ON)

include(FetchContent)

FetchContent_Declare(
  googletest
  URL      https://github.com/google/googletest/archive/refs/tags/v1.17.0.tar.gz
  URL_HASH SHA256=65fab701d9829d38cb77c14acdc431d2108bfdbf8979e40eb8ae567edf10b27c
)

FetchContent_Declare(
  etl
  URL      https://github.com/ETLCPP/etl/archive/refs/tags/20.47.1.tar.gz
  URL_HASH SHA256=ea4cff73a18106c2fbae35b9200f8099d1a08ed70ffcca392c4264c3825eedb3
)

FetchContent_MakeAvailable(googletest etl)

mark_as_advanced(
  BUILD_GMOCK BUILD_GTEST
  gmock_build_tests gtest_build_samples gtest_build_tests
  gtest_disable_pthreads
  gtest_hide_internal_symbols
)

include(GoogleTest)
include(${CMAKE_SOURCE_DIR}/cmake/CompilerWarnings.cmake)

# set(Python3_FIND_REGISTRY NEVER)
# set(Python3_FIND_STRATEGY LOCATION)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_library(UnitTests_core INTERFACE)

target_include_directories(UnitTests_core INTERFACE .)
target_set_warnings(UnitTests_core INTERFACE)

target_link_libraries(
  UnitTests_core
  INTERFACE
    gtest
    gmock
    gtest_main
    etl::etl
)

set(LRPC_IS_BUILT ${CMAKE_BINARY_DIR}/lrpc_is_built)
file(GLOB_RECURSE LRPC_PY_SRC_FILES
  ${CMAKE_SOURCE_DIR}/src/lrpc/*.py
  ${CMAKE_SOURCE_DIR}/**/lotusrpc-schema.json
  ${CMAKE_SOURCE_DIR}/**/meta.lrpc.yaml
)

add_custom_command(OUTPUT ${LRPC_IS_BUILT}
                  COMMAND ${Python3_EXECUTABLE} -m pip install --force-reinstall ${CMAKE_SOURCE_DIR}
                  COMMAND ${CMAKE_COMMAND} -E touch ${LRPC_IS_BUILT}
                  COMMENT "Build LRPC Python package"
                  DEPENDS ${LRPC_PY_SRC_FILES})

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/generated/core/lrpccore/EtlRwExtensions.hpp
                  COMMENT "Generate LRPC server core"
                  DEPENDS ${LRPC_IS_BUILT}
                  COMMAND ${Python3_EXECUTABLE} -m lrpc.tools.lrpcg.lrpcg cppcore -o ${CMAKE_CURRENT_SOURCE_DIR}/generated/core -b uint8_t)


function(generate_lrpc server_name)
  set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated/${server_name})
  set(LRPC_DEF ${CMAKE_SOURCE_DIR}/tests/testdata/Test${server_name}.lrpc.yaml)

  set(OVERLAY_OPTION "")
  set(OVERLAY_DEPENDS "")
  if(ARGC GREATER 1)
    set(LRPC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated/${server_name}/${ARGV1})
    set(LRPC_DEF_OVERLAY ${CMAKE_SOURCE_DIR}/tests/testdata/Test${server_name}_${ARGV1}.lrpc.yaml)
    set(OVERLAY_OPTION "-ov" "${LRPC_DEF_OVERLAY}")
    set(OVERLAY_DEPENDS "${LRPC_DEF_OVERLAY}")
  endif()

  set(LRPC_SERVER_HEADER ${LRPC_OUT_DIR}/${server_name}.hpp)

  add_custom_command(OUTPUT ${LRPC_SERVER_HEADER}
                  COMMENT "Generate Test${server_name} LRPC files"
                  DEPENDS ${LRPC_DEF} ${OVERLAY_DEPENDS} ${LRPC_IS_BUILT}
                  COMMAND ${Python3_EXECUTABLE} -m lrpc.tools.lrpcg.lrpcg cpp -d ${LRPC_DEF} ${OVERLAY_OPTION} -o ${LRPC_OUT_DIR} -w
                  COMMAND ${Python3_EXECUTABLE} -m lrpc.tools.lrpcg.lrpcg puml -d ${LRPC_DEF} -o ${LRPC_OUT_DIR} -w)

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

gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults DISCOVERY_MODE PRE_TEST)

function(add_test_ba_executable byte_type)
  generate_lrpc(Bytearray ${byte_type})

  set(UNIT_TESTS_BA_EXE UnitTests_ba_${byte_type})

  add_executable(${UNIT_TESTS_BA_EXE}
                  TestBytearray_${byte_type}.cpp
                  ${CMAKE_CURRENT_SOURCE_DIR}/generated/Bytearray/${byte_type}/Bytearray.hpp
  )

  gtest_discover_tests(${UNIT_TESTS_BA_EXE} XML_OUTPUT_DIR TestResults DISCOVERY_MODE PRE_TEST)

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


if(ENABLE_ASAN AND MSVC)
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
