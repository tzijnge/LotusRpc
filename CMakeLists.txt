cmake_minimum_required(VERSION 3.24.0)

project(UnitTests)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

enable_testing()
add_subdirectory(tests/cpp)