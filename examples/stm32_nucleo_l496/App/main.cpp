#include "main.h"
#include "usart.h"
#include "lrpc/generated/example.hpp"

extern "C" void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    (void)huart;
}

class Srv1 : public srv1ServiceShim
{
public:
    std::tuple<uint16_t, uint32_t> f1(uint16_t p1, uint32_t p2) override
    {
        return {p1 + 10, p2 + 20};
    }
};

class ExampleServer : public example
{
public:
    ExampleServer()
    {
        registerService(srv1);
    }

    void lrpcTransmit(etl::span<const uint8_t> bytes) override
    {
        HAL_UART_Transmit(&hlpuart1, bytes.data(), static_cast<uint16_t>(bytes.size()), HAL_MAX_DELAY);
    }

private:
    Srv1 srv1;
};

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    MX_LPUART1_UART_Init();

    SysTick->CTRL &= ~(SysTick_CTRL_ENABLE_Msk | SysTick_CTRL_TICKINT_Msk);

    ExampleServer server;

    uint8_t receiveBuffer{0};

    HAL_UART_Receive_IT(&hlpuart1, &receiveBuffer, 1);

    while (true)
    {

        __WFI();

        server.lrpcReceive(receiveBuffer);

        HAL_UART_Receive_IT(&hlpuart1, &receiveBuffer, 1);

        HAL_GPIO_TogglePin(LD3_GPIO_Port, LD3_Pin);
    }
}