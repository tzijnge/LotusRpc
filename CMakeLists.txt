cmake_minimum_required(VERSION 3.0.0)
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

add_subdirectory(../External/googletest External/googletest EXCLUDE_FROM_ALL)

add_custom_command(
    OUTPUT  ${CMAKE_CURRENT_BINARY_DIR}/erpc/generated/smole_erpc.h
    COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/../Scripts/erpcgen.py --generate c --output ${CMAKE_CURRENT_BINARY_DIR}/erpc/generated
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/../erpc/smole_erpc.erpc
)

add_executable(UnitTests TestDualBankFlashDetail.cpp ../Implant_Main_uC/App/DualBankFlashDetail.cpp
                        # TestUpgrade.cpp ../Implant_Main_uC/App/Upgrade.cpp Stubs/StubDualBankFlash.cpp
                        TestAlarmDispatcher.cpp ../Implant_Main_uC/App/Rtc/AlarmDispatcher.cpp
                        TestDateTime.cpp ../Implant_Main_uC/App/Rtc/DateTime.cpp
						TestTokenizer.cpp 
                        TestSingleton.cpp
                        TestQueue.cpp
                        TestRpc.cpp
                        ${CMAKE_CURRENT_BINARY_DIR}/erpc/generated/smole_erpc.h)

target_include_directories(UnitTests PRIVATE Stubs)
target_include_directories(UnitTests PRIVATE ../External/etl/include)
target_include_directories(UnitTests PRIVATE ../Implant_Main_uC/App)
target_include_directories(UnitTests PRIVATE ../Wearable/Src/application)
target_include_directories(UnitTests PRIVATE ../Implant_Main_uC/Middlewares/erpc)
target_include_directories(UnitTests PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/erpc/generated)

target_link_libraries(
  UnitTests
  gtest
  gmock
  gtest_main
)

enable_testing()
gtest_discover_tests(UnitTests XML_OUTPUT_DIR TestResults)
