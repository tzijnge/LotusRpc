# LRPC example for STM32 NucleoL496

* *stm32_nucleo_l496.ioc* created with CubeMX 6.15.0
* Using ARM GCC toolchain version 14.3
* To get started in VS code
  * Install Ninja and add to path
  * Install the CMake extension for VS code
  * Install the Cortex-debug extension for VS code
  * Add a CMake user presets file (*CmakeUserPresets.json*) to specify the ARM GCC installation directory as follows:

``` JSON
{
    "version": 3,
    "configurePresets": [
        {
            "name": "Debug",
            "inherits": "Debug_no_toolchain",
            "cacheVariables": {
                "TOOLCHAIN_PATH": "path_to_arm_gcc_install"
            }
        },
        {
            "name": "Release",
            "inherits": "Release_no_toolchain",
            "cacheVariables": {
                "TOOLCHAIN_PATH": "path_to_arm_gcc_install"
            }
        }
    ]
}
```

* Connect the board to PC with USB on CN1.
* Build the code and upload the resulting bin file to the target
* Find the COM port of the Nucleo board. It is called "STMicroelectronics STLink Virtual COM Port". Use that COM port name in *lrpcc.config.yaml*
* Open a terminal in the example root directory and communicate with the Nucleo by typing `lrpcc`

## Size comparison

The following table gives an impression of Flash memory usage of LotusRPC. The base line is a simple echo application that receives a byte on UART and echoes it back to the sender. Subsequent entries in the table add more and more LotusRPC features.

| Feature | Flash size (bytes) | |
|---------|--------------------|-|
| Simple echo, no LRPC | 12648 | |
| void f1(uint8_t)     | 13696 | |
| uint8_t f1(uint8_t)  | 13712 | |
| uint8_t f2(uint8_t)  | 13784 | |
| uint16_t f3(uint16_t)  | 13904 | |
| uint32_t f4(uint32_t)  | 14008 | |
| uint64_t f5(uint64_t)  | 14096 | |
| bool f6(bool)  | 14152 | |
| float f7(float)  | 14232 | |
| double f8(double)  | 14312 | |
| [uint8_t, uint8_t] f9()  | 14376 | Introduces `std::tuple` |
| uint8_t[20] f10()  | 14440 | Introduces `etl::array` |
| void f11(uint8_t[20])  | 14504 | Introduces `etl::span` |
| void f12(uint8_t?)  | 14560 | Introduces `etl::optional` |
| uint32_t f13(string)  | 14680 | Introduces `etl::string_view` |
| string_20 f14(string)  | 14968 | Introduces `etl::string` |
| second service  | 15184 | |
