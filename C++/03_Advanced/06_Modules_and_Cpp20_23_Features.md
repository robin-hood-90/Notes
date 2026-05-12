---
tags: [cpp, advanced, modules, cpp20, cpp23, span, mdspan, expected, generator, out-ptr, flat-map, deducing-this]
aliases: ["C++20 Modules", "C++20/23 Features", "deducing this", "flat_map", "mdspan", "cpp23 features"]
status: stable
updated: 2026-05-11
---

# Modern C++: Modules and C++20/23 Features

> [!summary] Goal
> Master C++20 modules (fast compilation, proper encapsulation), C++20/23 library additions (`std::span`, `std::mdspan`, `std::expected`, `std::flat_map`, `std::out_ptr`, `std::generator`), and language features (`deducing this`, `using enum`, `explicit(bool)`, `if consteval`, `std::bit_cast`, `std::source_location`).

## Table of Contents

1. [C++20 Language Features](#c20-language-features)
2. [C++20 Library Additions](#c20-library-additions)
3. [C++23 Deducing this](#c23-deducing-this)
4. [C++23 Library Additions](#c23-library-additions)
5. [Modules (C++20)](#modules)

---

## C++20 Language Features

### `using enum` — Scoped Enum Scope

```cpp
// Makes scoped enum values available without repetition:

enum class Color { Red, Green, Blue };

std::string to_string(Color c) {
    switch (c) {
        using enum Color;           // Brings Red, Green, Blue into this scope
        case Red:   return "red";
        case Green: return "green";
        case Blue:  return "blue";
    }
}
```

### `explicit(bool)` — Conditional Explicit

```cpp
// explicit can be parameterized by a boolean expression:

template<typename T>
struct Wrapper {
    // Only allow implicit conversion from types that are convertible with "narrowing"
    explicit(!std::is_convertible_v<T, int>) Wrapper(T val) : value(val) {}
    int value;
};

// Useful for: type-safe wrapper templates where implicit conversion
// should be allowed for some types but not others.

// C++23 also adds explicit this (deducing this):
struct S {
    template<typename Self>
    explicit(this Self&&) operator int() { return 42; }
};
```

### `constexpr` improvements (C++20)

```cpp
// C++20 expanded constexpr significantly:

// 1. Virtual functions can be constexpr:
struct Base { constexpr virtual int get() const = 0; };
struct Derived : Base { constexpr int get() const override { return 42; } };
constexpr int x = Derived{}.get();  // 42, compile-time

// 2. constexpr try/catch (catch only — can't throw):
constexpr int safe_div(int a, int b) {
    if (b == 0) return -1;  // Can't throw, but can handle
    return a / b;
}

// 3. constexpr dynamic_cast:
constexpr bool test(Base* b) {
    return dynamic_cast<Derived*>(b) != nullptr;  // OK in C++20
}

// 4. constexpr std::vector / std::string (stack-only):
constexpr int vec_test() {
    std::vector<int> v{1, 2, 3};    // Allocated and freed within one evaluation
    v.push_back(4);
    return v.size();                  // 4
}
static_assert(vec_test() == 4);
```

### `if consteval` (C++23)

```cpp
// Tests whether the function is being evaluated at compile time:

constexpr double compute(double x) {
    if consteval {
        // Compile-time path (must be constexpr-valid)
        return x * x;
    } else {
        // Runtime path (can use non-constexpr features)
        // e.g., SIMD intrinsic
        return x * x;
    }
}
```

### `std::bit_cast` — Type Punning Without UB

```cpp
#include <bit>

// std::bit_cast reinterprets the object representation of one type
// as another type — WITHOUT violating strict aliasing rules.
// Unlike reinterpret_cast or memcpy, bit_cast is constexpr and well-defined.

float f = 3.14f;
uint32_t bits = std::bit_cast<uint32_t>(f);  // IEEE 754 representation

// constexpr-safe:
constexpr uint64_t double_to_bits = std::bit_cast<uint64_t>(3.14);
```

### `std::endian` — Detect Endianness at Compile Time

```cpp
#include <bit>

if constexpr (std::endian::native == std::endian::little) {
    // Little-endian (x86, ARM)
} else if constexpr (std::endian::native == std::endian::big) {
    // Big-endian (network byte order)
} else {
    // Mixed-endian (unusual, e.g., PDP-11)
}
```

### `std::source_location` — Caller Information

```cpp
#include <source_location>

void log(const std::string& msg,
         const std::source_location& loc = std::source_location::current()) {
    std::println("[{}:{}] {}",
        loc.file_name(), loc.line(), msg);
    // Also: loc.function_name(), loc.column()
}
```

### `std::to_array` — Array from Initializer List

```cpp
#include <array>

auto arr = std::to_array({1, 2, 3, 4, 5});
// decltype(arr) = std::array<int, 5>
// Deduces size from the initializer list — cleaner than std::array<int, 5>{...}
```

### Designated initializers (C++20)

```cpp
struct Point { int x; int y; int z; };
Point p = {.x = 1, .y = 2};  // z is zero-initialized
// Note: C++20 designated initializers are LESS flexible than C99:
//   - Must be in declaration order
//   - Can't mix designated and non-designated
//   - No nested designated init
```

---

## C++20 Library Additions

### `std::span` — Non-owning Contiguous View

```cpp
#include <span>

void process(std::span<int> data) {
    for (int& x : data) x *= 2;
}

std::vector<int> v{1, 2, 3};
int arr[] = {4, 5, 6};
process(v);          // OK: vector → span
process(arr);        // OK: C array → span
process({v.data(), v.size()});  // Manual construction

// Subviews:
std::span<int> first_half = data.first(data.size() / 2);
std::span<int> last_ten = data.last(10);
std::span<int> middle = data.subspan(5, 10);

// Dynamic vs fixed extent:
std::span<int> dyn;                        // dynamic_extent (runtime size)
std::span<int, 10> fixed;                  // extent = 10 (compile-time)
```

### `std::mdspan` — Multi-Dimensional Span (C++23)

```cpp
#include <mdspan>
#include <vector>

std::vector<double> data(12);
auto matrix = std::mdspan(data.data(), 3, 4);  // 3×4 matrix

matrix(1, 2) = 3.14;               // Element access
// matrix.extent(0) — rows, matrix.extent(1) — cols

// With strides (non-contiguous data):
using extents_t = std::dextents<int, 2>;
std::layout_left::mapping<extents_t> left_map{{3, 4}};   // Column-major
std::layout_right::mapping<extents_t> right_map{{3, 4}}; // Row-major
```

---

## C++23 Deducing `this`

> [!info] Deducing this
> C++23 allows `this` to be a deduced parameter in member functions. This lets you avoid writing const/ non-const overloads separately, simplify CRTP, and write recursive lambdas.

### Before C++23: duplicated const/non-const

```cpp
// ❌ C++17: two identical methods differing only in const
class Container {
    const int& operator[](size_t i) const { /* ... */ }      // const version
    int& operator[](size_t i) { /* ... */ }                  // non-const version
};
```

### C++23: deduced this

```cpp
// ✅ C++23: one method with deduced this
class Container {
    template<typename Self>
    auto&& operator[](this Self&& self, size_t i) {
        return std::forward<Self>(self).data_[i];
    }
};
// const Container → returns const int&
// non-const Container → returns int&
```

### Simplifying CRTP

```cpp
// Before (CRTP — the base class never "knows" the derived type):
template<typename Derived>
struct Base {
    Derived& self() { return static_cast<Derived&>(*this); }
    // Every method must call self() — error-prone
};

// C++23 (deducing this — the derived type is deduced on each call):
struct Base {
    template<typename Self>
    void interface(this Self&& self) {
        // Calls the most-derived version
        self.impl();
    }
};
```

### Recursive lambdas

```cpp
// Before C++23: recursive lambdas required std::function (heap allocate)
std::function<int(int)> fib = [&](int n) {
    return n < 2 ? n : fib(n-1) + fib(n-2);
};

// C++23: direct recursion with auto self
auto fib = [](this auto self, int n) -> int {
    return n < 2 ? n : self(n-1) + self(n-2);
};
```

---

## C++23 Library Additions

### `std::expected<T, E>` — Error Handling with Value-or-Error

```cpp
#include <expected>

std::expected<int, std::error_code> safe_divide(int a, int b) {
    if (b == 0) return std::unexpected(make_error_code(errc::invalid_argument));
    return a / b;
}

auto result = safe_divide(10, 2);
if (result) {
    std::println("Result: {}", *result);         // 5
} else {
    std::println("Error: {}", result.error().message());
}

// Monadic operations (like optional):
result.and_then([](int v) -> std::expected<int, std::error_code> {
    return v > 0 ? v : std::unexpected(errc::invalid_argument);
}).transform([](int v) { return v * 2; })
  .or_else([](auto) { return std::expected<int, std::error_code>(1); });
```

### `std::flat_map` / `std::flat_set`

```cpp
#include <flat_map>
#include <flat_set>

// Sorted-vector-based map (contiguous storage, fast iteration, faster than map for
// small-to-medium N, slower insertion than map).
std::flat_map<int, std::string> ages;
ages[30] = "Alice";
ages[25] = "Bob";
// Backed by std::vector<std::pair<K,V>> — cache-friendly iteration

// std::flat_set — same idea for sets
std::flat_set<int> values;
values.insert(3);
values.insert(1);
values.insert(2);
// Iteration is over a contiguous vector (cache-friendly)
```

### `std::generator<T>` — Standard Coroutine Generator

```cpp
#include <generator>

std::generator<int> range(int n) {
    for (int i = 0; i < n; ++i)
        co_yield i;          // Lazy sequence — one element at a time
}

for (int x : range(5)) {
    std::println("{}", x);   // 0, 1, 2, 3, 4
}

// Lazy computation:
std::generator<int> fibonacci() {
    int a = 0, b = 1;
    while (true) {
        co_yield a;
        int next = a + b;
        a = b;
        b = next;
    }
}
```

### `std::out_ptr` / `std::inout_ptr`

```cpp
#include <memory>

// Adapted Pointer helpers for C APIs that return raw pointers via OUT parameters.
// The smart pointer is automatically reset when the function returns.

// C-style API: HRESULT CreateObject(IUnknown** out);
std::unique_ptr<IUnknown, ComDeleter> ptr;
HRESULT hr = CreateObject(std::out_ptr(ptr));
// ptr now owns the object — no manual Release() needed
```

### `import std;` (C++23)

```cpp
// C++23 allows importing the ENTIRE standard library as a module:
// import std;

// All standard library names are available — no more #include.
// Compilation is faster (no preprocessor), and the library can be
// cached as a precompiled module.

// Current status: GCC 14+ has experimental support.
// MSVC 2022 17.10+ has full support.
```

### `std::print` / `std::println`

```cpp
#include <print>

std::println("Hello {}", "world");         // stdout with newline
std::print("No newline");                   // stdout without newline
std::println(std::cerr, "Error: {}", msg);  // To stderr

// Uses std::format internally — same syntax and performance.
```

---

## Modules (C++20)

> [!info] Modules
> Modules replace header files with a faster, more robust compilation model. `import` brings a module's exported declarations into scope. Modules are compiled once — no more include guards, repetition, or ODR violations. Compilation is faster (no textual inclusion/preprocessing).

```cpp
// math.cppm — module interface unit
export module math;

export int add(int a, int b) {
    return a + b;
}

// Not exported — internal to the module
int square(int x) { return x * x; }

// main.cpp
import math;
int main() {
    return add(1, 2);      // OK: add is exported
    // square(3);           // Error: square is not exported
}
```

### Module partitions

```cpp
// math.cppm — primary module interface
export module math;
export import :ops;              // Re-export partition :ops

// ops.cppm — partition
export module math:ops;          // Part of module math
export int times(int a, int b) { return a * b; }
```

### Modules vs headers

```text
                  Headers                   Modules
─────────────────────────────────────────────────────────
Compilation      Re-processed per TU        Compiled once
Encapsulation    All declarations visible   Only exported names visible
ODR violations   Common (macros, inline)    None (module linkage)
Build time       O(N*M) for N TUs          O(N+M) for N TUs, M modules
Tooling          Mature                     Still maturing (CMake: experimental)
```

---

## Cross-Links

- [[C++/01_Foundations/09_Attributes_constexpr_consteval_constinit]] for constexpr, consteval, constinit deep dive
- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for template fundamentals
- [[C++/03_Advanced/03_Coroutines_C20]] for std::generator + coroutines
- [[C++/02_Core/09_Optional_Chrono_and_Format]] for std::format, std::print
- [[C++/02_Core/04_Iterators_and_Iterator_Categories]] for span iterators
- [[C++/02_Core/03_STL_Algorithms_and_Ranges]] for ranges with span
- [[C++/01_Foundations/07_Exception_Handling_and_Safety]] for std::expected vs exceptions
