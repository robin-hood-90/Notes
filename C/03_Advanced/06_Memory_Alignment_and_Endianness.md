---
tags: [c, advanced, alignment, padding, endianness, packed-structs, type-punning, byte-order]
aliases: ["Memory Alignment", "Padding", "Endianness", "Struct Packing", "Unaligned Access", "Network Byte Order"]
status: stable
updated: 2026-05-09
---

# Memory Alignment, Padding, and Endianness

> [!summary] Goal
> Understand memory alignment (what it is, why it matters), struct padding and reordering, endianness detection and conversion, and packed structs for networking/device drivers. Essential for portable code, networking protocols, and low-level system programming.

## Table of Contents

1. [Alignment Requirements](#alignment-requirements)
2. [Struct Padding and Layout](#struct-padding-and-layout)
3. [Controlling Alignment](#controlling-alignment)
4. [Endianness](#endianness)
5. [Unaligned Access](#unaligned-access)
6. [Pitfalls](#pitfalls)

---

## Alignment Requirements

### Memory layout visualization

```mermaid
flowchart LR
    subgraph MEM["Memory (4-byte aligned grid)"]
        A0["0x00: char a"]
        A1["0x01: [padding]"]
        A2["0x02: [padding]"]
        A3["0x03: [padding]"]
        A4["0x04: int b — correctly aligned<br/>(offset divisible by 4)"]
        A5["0x05: int b continues"]
        A6["0x06: int b continues"]
        A7["0x07: int b continues"]
        A8["0x08: char c"]
        A9["0x09: [trailing padding]"]
        A10["0x0A: [trailing padding]"]
        A11["0x0B: [trailing padding]"]
    end
    note for MEM "struct S { char a; int b; char c; } — 12 bytes (6 data + 6 padding)"
```

> [!info] Alignment
> A variable's **alignment requirement** is the address multiple at which it must be stored. An `int` (4 bytes) must be at an address divisible by 4. A `double` (8 bytes) at an address divisible by 8. The compiler inserts **padding** to satisfy alignment. Accessing a variable at an unaligned address may crash (ARM, MIPS, SPARC) or be slow (x86).

| Type | Size (bytes) | Alignment (bytes) | Valid offsets |
|------|:------------:|:-----------------:|:------------:|
| `char` | 1 | 1 | Any |
| `short` | 2 | 2 | Even |
| `int` | 4 | 4 | Multiple of 4 |
| `float` | 4 | 4 | Multiple of 4 |
| `long` (64-bit) | 8 | 8 | Multiple of 8 |
| `double` | 8 | 8 | Multiple of 8 |
| `void*` | 8 | 8 | Multiple of 8 |
| `long double` | 10-16 | 16 | Multiple of 16 (x86-64) |

### Checking alignment

```c
#include <stdalign.h>     // C11: alignof, alignas

printf("alignof(int)    = %zu\n", alignof(int));        // 4
printf("alignof(double) = %zu\n", alignof(double));      // 8
printf("alignof(void*)  = %zu\n", alignof(void*));       // 8

// Or with GCC:
printf("__alignof__(int)    = %zu\n", __alignof__(int));

// The address must be a multiple of the alignment:
// int at 0x1000 → OK (0x1000 % 4 == 0)
// int at 0x1001 → UNALIGNED (crash or slow)
```

---

## Struct Padding and Layout

> [!info] Padding
> The compiler inserts unused bytes between struct members to meet each member's alignment requirement. The total struct size is always a multiple of the **largest member's alignment**. This can waste significant space.

```c
#include <stdio.h>
#include <stddef.h>      // offsetof

// Layout analysis
typedef struct {
    char a;       // offset 0, size 1
                  // 3 bytes padding (to align int to 4)
    int b;        // offset 4, size 4
    char c;       // offset 8, size 1
                  // 3 bytes padding (to make total size multiple of 4)
} Bad;            // total: 12 bytes (but only 6 bytes of data!)

// Showing padding with offsetof
printf("offset of a: %zu\n", offsetof(Bad, a));   // 0
printf("offset of b: %zu\n", offsetof(Bad, b));   // 4 (3 bytes padding)
printf("offset of c: %zu\n", offsetof(Bad, c));   // 8
printf("sizeof(Bad): %zu\n", sizeof(Bad));         // 12
```

### Struct reordering to minimize padding

```c
// ❌ BAD — large alignment first causes more padding
typedef struct {
    char  a;      // 1 (+ 7 padding)
    double b;     // 8
    char  c;      // 1 (+ 7 padding)
} BadOrdered;     // 24 bytes (only 10 used)

// ✅ GOOD — largest fields first
typedef struct {
    double b;     // 8
    char   a;     // 1
    char   c;     // 1
                   // 6 bytes padding (trailing — to align next struct in array)
} GoodOrdered;    // 16 bytes (only 10 used, 6 padding)

// ✅ BEST — group same-size fields together
typedef struct {
    double b;     // 8
    int    d;     // 4
    char   a;     // 1
    char   c;     // 1
    char   e;     // 1
                   // 1 byte padding
} BestOrdered;    // 16 bytes (only 15 used)

printf("Bad:  %zu bytes\n", sizeof(BadOrdered));    // 24
printf("Good: %zu bytes\n", sizeof(GoodOrdered));   // 16
printf("Best: %zu bytes\n", sizeof(BestOrdered));   // 16
```

### Rule: order members by decreasing alignment

```c
// 1. Pointers and doubles (8 bytes)
// 2. Long, int, float (4 bytes)
// 3. Short (2 bytes)
// 4. Char, bool (1 byte)
```

---

## Controlling Alignment

### C11: _Alignas and _Alignof

```c
#include <stdalign.h>

// Specify alignment for a variable
alignas(64) int cache_aligned_array[1024];    // 64-byte aligned for cache lines
_Alignas(4096) char page_buffer[4096];         // Page-aligned for mmap/DMA

// Get alignment of a type
size_t al = alignof(max_align_t);              // Largest fundamental alignment

// Heap allocation with alignment
void *ptr = aligned_alloc(64, 1024 * sizeof(int));  // C11, 64-byte aligned
free(ptr);
```

### GCC/Clang attributes

```c
// __attribute__((aligned(N)))
int cache_aligned_var __attribute__((aligned(64)));

// __attribute__((packed)) — NO padding between members
typedef struct __attribute__((packed)) {
    uint8_t  version;         // 1 byte
    uint16_t length;          // 2 bytes (at offset 1 — UNALIGNED!)
    uint32_t timestamp;       // 4 bytes (at offset 3 — UNALIGNED!)
} Packet;                     // Total: 7 bytes (no padding)

// __attribute__((aligned)) — minimum alignment for a struct
typedef struct __attribute__((aligned(8))) {
    int a;
    char b;
} AlignedStruct;              // Total: 8 bytes (padded to multiple of 8)

// Check layout
printf("Packet length at offset: %zu\n", offsetof(Packet, length));    // 1
printf("Packet timestamp at offset: %zu\n", offsetof(Packet, timestamp)); // 3
printf("sizeof(Packet): %zu\n", sizeof(Packet));                        // 7
```

---

## Endianness

> [!info] Endianness
> Endianness defines the byte order of multi-byte values in memory. **Little-endian** (x86, x86-64): least significant byte first. **Big-endian** (network protocols, some embedded): most significant byte first. Network byte order is always big-endian.

```c
// Endianness visualized
uint32_t value = 0x12345678;

// Little-endian (x86):
// Address:  0x100  0x101  0x102  0x103
// Value:    [0x78] [0x56] [0x34] [0x12]
// (LSB first)

// Big-endian:
// Address:  0x100  0x101  0x102  0x103
// Value:    [0x12] [0x34] [0x56] [0x78]
// (MSB first)
```

### Detecting endianness at compile time

```c
// Method 1: predefined macros
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    #define IS_LITTLE_ENDIAN 1
#elif __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    #define IS_LITTLE_ENDIAN 0
#endif
```

### Detecting endianness at runtime

```c
// Method 2: runtime detection
int is_little_endian(void) {
    uint16_t test = 0x0001;
    uint8_t *bytes = (uint8_t *)&test;
    return bytes[0] == 0x01;    // LSB first = little endian
}
```

### Byte swapping

```c
#include <byteswap.h>     // Linux
#include <endian.h>       // Linux: le16toh, be16toh

// Manual byte swap
uint16_t swap16(uint16_t v) {
    return (v << 8) | (v >> 8);
}

uint32_t swap32(uint32_t v) {
    return ((v & 0xFF000000) >> 24) |
           ((v & 0x00FF0000) >> 8)  |
           ((v & 0x0000FF00) << 8)  |
           ((v & 0x000000FF) << 24);
}

// Using compiler builtins (faster — may use single instruction)
uint16_t swapped = __builtin_bswap16(value);
uint32_t swapped = __builtin_bswap32(value);
uint64_t swapped = __builtin_bswap64(value);

// Network to host byte order conversion
htons(8080);          // Host TO Network Short
htonl(0x1234);        // Host TO Network Long
ntohs(port);          // Network TO Host Short
ntohl(addr);          // Network TO Host Long
```

---

## Unaligned Access

> [!info] Unaligned access
> When a multi-byte value is read from or written to an address that doesn't satisfy its alignment requirement. On x86, this is slow but works. On ARM/MIPS, this causes a **bus error** (SIGBUS). Packed structs often cause unaligned access. Always use `memcpy` for portable unaligned access.

```c
// SAFE unaligned access — using memcpy
uint32_t read_unaligned32(const void *addr) {
    uint32_t result;
    memcpy(&result, addr, sizeof(result));    // memcpy handles alignment
    return result;
}

void write_unaligned32(void *addr, uint32_t value) {
    memcpy(addr, &value, sizeof(value));
}

// Usage with packed struct
Packet *pkt = receive_packet();              // Packet has unaligned fields
uint32_t ts = read_unaligned32(&pkt->timestamp);  // Safe on any CPU

// ARM: the same with direct access would crash:
// uint32_t ts = pkt->timestamp;  // ❌ SIGBUS on ARM!
```

### When alignment matters

| Platform | Unaligned access behavior |
|----------|---------------------------|
| **x86/x86-64** | ✅ Works, but 2-3× slower (extra memory bus cycles) |
| **ARM (older)** | ❌ Bus error (SIGBUS) — must use memcpy |
| **ARM (modern)** | ⚠️ Works for some types, but not guaranteed |
| **MIPS** | ❌ Bus error |
| **RISC-V** | ⚠️ Configurable (usually traps) |

---

## Pitfalls

### Assuming struct layout is sequential

Don't assume `struct S { char a; int b; }` has `b` at offset 1. The compiler aligns `b` to offset 4. Use `offsetof()` for portable access or reorder fields.

### Packed struct + pointer return

```c
// ❌ Returning pointer to packed struct member is unsafe
uint32_t *get_timestamp(Packet *pkt) {
    return &pkt->timestamp;     // Address is unaligned!
}

// ✅ Return copy
uint32_t get_timestamp_safe(Packet *pkt) {
    uint32_t ts;
    memcpy(&ts, &pkt->timestamp, sizeof(ts));
    return ts;
}
```

### Byte order on multi-byte protocols

Every multi-byte field in a network packet or file format must be explicitly byte-swapped. `ntohs()`/`ntohl()` for network protocols. Custom reading functions for file formats.

### Sizeof on packed structs

```c
// On x86, sizeof(Packet) = 7 with packed, 12 without
// On ARM, 7 with packed
// Size is always the same with packed, regardless of platform
```

---

> [!question]- Interview Questions
>
> **Q: What is struct padding and how does it affect memory usage?**
> A: The compiler inserts padding between struct members to satisfy each member's alignment requirement. `char a` (align 1) followed by `int b` (align 4) has 3 bytes of padding before `b`. The total size is always a multiple of the largest alignment. This can waste significant space — reordering members from largest to smallest alignment minimizes padding.
>
> **Q: What is the difference between little-endian and big-endian?**
> A: Little-endian stores the least significant byte first (at the lowest address). Big-endian stores the most significant byte first. x86/x86-64 is little-endian. Network protocols (IP, TCP) use big-endian ("network byte order"). When reading/writing multi-byte values from network packets or binary files, always convert byte order using `htons`/`ntohs`.
>
> **Q: What is a packed struct and when is it used?**
> A: A packed struct (`__attribute__((packed))`) tells the compiler to omit all padding bytes between members. Used for: (1) network protocol headers that must match wire format exactly, (2) file system structures that must match on-disk format, (3) device register maps, (4) saving memory in arrays of many structs. Disadvantage: unaligned access is slow on x86 and crashes on ARM.
>
> **Q: How do you safely read an unaligned field from a packed struct?**
> A: Use `memcpy(&dest, &packed->field, sizeof(dest))`. `memcpy` handles any alignment correctly. On x86, the compiler often optimizes `memcpy` of small values into a single load instruction. Never return a pointer to an unaligned field, as that pointer is unaligned and may crash when dereferenced.
>
> **Q: What is `alignof` and when would you use `aligned_alloc`?**
> A: `alignof(type)` returns the alignment requirement of a type. `aligned_alloc(alignment, size)` allocates heap memory with a specific alignment. Use when: (1) allocating memory for SIMD operations (requires 16 or 32-byte alignment), (2) caching sensitive data (aligning to cache line boundaries, typically 64 bytes, to avoid false sharing), (3) DMA buffers that require page alignment.

---

## Cross-Links

- [[C/01_Foundations/05_Structs_Unions_and_Bit_Fields]] for struct layout and unions
- [[C/01_Foundations/03_Dynamic_Memory]] for aligned_alloc
- [[C/03_Advanced/04_Socket_Programming]] for network byte order
- [[C/03_Advanced/08_Performance_Profiling_and_Optimization]] for cache alignment
- [[C/02_Core/06_Undefined_Behavior_and_Memory_Safety]] for strict aliasing
