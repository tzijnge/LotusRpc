---
title: Binary
toc: true
---

As an engineer in the low level embedded domain, you are probably very curious what LotusRPC produces as binary data to transport a function call (or its response) from one device to another. Here is some info about that.

## Frame format

All data is encoded in little endian byte order. The smallest unit of data is 1 byte (8 bits). Packets have a minimum size of 3 bytes and a maximum size of 255 bytes. The actual packet size depends on the type of function that is encoded

Here's a top level overview of a LotusRPC data frame. The payload field is not actually 8 bits, but a placeholder for the packet payload (the parameters or return values of the function). The frame format for a function call from client to server is exactly the same as the frame format for getting the return value(s) back from server to client.

``` mermaid
---
title: "LotusRPC data frame"
config:
  packet:
    bitsPerRow: 16
---
packet
+8: "Packet size"
+8: "Service ID"
+8: "Function / Stream ID"
+8: "Payload"
```

| Field name              | Size (bytes) | Comment |
| ----------              | ------------ | ------- |
| Packet size             | 1            | Total packet size (including this field) |
| Service ID              | 1            | ID of the current service |
| Function ID / Stream ID | 1            | ID of the current function or stream |
| Payload                 | 0-252        | Any number of parameters or return values |

## Function payload encoding

The following sections detail the encoding of all types supported by LotusRPC.

### No parameters or no return values

For a function with no parameters, the payload of the message from client to server has size 0. Likewise, a function with no return values has a payload of 0 bytes for the message from client to server.

### (u)int**x**_t

For all integral types (u)int**x**_t, the size of the field is **x**/4 bytes

### Float

Float is encoded as 4 bytes

### Double

Double is encoded as 8 bytes

### Bool

Booleans are encoded as 1 byte, with the value 0 demarking `False` and the value 1 demarking `True`.

### String

LotusRPC distinguishes two types of strings. Fixed size string and auto string. A fixed size string always occupies the same amount of bytes in a packet. An auto string occupies only the required amount.
Strings are always null terminated, regardless of the type.
The string 'lrpc' is encoded as follows

``` mermaid
---
title: "Auto string"
config:
  packet:
    bitsPerRow: 16
---
packet
+8: "'l' (0x6C)"
+8: "'r' (0x72)"
+8: "'p' (0x70)"
+8: "'c' (0x63)"
+8: "null (0x00)"
```

``` mermaid
---
title: "Fixed size (7) string"
config:
  packet:
    bitsPerRow: 16
---
packet
+8: "'l' (0x6C)"
+8: "'r' (0x72)"
+8: "'p' (0x70)"
+8: "'c' (0x63)"
+8: "null (0x00)"
+8: "null (0x00)"
+8: "null (0x00)"
+8: "null (0x00)"
```

### Array

In LotusRPC, an array always has a fixed capacity as specified in the interface definition file. The number of used elements in the array is however determined at runtime so can be less than the capacity. In addition to space for all elements, the encoded array has a single byte size field at the start. The array [12, 13, 14, 15] with capacity of 6 and is encoded as follows

``` mermaid
---
title: "Array of capacity 6 with 4 elements"
config:
  packet:
    bitsPerRow: 16
---
packet
+8: "Size (0x04)"
+8: "El 0 (0x0C)"
+8: "El 1 (0x0D)"
+8: "El 2 (0x0E)"
+8: "El 3 (0x0F)"
+8: "Padding (0x00)"
+8: "Padding (0x00)"
```

### Optional

In LotusRPC, an optional can hold a value of any other type. The contained value may be there or it may not be there. As such, an optional value is encoded as a boolean that indicates if there is a contained value and either nothing else or the encoded contained value. The encoded optional value therefore has a size of 1 byte (no contained value) or [sizeof(contained) + 1] bytes. Here's an example of an optional uint8_t with and without contained value.

``` mermaid
---
title: "Optional uint8_t. No contained value"
config:
  packet:
    bitsPerRow: 16
---
packet
+8: "State (0x00)"
```

``` mermaid
---
title: "Optional uint8_t. Contained value is 0x88"
config:
  packet:
    bitsPerRow: 16
---
packet
+8: "State (0x01)"
+8: "State (0x88)"
```

### Enum

An enum value is simply encoded as uint8_t.

### Struct

LotusRPC allows defining a custom composition of types called a struct. A struct is simply encoded by concatenating the encoded fields. Here's an example of a simple struct.

``` yaml
...
structs:
  - name: CompositeData
    fields:
      - { name: a, type: uint8_t}
      - { name: b, type: string }
      - { name: c, type: uint16_t }
...
```

``` mermaid
---
title: "Struct 'CompositeData' = {0x12, '34', 0x5678}"
config:
  packet:
    bitsPerRow: 16
---
packet
+8: "a (0x12)"
+8: "b0 (0x33)"
+8: "b1 (0x34)"
+8: "b2 (0x00)"
+8: "c0 (0x78)"
+8: "c1 (0x56)"
```
