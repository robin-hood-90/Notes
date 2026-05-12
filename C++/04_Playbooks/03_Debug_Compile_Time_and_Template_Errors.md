---
tags: [cpp, playbook, compile-time, template-errors, build-performance, modules, pch, precompiled-headers]
aliases: ["Debug Template Errors", "Compile-Time Optimization", "Build Speed", "C++ Compilation"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug Compile-Time Performance and Template Errors

> [!summary] Goal
> Diagnose and fix slow C++ compilation, reduce template instantiation bloat, and read complex template error messages. Topics: build timing, precompiled headers, unity builds, modules, ccache/sccache, and error message navigation.

## Table of Contents

1. [Measuring Compile Time](#measuring-compile-time)
2. [Reducing Compile Time](#reducing-compile-time)
3. [Reading Template Error Messages](#reading-template-error-messages)
4. [Precompiled Headers and Modules](#precompiled-headers-and-modules)

---

## Measuring Compile Time

```bash
# Clang: time trace
clang++ -std=c++20 -ftime-trace main.cpp -o main
# Opens in chrome://tracing — shows per-template instantiation time

# GCC: time report
g++ -std=c++20 -ftime-report main.cpp -o main
# Shows time per compiler phase

# General build timing:
time cmake --build .

# CMake with ninja: per-file compilation time
ninja -j$(nproc) 2>&1 | tail -20
```

---

## Reducing Compile Time

### External templates

```cpp
// Declare an explicit instantiation in the header:
extern template class std::vector<int>;      // Don't instantiate in this TU

// Define in exactly one .cpp:
template class std::vector<int>;             // Instantiate once

// Saves re-instantiation across multiple TUs.
// Best for: commonly used template types (vector<int>, map<string, string>).
```

### Forward declarations

```cpp
// Instead of #include <vector> in a header:
#include <vector>  // Heavy — includes all of vector

// Use forward declarations where possible:
namespace std { template<typename T> class vector; }
// But: forward-declaring STL types is implementation-defined.
// Better: include only what you need, use PIMPL to hide heavy includes.
```

### Unity builds

```cmake
# CMake: combine multiple .cpp files into one translation unit
# CMake's Unity Build feature (3.16+):
set(CMAKE_UNITY_BUILD ON)
# Compiles: a.unity.cpp → #include "a.cpp" + #include "b.cpp"
# Saves: repeated header processing, template instantiation
# Risk: ODR violations if two TUs define the same symbol
```

### ccache / sccache

```bash
# ccache: cache compiled object files
export CC="ccache gcc"
export CXX="ccache g++"

# sccache: distributed cache (works with CI)
export RUSTC_WRAPPER=sccache  # Also works for Rust!
```

---

## Reading Template Error Messages

### Navigating errors

```text
GCC error message structure:
  source.cpp:10:30: error: no matching function for call to 'min'
      auto x = min(string{}, int{});
                           ^~~
  /usr/include/c++/13/bits/...  ← DEEP: STL internals
  /usr/include/c++/13/bits/...
  /usr/include/c++/13/bits/...
  source.cpp:10:30: note: candidate template ignored: ... deduced conflicting types

Clang's error messages are generally better:
  - Shorter (skips internal STL boilerplate)
  - Shows the actual constraint that failed
  - Color-highlights the offending expressions

How to read:
  1. Skip the first 200 lines of STL internals — jump to your code.
  2. Look for "candidate template ignored" — this tells you WHY.
  3. Look for "deduced conflicting types" — this is the root problem.
  4. Use static_assert with type traits to get earlier, clearer errors:

template<typename T>
void my_func(T val) {
    static_assert(std::is_arithmetic_v<T>,
                  "my_func requires an arithmetic type (int, float, etc.)");
    // ...
}
```

### Common error patterns

```cpp
// 1. Deduced conflicting template argument:
auto x = std::min(42, 3.14);
// Error: deduced conflicting types (int vs double)
// Fix: explicit template argument: std::min<double>(42, 3.14)

// 2. Missing include:
std::cout << std::println("{}", 42);  // Error: 'println' not in std
// Fix: #include <print>

// 3. Concept / constraint failure:
template<std::ranges::range R>
void process(R&& r) { /* ... */ }
process(42);
// Error: int does not satisfy std::ranges::range
// Clang shows which concept sub-expression failed

// 4. Requires clause failure:
template<typename T> requires (sizeof(T) > 4)
void only_large(T) {}
only_large(char{});
// Error: constraint not satisfied
```

---

## Precompiled Headers and Modules

### Precompiled headers

```cmake
# CMake: precompiled headers (3.16+)
target_precompile_headers(myapp PRIVATE
    <vector>
    <string>
    <iostream>
    <algorithm>
)

# Manual:
# Create a pch.hpp with all slow-to-compile headers
# Compile once: g++ -std=c++20 -x c++-header pch.hpp -o pch.hpp.gch
# Use with: g++ -std=c++20 -include pch.hpp main.cpp
# Saves: ~30-50% compile time for large projects
```

### Modules (C++20)

```cpp
// Modules are FASTER than headers:
//   - No preprocessor scanning
//   - Compiled once (cached as BMI — Binary Module Interface)
//   - No ODR violations
//   - No include guards

// CMake modules support (experimental):
set(CMAKE_EXPERIMENTAL_CXX_MODULE_CMAKE_API "2182bf5c-ef0d-489a-91da-49dbc3090d2a")
target_sources(myapp PRIVATE FILE_SET CXX_MODULES FILES math.cppm)
```

---

## Cross-Links

- [[C++/03_Advanced/06_Modules_and_Cpp20_23_Features]] for modules deep dive
- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for template fundamentals
- [[C++/03_Advanced/01_Template_Metaprogramming_SFINAE_Type_Traits]] for TMP techniques
- [[C++/06_Build_Systems/01_CMake_Deep_Dive]] for CMake build configuration
