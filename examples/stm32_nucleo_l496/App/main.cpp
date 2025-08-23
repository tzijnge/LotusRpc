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
    uint8_t f1(uint8_t p1) override
    {
        return p1;
    }

    uint8_t f2(uint8_t p1) override
    {
        return p1;
    }

    uint16_t f3(uint16_t p1) override
    {
        return p1;
    }

    uint32_t f4(uint32_t p1) override
    {
        return p1;
    }

    uint64_t f5(uint64_t p1) override
    {
        return p1;
    }

    bool f6(bool p1) override
    {
        return p1;
    }

    float f7(float p1) override
    {
        return p1;
    }

    double f8(double p1) override
    {
        return p1;
    }

    std::tuple<uint8_t, uint8_t> f9() override
    {
        return {123, 456};
    }

    etl::array<uint8_t, 20> f10() override
    {
        return {};
    }

    void f11(const etl::span<const uint8_t> &) override
    {
    }

    void f12(const etl::optional<uint8_t> &) override
    {
    }

    uint32_t f13(const etl::string_view &p1) override
    {
        return p1.size();
    }

    etl::string<20> f14(const etl::string_view &p1) override
    {
        return {p1.begin(), p1.end()};
    }
};

class Srv2 : public srv2ServiceShim
{
public:
    int32_t f1(int32_t p1) override
    {
        return p1;
    }
};

class ExampleServer : public example
{
public:
    ExampleServer()
    {
        registerService(srv1);
        registerService(srv2);
    }

    void lrpcTransmit(etl::span<const uint8_t> bytes) override
    {
        HAL_UART_Transmit(&hlpuart1, bytes.data(), static_cast<uint16_t>(bytes.size()), HAL_MAX_DELAY);
    }

private:
    Srv1 srv1;
    Srv2 srv2;
};

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    MX_LPUART1_UART_Init();

    SysTick->CTRL &= ~(SysTick_CTRL_ENABLE_Msk | SysTick_CTRL_TICKINT_Msk);

    ExampleServer server;

    uint8_t receiveBuffer{0};

    while (true)
    {
        HAL_UART_Receive_IT(&hlpuart1, &receiveBuffer, 1);
        __WFI();

        server.lrpcReceive(receiveBuffer);
    }
}