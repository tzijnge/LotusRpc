# LRPC example for STM32 NucleoL496

* *stm32_nucleo_l496.ioc* created with CubeMX 6.15.0
* Using ARM GCC toolchain version 14.3
* To get started in VS code
  * Install Ninja and add to path
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