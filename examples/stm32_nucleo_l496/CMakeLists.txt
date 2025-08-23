cmake_minimum_required(VERSION 3.22)


# Setup compiler settings
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)


if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug")
endif()

set(CMAKE_PROJECT_NAME stm32_nucleo_l496)

project(${CMAKE_PROJECT_NAME})
message("Build type: " ${CMAKE_BUILD_TYPE})

enable_language(C CXX ASM)

add_executable(${CMAKE_PROJECT_NAME})

add_subdirectory(cmake/stm32cubemx)

target_link_directories(${CMAKE_PROJECT_NAME} PRIVATE)

set(LRPC_DIR ${CMAKE_SOURCE_DIR}/App/lrpc)
set(LRPC_OUT_DIR ${LRPC_DIR}/generated)
set(LRPC_SERVER_HEADER ${LRPC_OUT_DIR}/example.hpp)
set(LRPC_DEF ${LRPC_DIR}/example.lrpc.yaml)

add_custom_command(OUTPUT ${LRPC_SERVER_HEADER}
                COMMENT "Generate LRPC files"
                DEPENDS ${LRPC_DEF}
                COMMAND lrpcg cpp -d ${LRPC_DEF} -o ${LRPC_OUT_DIR} -w)

set_directory_properties(PROPERTIES ADDITIONAL_CLEAN_FILES ${LRPC_OUT_DIR})

target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${CMAKE_SOURCE_DIR}/App/main.cpp
    ${LRPC_SERVER_HEADER}
)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    ${CMAKE_SOURCE_DIR}/../../external/etl/include
)

target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE)

target_compile_options(${CMAKE_PROJECT_NAME} PRIVATE
    -Wall
    -Wextra
    -Wconversion
    -Werror
)

# Remove wrong libob.a library dependency when using cpp files
list(REMOVE_ITEM CMAKE_C_IMPLICIT_LINK_LIBRARIES ob)

# Add linked libraries
target_link_libraries(${CMAKE_PROJECT_NAME}
    stm32cubemx
)
