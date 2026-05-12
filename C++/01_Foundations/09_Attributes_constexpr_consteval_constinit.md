---
tags: [cpp, foundations, attributes, consteval, constinit, constexpr, nodiscard, likely, no_unique_address]
aliases: ["C++ Attributes", "consteval", "constinit", "constexpr deep dive", "[[nodiscard]]", "[[likely]]", "[[no_unique_address]]"]
status: stable
updated: 2026-05-11
---

# C++ Attributes, `constexpr`/`consteval`/`constinit`, and Compile-Time Programming

> [!summary] Goal
> Master C++17/20/23 attributes (`[[nodiscard]]`, `[[likely]]`/`[[unlikely]]`, `[[no_unique_address]]`, `[[fallthrough]]`, `[[maybe_unused]]`) and compile-time function evaluation (`constexpr` deep dive, `consteval` immediate functions, `constinit` guarantee, `if consteval`). Understand what each guarantees and how it affects code generation.

## Table of Contents

1. [Why This Matters](#why-this-matters)
2. [Attributes Reference](#attributes-reference)
3. [constexpr Deep Dive](#constexpr-deep-dive)
4. [consteval — Immediate Functions](#consteval-immediate-functions)
5. [constinit — Guaranteed Static Init](#constinit-guaranteed-static-init)
6. [if consteval (C++23)](#if-consteval)
7. [Compiler Support Table](#compiler-support-table)

---

## Why This Matters

Modern C++ provides two categories of annotation:

- **Attributes** (`[[...]]`) — hint the compiler about intent: "this return value must not be ignored", "this branch is hot/cold", "this empty member can be compressed". They're standardized across compilers, unlike `__attribute__` or `__declspec`.
- **Compile-time specifiers** (`constexpr`, `consteval`, `constinit`) — control WHEN code runs. `constexpr` since C++11, but C++20+ makes it dramatically more powerful (virtual, try, dynamic_cast, `vector` and `string`).

---

## Attributes Reference

### `[[nodiscard]]` (C++17)

```cpp
// Ensures the return value is NOT ignored.
// If the caller discards the return, the compiler emits a warning.

[[nodiscard]] int compute_important_value() { return 42; }

void test() {
    compute_important_value();  // WARNING: ignoring return value
    int x = compute_important_value();  // OK
}

// On types (C++20):
struct [[nodiscard]] ErrorInfo { int code; const char* msg; };

ErrorInfo open_file(const char* path);  // The type is nodiscard
void test() {
    open_file("config.txt");  // WARNING: ErrorInfo discarded
}

// With string reason (C++20):
[[nodiscard("Memory leak: caller must free the returned pointer")]]
void* allocate_buffer(size_t size);

// When to use:
//   - Factory functions (make_shared, create_widget)
//   - Error-result types (expected, error_code)
//   - Functions whose sole purpose is to compute a value
//   - Allocator functions returning ownership

// When NOT to use:
//   - void functions
//   - Functions with side effects as primary purpose
//   - Observers that are called for their side effects
```

### `[[maybe_unused]]` (C++17)

```cpp
// Suppresses "unused" warnings deliberately.
// Use when the parameter is intentionally unused over some code path.

void on_event(int id, [[maybe_unused]] const char* name) {
    // name is unused in release builds but needed for debug logging
    if constexpr (debug_enabled) {
        log("Event %d from %s", id, name);
    }
}

class Logger {
    [[maybe_unused]] int log_level_;  // Only used in debug builds
};
```

### `[[fallthrough]]` (C++17)

```cpp
// Indicates deliberate fallthrough in a switch statement.
// Without this, many compilers warn on every fallthrough.

switch (state) {
    case IDLE:
        prepare();
        [[fallthrough]];  // Intentional: fall through to CONNECTING
    case CONNECTING:
        start_connection();
        break;
    case ACTIVE:
        if (needs_refresh()) {
            goto ACTIVE;  // OK: not a fallthrough
        }
        break;
}
```

### `[[likely]]` / `[[unlikely]]` (C++20)

```cpp
// Hints branch probability for optimizer.
// Affects code layout: likely paths are placed in the hot section.
// Without these, the optimizer uses heuristics (loop exits, error checks).

double process(double value) {
    if (value < 0) [[unlikely]] {
        return handle_error(value);
    }
    // Normal path — optimizer lays out the hot path sequentially
    return value * 2.0;
}

// Usage in switch (C++23):
switch (status) {
    [[likely]] case OK: return handle_success();
    [[unlikely]] case ERROR: return handle_error();
    default: return handle_unknown();
}

// Performance impact:
//   - Correct placement: saves icache pollution on cold branches.
//   - Wrong placement: can slow down the hot path.
//   - Measure before adding; don't guess.
```

### `[[no_unique_address]]` (C++20)

```cpp
// Allows an empty data member to NOT occupy any memory (no unique address).
// The compiler can merge the member's storage with another member.
// This is the standard version of the "empty base optimization" (EBCO)
// applied to data members instead of just base classes.

template<typename T, typename Allocator = std::allocator<T>>
struct MyContainer {
    T* data = nullptr;
    size_t size_ = 0;
    [[no_unique_address]] Allocator alloc_;  // 0 bytes if Allocator is stateless
};

// Without [[no_unique_address]]: the allocator takes at least 1 byte.
// With [[no_unique_address]]: zero bytes for std::allocator.

// Real-world: std::vector, std::string, std::deque use this internally.

// Pitfall: two members with [[no_unique_address]] can't share the same address.
struct Bad {
    [[no_unique_address]] Empty e1;
    [[no_unique_address]] Empty e2;  // e2 gets a different address
    // Total size may be > sizeof(Empty) because they can't alias.
};
```

### `[[deprecated]]` (C++14)

```cpp
[[deprecated("Use create_pool(size_t) instead")]]
void create_pool(int);  // Warns at call site
```

---

## `constexpr` Deep Dive

> [!info] constexpr
> A `constexpr` function CAN be evaluated at compile time if the arguments are constant expressions. It can also be called at runtime. Since C++20, `constexpr` functions support: `virtual` calls, `dynamic_cast`, `try`/`catch`, `new`/`delete` (in `constexpr` context with `constexpr` allocators), `std::vector`/`std::string` (if the allocator is `constexpr`-compatible), unions with active member changes.

### C++20 — what became constexpr

```cpp
// C++20 constexpr additions:

// 1. Virtual functions (compile-time polymorphic dispatch)
struct Shape {
    constexpr virtual double area() const = 0;
};
struct Circle : Shape {
    double r;
    constexpr Circle(double r) : r(r) {}
    constexpr double area() const override { return 3.14159 * r * r; }
};
constexpr double circle_area = Circle(5.0).area();  // Compile-time!

// 2. Try-catch (catch only, can't throw)
constexpr int safe_divide(int a, int b) {
    if (b == 0) throw std::runtime_error("div by zero");  // Error: throw not allowed
    return a / b;
}
// Catch blocks ARE allowed but throw is NOT allowed in constant evaluation.
// The try/catch is only for catching from non-constexpr calls.

// 3. dynamic_cast
struct Base { constexpr virtual ~Base() = default; };
struct Derived : Base {};
constexpr bool test() {
    Base* b = new Derived();
    bool result = dynamic_cast<Derived*>(b) != nullptr;  // OK in C++20
    delete b;
    return result;
}

// 4. std::vector and std::string (in local scope)
constexpr int test_vector() {
    std::vector<int> v = {1, 2, 3};  // OK in C++20 (local, no static storage)
    v.push_back(4);
    return v.size();  // 4, computed at compile time
}
```

### `constexpr` allocation limitations

```cpp
// C++20 constexpr allocation rules:
//   - Memory allocated with new MUST be deallocated within the same evaluation.
//   - No static/thread-local storage duration.
//   - No placement new (in strict constant expressions).
//   - std::allocator is constexpr-friendly (C++20).

// C++23 adds: constexpr std::unique_ptr, constexpr const &, implicit lifetimes.

constexpr int valid() {
    int* p = new int(42);
    int r = *p;
    delete p;  // Must free within the same evaluation!
    return r;
}

// constexpr int invalid() {
//     int* p = new int(42);  // Leaks — NOT allowed in constant evaluation
//     return *p;
// }
```

### `constexpr` lambdas

```cpp
// C++17: lambdas are implicitly constexpr if possible.
// C++20: lambdas can be explicitly constexpr for compile-time capture.

constexpr auto square = [](int x) constexpr { return x * x; };
static_assert(square(5) == 25);
```

### Rules summary

```text
What is allowed in constexpr by standard version:

Operation                   C++11    C++14    C++17    C++20    C++23
──────────────────────────────────────────────────────────────────────
Simple expressions          ✅      ✅       ✅       ✅       ✅
Mutable state               ❌      ✅       ✅       ✅       ✅
Loops                       ❌      ✅       ✅       ✅       ✅
constexpr lambdas           ❌      ❌       ✅       ✅       ✅
if constexpr                ❌      ❌       ✅       ✅       ✅
Virtual functions           ❌      ❌       ❌       ✅       ✅
dynamic_cast                ❌      ❌       ❌       ✅       ✅
try/catch                   ❌      ❌       ❌       ✅       ✅
new/delete (bounded)        ❌      ❌       ❌       ✅       ✅
std::vector/string          ❌      ❌       ❌       ✅       ✅
constexpr unique_ptr        ❌      ❌       ❌       ❌       ✅
```

---

## `consteval` — Immediate Functions (C++20)

> [!info] consteval
> A `consteval` function MUST be evaluated at compile time. It's an **immediate function** — the compiler runs it during compilation and the result is embedded in the binary. Unlike `constexpr` (which can also run at runtime), `consteval` is FORCED compile-time execution. This guarantees zero runtime overhead and allows use in contexts where only constant expressions are allowed (template arguments, `static_assert`, array sizes).

```cpp
// consteval — forced compile-time evaluation

consteval int square(int x) { return x * x; }

int runtime = square(5);            // OK: evaluated at compile time, result 25
// int bad = square(runtime_value);  // ERROR: runtime_value is not a constant

// Use case: compile-time string hashing
consteval uint32_t fnv1a(const char* str) {
    uint32_t hash = 2166136261u;
    while (*str) {
        hash ^= static_cast<uint32_t>(*str++);
        hash *= 16777619u;
    }
    return hash;
}

constexpr uint32_t HASH_CONFIG = fnv1a("production");  // Compile-time hash

// Use case: compile-time lookup tables
consteval auto make_sine_table() {
    std::array<double, 360> table{};
    for (int i = 0; i < 360; ++i)
        table[i] = std::sin(i * 3.14159 / 180.0);
    return table;
}

constexpr auto SINE_TABLE = make_sine_table();  // Computed at compile time!
double value = SINE_TABLE[45];  // Runtime: just a table lookup
```

### `consteval` vs `constexpr`

```text
            constexpr                   consteval
─────────────────────────────────────────────────────────────────
Can run at  Both                         Only compile time
runtime?    (if inputs are runtime)
Compile     Required if possible           Always required
time?
Guarantee   May degrade to runtime       Always zero runtime cost
Use with    Variable initializers,       Template arguments,
            static_assert,                static_assert,
            array sizes, etc.            any constant-expression context
            (if inputs are constant)
```

### `consteval` and `constexpr` interaction

```cpp
constexpr int double_it(int x) { return x * 2; }
consteval int triple_it(int x) { return x * 3; }

constexpr int caller(int x) {
    int a = double_it(x);    // OK: double_it works at runtime too
    // int b = triple_it(x); // ERROR: triple_it requires constant input
    return a;
}
```

---

## `constinit` — Guaranteed Static Init (C++20)

> [!info] constinit
> `constinit` guarantees that a variable with static storage duration is initialized at compile time (constant initialization), not at runtime (dynamic initialization). This prevents the **static initialization order fiasco** (SIOF) — when two globals in different translation units depend on each other's initialization order.

```cpp
// constinit: must be initialized with a constant expression.
// Unlike constexpr, constinit does NOT imply const — the variable
// can be modified later.

constinit int global_counter = 0;     // OK: zero-init is constant
constinit std::array<int, 5> data{};  // OK: all-zeros is constant
// constinit std::string name = "hello";  // ERROR: std::string constructor is not constexpr
// (though it may be in C++20+ with some implementations)

// The real use: preventing SIOF

// ❌ BAD — possible SIOF:
// a.cpp:
struct Config { int port; };
Config& get_config() {
    static Config cfg{.port = 8080};  // Dynamic init — order matters!
    return cfg;
}
// b.cpp: Config& cfg = get_config();  // SIOF if a.cpp hasn't initialized yet

// ✅ GOOD — guaranteed compile-time init:
// a.cpp:
struct Config { int port; };
constinit Config global_config{.port = 8080};  // Constant init — before main()

// b.cpp: extern Config global_config;  // Always safe to use
```

---

## `if consteval` (C++23)

> [!info] if consteval
> `if consteval` tests whether the enclosing function is being evaluated in a constant expression context. This lets a single function provide different implementations for compile-time vs runtime — without splitting into `constexpr` + runtime overloads.

```cpp
#include <type_traits>

// Before C++23: hard to provide different impls for constexpr vs runtime
// After C++23:

constexpr double compute(double x) {
    if consteval {
        // Compile-time path: use a slower but fully constexpr algorithm
        return x * x;
    } else {
        // Runtime path: could call SIMD intrinsics
        return x * x;
    }
}

// Practical: constexpr-compatible logging
constexpr int parse_int(const char* s) {
    if consteval {
        int r = 0;
        while (*s) r = r * 10 + (*s++ - '0');
        return r;
    } else {
        return std::stoi(s);  // Runtime version: exception-safe, locale-aware
    }
}
```

---

## Compiler Support Table

| Feature | Standard | GCC | Clang | MSVC |
|---------|:--------:|:---:|:----:|:----:|
| `[[nodiscard]]` | C++17 | 7+ | 3.9+ | 2017+ |
| `[[maybe_unused]]` | C++17 | 7+ | 3.9+ | 2017+ |
| `[[fallthrough]]` | C++17 | 7+ | 3.9+ | 2017+ |
| `[[nodiscard("msg")]]` | C++20 | 10+ | 10+ | 2022+ |
| `[[likely]]`/`[[unlikely]]` | C++20 | 9+ | 12+ | 2022+ |
| `[[no_unique_address]]` | C++20 | 9+ | 9+ | 2019+ |
| `consteval` | C++20 | 12+ | 14+ | 2022+ |
| `constinit` | C++20 | 12+ | 14+ | 2022+ |
| `constexpr` virtual | C++20 | 10+ | 12+ | 2022+ |
| `constexpr` try/catch | C++20 | 12+ | 10+ | 2022+ |
| `constexpr` `dynamic_cast` | C++20 | 13+ | 12+ | 2022+ |
| `constexpr` vector/string | C++20 | 12+ | 15+ | 2022+ |
| `if consteval` | C++23 | 14+ | 16+ | 2022+ |

---

## Cross-Links

- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for constexpr templates
- [[C++/03_Advanced/01_Template_Metaprogramming_SFINAE_Type_Traits]] for constexpr in TMP
- [[C++/02_Core/08_Undefined_Behavior_and_Low_Level_Cpp]] for static init order fiasco
- [[C++/03_Advanced/06_Modules_and_Cpp20_23_Features]] for other C++20/23 features
