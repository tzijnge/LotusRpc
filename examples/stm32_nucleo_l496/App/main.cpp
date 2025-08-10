#include "main.h"
#include "usart.h"
#include "gpio.h"
#include <etl/scheduler.h>

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    MX_GPIO_Init();
    MX_LPUART1_UART_Init();

    etl::scheduler<etl::scheduler_policy_sequential_single, 10> scheduler;

    while (1)
    {
    }
}