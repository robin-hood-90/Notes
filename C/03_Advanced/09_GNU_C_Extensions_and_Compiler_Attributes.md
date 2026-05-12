---
tags: [c, advanced, gnu-extensions, attribute, typeof, alloca, vla, pragma, builtins]
aliases: ["GNU C Extensions", "__attribute__", "GCC Attributes", "typeof", "alloca", "VLA", "Compiler Extensions"]
status: stable
updated: 2026-05-11
---

# GNU C Extensions and Compiler Attributes

> [!summary] Goal
> Master GCC/Clang extensions used in real-world C: the `__attribute__` system for controlling code generation, `typeof` for type deduction, `alloca` for stack allocation, variable-length arrays (VLAs), and `#pragma` directives. Essential for kernel development, high-performance code, and working with production C codebases.

## Table of Contents

1. [Why GNU Extensions Matter](#why-gnu-extensions-matter)
2. [__attribute__ Comprehensive Table](#attribute-comprehensive-table)
3. [Function Attributes](#function-attributes)
4. [Variable Attributes](#variable-attributes)
5. [Type Attributes](#type-attributes)
6. [typeof and __auto_type](#typeof-and-autotype)
7. [alloca and VLAs](#alloca-and-vlas)
8. [__builtin Functions](#builtin-functions)
9. [#pragma Directives](#pragma-directives)
10. [Pitfalls](#pitfalls)

---

## Why GNU Extensions Matter

GCC and Clang (which aim for GCC compatibility) provide a rich set of extensions that go beyond standard C. These extensions are used pervasively in:
- The Linux kernel (`__attribute__((section))`, `__attribute__((packed))`)
- glibc and system libraries (`__attribute__((format))`, `__attribute__((weak))`)
- Embedded systems (packed structs, interrupt attributes)
- Performance-critical code (cold/hot, always_inline, builtins)

> [!info] Portability boundary
> GNU extensions are NOT portable to other compilers (MSVC, ICC, specific embedded compilers). However, GCC and Clang share most extensions. MSVC has its own equivalents (`__declspec`, `__forceinline`). Use `#ifdef __GNUC__` to guard non-portable code.

---

## `__attribute__` Comprehensive Table

```c
// Syntax:
__attribute__((attribute_name, attribute_name, ...))

// Placed after declarations:
int func(void) __attribute__((noreturn));
int aligned_var __attribute__((aligned(64)));
typedef struct { ... } __attribute__((packed)) PackedType;

// GCC 2.7+ syntax, also accepts __attribute__((__attribute_name__)) to avoid
// macro conflicts with user-defined `attribute_name`.
```

| Attribute | Applies to | Purpose |
|:---------:|:----------:|---------|
| `packed` | struct/union | Minimize padding — fields aligned to 1 byte |
| `aligned(N)` | var/type/field | Set minimum alignment to N bytes |
| `section("name")` | func/var | Place object in named ELF section |
| `constructor` | func | Run automatically before `main()` |
| `destructor` | func | Run automatically after `exit()` |
| `weak` | func/var | Weak symbol — can be overridden by a strong definition |
| `alias("target")` | func/var | Create an alias for another symbol |
| `visibility("default"|"hidden")` | func/var | Control ELF symbol visibility |
| `format(printf, fmt_idx, arg_idx)` | func | Enable printf-style argument checking |
| `noreturn` | func | Function does not return |
| `always_inline` | func | Force inlining (override compiler heuristics) |
| `cold` | func | Mark function as cold (rarely executed) |
| `hot` | func | Mark function as hot (frequently executed) |
| `unused` | var/func | Suppress "unused" warning |
| `used` | var/func | Keep symbol even if not referenced |
| `warn_unused_result` | func | Warn if return value is ignored |
| `cleanup(cleanup_fn)` | var | Run function when variable goes out of scope |
| `nonnull(arg_idx, ...)` | func | Arguments must not be NULL |
| `pure` | func | Result depends only on args (no side effects) |
| `const` | func | Result depends only on args (no side effects, no pointer deref) |
| `malloc` | func | Return value is a freshly allocated pointer |
| `deprecated("msg")` | func/var | Mark code as deprecated |
| `noinline` | func | Prevent inlining |
| `target("arch")` | func | Compile for specific architecture |
| `target_clones("arch1","arch2")` | func | Create multiple versions for runtime dispatch |

---

## Function Attributes

### `constructor` / `destructor`

```c
#include <stdio.h>

// Run before main() — like a C++ static initializer.
// Priority argument (101) controls order among constructors:
// lower numbers run first. 101+ reserved for user code.
__attribute__((constructor(101)))
void init_early(void) {
    printf("Early init (before main)\n");
}

__attribute__((constructor(200)))
void init_late(void) {
    printf("Late init (still before main)\n");
}

// Run after exit() — like a C++ static destructor.
__attribute__((destructor))
void cleanup(void) {
    printf("Cleanup after main\n");
}

int main(void) {
    printf("Main\n");
    return 0;
}
// Output:
//   Early init (before main)
//   Late init (still before main)
//   Main
//   Cleanup after main
```

### `weak` and `alias`

```c
#include <stdio.h>

// Weak symbol: a definition that can be overridden.
// If no strong definition exists, the weak one is used.
// Used extensively in libraries for default implementations.

__attribute__((weak))
const char *get_platform_name(void) {
    return "generic";
}

// Strong definition overrides the weak one
const char *get_platform_name(void) {
    return "x86-64";
}

// Alias: another name for the same function
void original_func(void) {
    printf("Original\n");
}

void new_func(void) __attribute__((alias("original_func")));
// new_func() calls original_func() directly.
```

### `section` — placing objects in custom ELF sections

```c
// Place a function in a specific ELF section (used by kernel initcall system).
__attribute__((section(".my_init")))
void my_init_function(void) {
    // This function is placed in .my_init section, not .text
}

// The linker script or startup code can locate and call all functions
// in .my_init without knowing their names at compile time.
// This is how the Linux kernel's initcall system works:
//   #define __initcall(fn) __attribute__((section(".initcall"))) typeof(fn) *__initcall_##fn = fn
```

### `cleanup` — scope-based resource management

```c
#include <stdio.h>
#include <stdlib.h>

// cleanup attribute: call a function when the variable goes out of scope.
// Similar to C++ destructors, but per-variable.

static inline void free_cleanup(void *p) {
    free(*(void **)p);
}

// Usage:
void example(void) {
    __attribute__((cleanup(free_cleanup))) int *data = malloc(100 * sizeof(int));
    // ... use data ...
    // No explicit free needed — free_cleanup is called when data goes out of scope
}

// Macro wrapper for cleaner syntax:
#define autofree __attribute__((cleanup(free_cleanup)))

void example_macro(void) {
    autofree int *data = malloc(100 * sizeof(int));
    // auto-freed when leaving scope
}

// ⚠️  cleanup is NOT standard — guarded with #ifdef __GNUC__
```

### `format` — compile-time printf-style checking

```c
#include <stdio.h>

// __attribute__((format(printf, format_arg_index, first_vararg_index)))
// Tells the compiler to check format strings like it does for printf.

void log_error(const char *file, int line,
               const char *fmt, ...)
    __attribute__((format(printf, 3, 4)));  // fmt is arg 3, ... starts at arg 4

void log_error(const char *file, int line,
               const char *fmt, ...) {
    fprintf(stderr, "[%s:%d] ", file, line);
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
}

// Now the compiler checks:
log_error(__FILE__, __LINE__, "count = %d", 42);     // OK
log_error(__FILE__, __LINE__, "count = %d", "not int");  // WARNING: format mismatch
```

### `target_clones` — CPU-specific function versions

```c
// Create multiple compiled versions of a function for different CPU features.
// The runtime selects the best version for the current CPU.

__attribute__((target_clones("default", "avx2", "sse4.2")))
double compute_sum(const double *data, size_t n) {
    // Compiler generates 3 versions (default, AVX2, SSE4.2)
    // On startup, the dynamic linker selects the best one.
    double sum = 0.0;
    for (size_t i = 0; i < n; i++) sum += data[i];
    return sum;
}
```

---

## Variable Attributes

```c
// aligned — minimum alignment
__attribute__((aligned(64))) int cache_line_aligned;
// Ensures int is at a 64-byte boundary

// section — specific ELF section
__attribute__((section(".my_data"))) int placed_in_section;
// Visualized via: readelf -a a.out | grep my_data

// unused — suppress "unused variable" warnings
__attribute__((unused)) int may_be_unused;
```

---

## Type Attributes

```c
// packed — no padding between fields
struct __attribute__((packed)) DeviceRegister {
    uint8_t  status;    // offset 0
    uint16_t data;      // offset 1 (not 2, as aligned)
    uint32_t config;    // offset 3 (not 4)
    // Total: 7 bytes (vs 8 with padding)
};

// aligned — minimum alignment for a type
struct __attribute__((aligned(4096))) Page {
    char data[4096];
};
```

---

## `typeof` and `__auto_type`

### `typeof` (GNU, C23)

```c
// typeof — determine type at compile time
typeof(1 + 2) x = 42;  // x is int

// Real-world: MIN/MAX macros without double-evaluation
#define MAX(a, b) ({                   \
    typeof(a) _a = (a);                \
    typeof(b) _b = (b);                \
    _a > _b ? _a : _b;                 \
})

// C23 standardizes typeof and adds typeof_unqual (strips qualifiers)
typeof_unqual(const int) y = 42;  // y is int (const removed)
```

### `__auto_type` (GNU)

```c
// __auto_type — type from initializer (like C++ auto)
#define SWAP(a, b) do {               \
    __auto_type _tmp = (a);           \
    (a) = (b);                        \
    (b) = _tmp;                       \
} while (0)

// typeof is preferred over __auto_type:
//   - typeof is C23 standard
//   - typeof works in more contexts (struct members, cast targets)
```

---

## `alloca` and VLAs

### `alloca` — stack allocation

```c
#include <alloca.h>   // or <stdlib.h> on some systems

// alloca allocates memory on the stack, not the heap.
// The memory is automatically freed when the calling function returns.
// NO free() needed — allocation and deallocation are O(1).

void process(size_t n) {
    // Allocate n ints on the stack
    int *temp = alloca(n * sizeof(int));

    for (size_t i = 0; i < n; i++) {
        temp[i] = (int)i;  // Use like a regular array
    }
    // No free needed — stack is cleaned up on return
}

// When to use alloca:
//   - Need a small temporary buffer in a performance-critical path
//   - Want to avoid malloc overhead (alloca is a single stack pointer adjust)
//   - The function is not recursive (stack keeps growing!)

// When NOT to use alloca:
//   - Large allocations (stack overflow risk)
//   - The allocation size depends on untrusted input
//   - Deep recursion
//   - In a loop (stack grows unboundedly — no free until function returns!)
```

### VLAs — Variable-Length Arrays (C99, optional in C11)

```c
// VLAs are stack-allocated arrays with runtime-determined size.
// Available in C99. Optional in C11 (C11 §6.7.6.2). Not supported in MSVC.
// Removed from C23 (making VLAs optional was a mistake, C23 makes them
// a mandatory conditional feature again).

void process_vla(size_t n) {
    int vla[n];         // Allocated on the stack
    for (size_t i = 0; i < n; i++) {
        vla[i] = (int)i;
    }
}

// VLAs with two dimensions:
void matrix_op(size_t rows, size_t cols, int matrix[rows][cols]) {
    for (size_t r = 0; r < rows; r++) {
        for (size_t c = 0; c < cols; c++) {
            matrix[r][c] *= 2;
        }
    }
}
```

### VLA pitfalls vs alloca

```c
void example(void) {
    size_t n = 100000;   // Arbitrary large value from input
    // int vla[n];       // May overflow the stack silently
    // int *p = alloca(n * sizeof(int));  // Same risk

    // Neither VLAs nor alloca provide failure indication on stack overflow.
    // If the allocation exceeds available stack space: crash (SIGSEGV).
    // Use malloc() for large or untrusted-size allocations.
}
```

---

## `__builtin` Functions

### Branch prediction hints

```c
// __builtin_expect: tell the compiler which branch is more likely
// Used pervasively in the Linux kernel.

#define likely(x)    __builtin_expect(!!(x), 1)
#define unlikely(x)  __builtin_expect(!!(x), 0)

void handle_error(void);

void process(int value) {
    // Default: compiler assumes error path is uncommon
    if (unlikely(value < 0)) {
        handle_error();
        return;
    }
    // Normal processing — compiler can optimize for the common path
}

// C23 standardizes [[likely]] and [[unlikely]] attributes:
// void process(int value) {
//     if (value < 0) [[unlikely]] { ... }
// }
```

### Unreachable code marker

```c
// __builtin_unreachable — tells the compiler a code path is never reached.
// Suppresses warnings and enables dead-code elimination.

int div_checked(int a, int b) {
    switch (b) {
        case 0:  return 0;       // handle zero
        case 1:  return a;       // identity
        default: return a / b;
    }
    __builtin_unreachable();     // All cases covered above
}

// Without __builtin_unreachable, the compiler may warn
// "control reaches end of non-void function" even when all paths are covered.
```

### Overflow checking builtins

```c
// GCC has builtins for checked arithmetic (similar to C23 stdckdint.h):

int add_safe(int a, int b, int *result) {
    return __builtin_add_overflow(a, b, result);
    // Returns non-zero if overflow occurred
}

int sub_safe(int a, int b, int *result) {
    return __builtin_sub_overflow(a, b, result);
}

int mul_safe(int a, int b, int *result) {
    return __builtin_mul_overflow(a, b, result);
}
```

### Other useful builtins

```c
// Type checking
__builtin_types_compatible_p(int, long)     // 0 or 1 (compile-time constant)
__builtin_constant_p(42)                    // 1 if argument is compile-time constant

// Object size (for bounds checking in __builtin___memcpy_chk, etc.)
__builtin_object_size(ptr, 0)               // Remaining size of object

// CPU feature detection
__builtin_cpu_supports("avx2")              // Runtime CPU feature check

// Trap
__builtin_trap()                            // Emit a trap instruction (abort)
```

---

## `#pragma` Directives

```c
// #pragma once — include guard equivalent (non-standard but widely supported)
#pragma once
// The compiler tracks the file and skips it on subsequent includes.
// Faster than #ifndef guards, but not guaranteed to work universally.

// #pragma pack — control struct packing (alternative to __attribute__((packed)))
#pragma pack(push, 1)       // Save current alignment, set to 1 byte
struct Packed {
    uint8_t  c;
    uint32_t i;
};
#pragma pack(pop)           // Restore previous alignment

// #pragma GCC diagnostic — control compiler warnings
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
    int unused_variable;
#pragma GCC diagnostic pop

// #pragma GCC poison — prevent use of identifiers
#pragma GCC poison malloc sprintf
// Any use of malloc or sprintf after this line triggers a compile error.

// #pragma message — print a message during compilation
#pragma message "Compiling for debug configuration"
```

---

## Pitfalls

### `alloca` inside a loop

`alloca` is freed when the FUNCTION returns, not when the loop iteration ends. Calling `alloca` in a loop grows the stack until the function returns, leading to stack overflow.

```c
void bad_loop(size_t n) {
    for (size_t i = 0; i < n; i++) {
        int *buf = alloca(4096);  // Stack grows by 4KB EACH ITERATION
        // Buf is NOT freed until the function returns!
    }
}
```

### `weak` symbols and static linking

Weak symbols behave differently with static vs dynamic linking. With static linking, a weak symbol in an archive may not be linked at all. Use `__attribute__((weakref))` or ensure your build system handles weak symbols correctly.

### VLAs are not supported by MSVC

Code using VLAs is not portable to MSVC. For cross-platform code, use `alloca` (which MSVC supports as `_alloca`) or `malloc`.

### `#pragma once` is not ISO standard

While supported by GCC, Clang, MSVC, and most modern compilers, `#pragma once` is not technically standard C. For maximum portability, use traditional `#ifndef` include guards. In practice, `#pragma once` is safe for GCC/Clang/MSVC-only codebases.

---

## Cross-Links

- [[C/01_Foundations/05_Structs_Unions_and_Bit_Fields]] for packed structs and alignment
- [[C/01_Foundations/03_Dynamic_Memory]] for malloc vs alloca trade-offs
- [[C/01_Foundations/06_Preprocessor_and_Compilation]] for #pragma and compiler flags
- [[C/03_Advanced/07_Inline_Assembly_ABI_and_Calling_Conventions]] for __attribute__((interrupt)), ABI
- [[C/02_Core/07_Debugging_with_GDB]] for debugging attribute-influenced code
