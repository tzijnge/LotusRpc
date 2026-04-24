---
title: Examples
toc: true
toc_icon: flask
---

## Math service (end-to-end walkthrough)

This example builds a complete math service: a C++ server that adds and multiplies integers, and a Python client that calls it. It shows every step from definition to a working call.

### 1. Write the definition

Save the following as `math.lrpc.yaml`:

``` yaml
name: math
settings:
  namespace: ex
  rx_buffer_size: 32
  tx_buffer_size: 32
services:
  - name: calc
    functions:
      - name: add
        params:
          - { name: a, type: int32_t }
          - { name: b, type: int32_t }
        returns:
          - { name: result, type: int32_t }
      - name: multiply
        params:
          - { name: a, type: int32_t }
          - { name: b, type: int32_t }
        returns:
          - { name: result, type: int32_t }
```

### 2. Generate C++ code

``` bash
lrpcg cpp -d math.lrpc.yaml -o generated/
```

This creates `generated/math/` with the following files:

| File            | Purpose                                    |
|-----------------|--------------------------------------------|
| `math.hpp`      | Top-level include                          |
| `calc_shim.hpp` | Abstract base class for the `calc` service |

### 3. Implement the server

#### CalcService.hpp

``` cpp
#include "math/math.hpp"

class CalcService : public ex::calc_shim {
protected:
    int32_t add(int32_t a, int32_t b) override {
        return a + b;
    }

    int32_t multiply(int32_t a, int32_t b) override {
        return a * b;
    }
};
```

**main.cpp** — subclass the server to provide the transport, then register services and feed incoming bytes:

``` cpp
#include "math/math.hpp"
#include "CalcService.hpp"

// Replace the UART calls with whatever your platform uses.
extern "C" void uart_write(const uint8_t* data, size_t len);
extern "C" bool uart_read_byte(uint8_t* out);

class MathServer : public ex::math {
    void lrpcTransmit(lrpc::span<const uint8_t> bytes) override {
        uart_write(bytes.data(), bytes.size());
    }
};

CalcService calc;
MathServer server;

int main() {
    server.registerService(calc);

    while (true) {
        uint8_t byte;
        if (uart_read_byte(&byte)) {
            server.lrpcReceive(byte);
        }
    }
}
```

### 4. Call from the command line

Create `lrpcc.config.yaml` next to your project:

``` yaml
definition_url: 'math.lrpc.yaml'
transport_type: serial
transport_params:
  port: COM3       # adjust to your port
  baudrate: 115200
  timeout: 2
```

Then call functions directly:

``` bash
lrpcc calc add 3 7       # result = 10
lrpcc calc multiply 6 7  # result = 42
```

### 5. Call from Python

``` python
from lrpc.client import LrpcClient
from lrpc.utils import load_lrpc_def
import serial

lrpc_def = load_lrpc_def("math.lrpc.yaml")
port = serial.Serial(port="COM3", baudrate=115200, timeout=2)
client = LrpcClient(lrpc_def, port)

for resp in client.communicate("calc", "add", a=3, b=7):
    print(resp["result"])   # 10

for resp in client.communicate("calc", "multiply", a=6, b=7):
    print(resp["result"])   # 42
```

---

## STM32 Nucleo L496

A complete embedded example running on the STM32 Nucleo L496 board is available [in the repository](https://github.com/tzijnge/LotusRpc/tree/main/examples/stm32_nucleo_l496). It demonstrates:

- An LRPC definition file
- CMake integration for code generation
- Using the generated code in a bare-metal C++ project with HAL
