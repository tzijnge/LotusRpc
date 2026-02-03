#include "main.h"
#include "usart.h"
#include "lrpc/generated/example.hpp"
#include <etl/array.h>
#include <etl/algorithm.h>
#include <algorithm>
#include <random>

extern "C" void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    (void)huart;
}

class Srv1 : public srv1_shim
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

    etl::span<const uint8_t> f10() override
    {
        return {};
    }

    void f11(etl::span<const uint8_t>) override
    {
    }

    void f12(etl::optional<uint8_t>) override
    {
    }

    uint32_t f13(etl::string_view p1) override
    {
        return p1.size();
    }

    etl::string_view f14(etl::string_view p1) override
    {
        return p1;
    }

    lrpc::bytearray_t f15(lrpc::bytearray_t p1) override
    {
        return p1;
    }
};

class Srv2 : public srv2_shim
{
public:
    int32_t f1(int32_t p1) override
    {
        return p1;
    }

    void s0() override
    {
        s0_response(0, 0, false);
        s0_response(1, 10, false);
        s0_response(2, 20, s0StopCalled);
        if (!s0StopCalled)
        {
            s0_response(3, 30, true);
        }
    }

    void s0_stop() override
    {
        s0StopCalled = true;
    }

    void s1() override
    {
        if (s1StopCalled)
        {
            s1_response("stop called", -9912);
        }
        s1_response("123", -10);
        s1_response("456", -20);
        s1_response("789", -30);
    }

    void s1_stop() override
    {
        s1StopCalled = true;
    }

    void s2(uint16_t, etl::string_view, bool) override
    {
    }

    void s3(etl::string_view, int16_t) override
    {
    }

    void s4() override
    {
        s4StopCalled = false;
        std::random_device rd;
        std::mt19937 g(rd());
        std::shuffle(data.begin(), data.end(), g);
        s4_remaining = data;

        while (!s4StopCalled)
        {
            const auto sub_size = etl::min<size_t>(s4_remaining.size(), 2);
            const auto sub = s4_remaining.subspan(0, sub_size);
            const auto final = sub_size != 2;
            s4_response(sub, final);
            if (!final)
            {
                s4_remaining = s4_remaining.last(s4_remaining.size() - sub_size);
            }
            else
            {
                return;
            }
        }
    }

    void s4_stop() override
    {
        s4StopCalled = true;
    }

private:
    bool s0StopCalled{false};
    bool s1StopCalled{false};
    bool s4StopCalled{false};

    etl::array<uint8_t, 7> data{0x00U, 0x01U, 0x02U, 0x03U, 0x04U, 0x05U, 0x06U};
    lrpc::bytearray_t s4_remaining{data};
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