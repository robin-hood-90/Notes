---
tags: [cpp, playbook, production, abi-stability, lto, visibility, sanitizers, core-guidelines]
aliases: ["Production Readiness", "ABI Compatibility", "LTO", "Visibility", "Sanitizer CI"]
status: stable
updated: 2026-05-11
---

# Playbook: Production Readiness and ABI Compatibility

> [!summary] Goal
> Ensure C++ code is production-ready: manage ABI compatibility, optimize with LTO, control symbol visibility, harden with compiler flags, and apply CI sanitizer integration.

## Table of Contents

1. [ABI Compatibility](#abi-compatibility)
2. [LTO and Visibility](#lto-and-visibility)
3. [Security Hardening Flags](#security-hardening-flags)
4. [Sanitizer CI Integration](#sanitizer-ci-integration)

---

## ABI Compatibility

> [!info] ABI
> C++ has NO stable ABI (unlike C). The same code compiled with different compiler versions may produce incompatible binaries. PIMPL idiom hides implementation: if the header doesn't change, the ABI is stable.

### ABI breakers

```cpp
// ❌ These change ABI:
//   - Add/remove virtual functions (changes vtable layout)
//   - Add/remove data members (changes sizeof, layout)
//   - Add virtual function to class with no vtables
//   - Change noexcept on a function

// ✅ ABI-safe:
//   - Add non-virtual functions
//   - Add static members
//   - Add typedefs, enums, constexpr values
//   - Change function bodies (signature stays same)
```

### PIMPL pattern for ABI stability

```cpp
// widget.h — stable ABI (header never changes)
class Widget {
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
public:
    Widget();
    ~Widget();
    void doSomething();
};

// widget.cpp — can change freely (no ABI impact)
struct Widget::Impl {
    int new_member = 42;    // Adding this doesn't change visible ABI
    void helper() {}
};
```

---

## LTO and Visibility

### Link-Time Optimization

```bash
# GCC/Clang: enables inter-procedural optimization across TUs
#   - Inlines across source files
#   - Eliminates dead code
#   - Removes unused virtual functions

# GCC:
g++ -O2 -flto program1.cpp program2.cpp -o program

# CMake:
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
# or: target_link_options(myapp PRIVATE -flto=auto)

# Clang thin LTO (faster than full LTO for large projects):
target_link_options(myapp PRIVATE -flto=thin)

# NOTE: LTO requires ALL object files compiled with the same -flto flag.
# Mixed LTO/non-LTO objects are handled but may lose optimization.
```

### Symbol visibility

```bash
# Default: ALL symbols are exported (large binary, slow loading).
# Recommended: hide everything, export only the public API.

# Compile with hidden visibility:
g++ -fvisibility=hidden -fvisibility-inlines-hidden program.cpp

# Export specific functions:
class __attribute__((visibility("default"))) PublicAPI {
    void public_method();
    void hidden_method();  // Uses hidden (default) visibility
};

# CMake: set target properties
set_target_properties(myapp PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)
```

---

## Security Hardening Flags

```bash
# Recommended release flags:

# Stack canary (detect buffer overflow on stack):
-fstack-protector-strong

# Immediate binding (resolve all symbols at load time):
-Wl,-z,now           # Full RELRO
-Wl,-z,relro         # Partial RELRO

# No execute (NX bit for stack):
-Wl,-z,noexecstack

# Position-independent executable (PIE, ASLR-friendly):
-fpie -pie

# Fortify source (detect buffer overflows at runtime):
-D_FORTIFY_SOURCE=2 -O2

# Full hardening example:
g++ -O2 -D_FORTIFY_SOURCE=2 \
    -fstack-protector-strong \
    -fpie -pie \
    -Wl,-z,now -Wl,-z,relro -Wl,-z,noexecstack \
    -fvisibility=hidden \
    program.cpp -o program
```

### `_GLIBCXX_ASSERTIONS` — lightweight debug checks

```bash
# Less heavy than _GLIBCXX_DEBUG (use in release testing):
-D_GLIBCXX_ASSERTIONS

# Adds runtime checks for:
#   - std::array::operator[] bounds
#   - std::optional::value() access on empty
#   - std::variant::get() type mismatch
# Performance cost: ~5-10% (vs 2-10× for _GLIBCXX_DEBUG)
```

---

## Sanitizer CI Integration

```yaml
# .github/workflows/ci.yml
name: C++ CI
on: [push, pull_request]
jobs:
  sanitizers:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        sanitizer: [address, undefined, thread]
    steps:
      - uses: actions/checkout@v4
      - name: Configure
        run: |
          cmake -B build \
            -DCMAKE_CXX_FLAGS="-fsanitize=${{ matrix.sanitizer }} -fno-omit-frame-pointer -g -O1" \
            -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=${{ matrix.sanitizer }}"
      - name: Build
        run: cmake --build build
      - name: Test
        run: ctest --test-dir build --output-on-failure

  debug-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build with debug checks
        run: |
          cmake -B build -DCMAKE_CXX_FLAGS="-D_GLIBCXX_DEBUG -g -O0"
          cmake --build build
          ctest --test-dir build --output-on-failure
```

### Cross-compiler flags matrix

```text
Flag                    GCC              Clang            MSVC
───────────────────────────────────────────────────────────────
ASan                    -fsanitize=address  same         /fsanitize=address
UBSan                   -fsanitize=undefined same        /fsanitize=undefined
TSan                    -fsanitize=thread   same         /fsanitize=thread (VS 2022+)
FORTIFY_SOURCE          -D_FORTIFY_SOURCE=2 same        /guard:cf (CFG)
Stack protector         -fstack-protector-strong same     /GS
PIE                     -fpie -pie         -fpie -pie  /DYNAMICBASE
LTO                     -flto              -flto=thin  /GL /LTCG
```

---

## Cross-Links

- [[C++/01_Foundations/07_Exception_Handling_and_Safety]] for noexcept and ABI
- [[C++/03_Advanced/04_CRTP_Mixins_and_Static_Polymorphism]] for CRTP vs PIMPL
- [[C++/03_Advanced/06_Modules_and_Cpp20_23_Features]] for module-based compilation
- [[C++/06_Build_Systems/01_CMake_Deep_Dive]] for CMake configuration
