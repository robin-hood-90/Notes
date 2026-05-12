---
tags: [cpp, playbook, memory-debug, asan, ubsan, valgrind, gdb, leaks, glibcxx-debug, libcpp-debug]
aliases: ["Debug Memory Issues", "ASan C++", "Valgrind C++", "GDB STL", "glibcxx debug", "libcpp debug"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug Memory Issues in C++

> [!summary] Goal
> Diagnose and fix C++ memory issues: use-after-free, double delete, buffer overflows, memory leaks, and STL container corruption. Tools: ASan, UBSan, Valgrind, glibc debug modes, and GDB pretty-printers.

## Table of Contents

1. [ASan for C++](#asan-for-c)
2. [STL Debug Modes](#stl-debug-modes)
3. [Custom operator new/delete Tracking](#custom-operator-new-delete-tracking)
4. [GDB Pretty-Printers for STL](#gdb-pretty-printers-for-stl)
5. [Valgrind for C++](#valgrind-for-c)

---

## ASan for C++

```bash
# Compile with AddressSanitizer
g++ -g -O1 -fsanitize=address -fno-omit-frame-pointer program.cpp -o program

# C++-specific issues ASan catches:
#   - new/delete mismatches
#   - Container overflow (vector, string, deque)
#   - use-after-free on shared_ptr internals
#   - Double deletion via raw pointers

# Combine with UBSan:
g++ -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer program.cpp -o program
```

---

## STL Debug Modes

### GCC libstdc++ `_GLIBCXX_DEBUG`

```bash
# Compile with debug checks:
g++ -D_GLIBCXX_DEBUG -g -O0 program.cpp -o program

# What it checks:
#   - Iterator validity (dereferencing past end)
#   - Container bounds (at() and operator[])
#   - Reverse iterator consistency
#   - Algorithm precondition violations (e.g., sorting with invalid comparator)
#   - Container mutation while iterating

# Performance: ~2-10× slower. Use for testing, not production.

# Check if _GLIBCXX_DEBUG is active at runtime:
#include <iostream>
#ifdef _GLIBCXX_DEBUG
std::cout << "Debug mode active\n";
#endif
```

### Clang libc++ `_LIBCPP_DEBUG`

```bash
# libc++ debug mode (level 1: basic checks):
clang++ -D_LIBCPP_DEBUG=1 -g -O0 program.cpp -o program

# Level 2: extended checks (iterator invalidation, bounds):
clang++ -D_LIBCPP_DEBUG=2 -g -O0 program.cpp -o program

# Comparison with _GLIBCXX_DEBUG:
#   - libc++ debug mode is less comprehensive
#   - Catches out-of-bounds, misuse of at()
#   - Does NOT catch all iterator invalidation like _GLIBCXX_DEBUG
```

### MSVC debug mode

```bash
# MSVC: /D_ITERATOR_DEBUG_LEVEL=2 (default in Debug builds)
# Enables checked iterators + iterator invalidation detection.
```

---

## Custom `operator new`/`delete` Tracking

```cpp
// Override global operator new/delete to track allocations:

#include <iostream>
#include <cstdlib>
#include <unordered_map>
#include <mutex>

std::mutex alloc_mutex;
std::unordered_map<void*, size_t> allocations;

void* operator new(size_t size) {
    void* ptr = std::malloc(size);
    if (!ptr) throw std::bad_alloc{};
    {
        std::lock_guard lk(alloc_mutex);
        allocations[ptr] = size;
    }
    return ptr;
}

void operator delete(void* ptr) noexcept {
    if (!ptr) return;
    {
        std::lock_guard lk(alloc_mutex);
        if (allocations.erase(ptr) == 0) {
            // Double free or unknown pointer!
            std::cerr << "Double delete of " << ptr << "\n";
        }
    }
    std::free(ptr);
}

void print_allocations() {
    std::lock_guard lk(alloc_mutex);
    for (const auto& [ptr, size] : allocations) {
        std::println("Leaked: {} ({} bytes)", ptr, size);
    }
}
```

### Linux `mtrace` / `muntrace`

```bash
# mtrace: glibc's built-in malloc tracing

#include <mcheck.h>
int main() {
    mtrace();  // Start tracing
    // ... your code ...
    muntrace();  // Stop tracing
}

# Run with MALLOC_TRACE environment variable:
MALLOC_TRACE=/tmp/trace.log ./program

# Analyze:
mtrace program /tmp/trace.log
# Output: "Memory not freed:" + allocation site
```

### `MALLOC_CHECK_` environment variable

```bash
# glibc heap consistency checking (no recompilation needed):
MALLOC_CHECK_=1 ./program   # Print error message, don't abort
MALLOC_CHECK_=2 ./program   # Abort on heap corruption
MALLOC_CHECK_=3 ./program   # Print + abort
```

---

## GDB Pretty-Printers for STL

```bash
# GDB with STL pretty-printers (Ubuntu: pre-installed)

# In GDB session:
(gdb) print my_vector
# $1 = std::vector of length 5, capacity 8 = {1, 2, 3, 4, 5}
(gdb) print my_map
# $2 = std::map with 3 elements = {[1] = "one", [2] = "two", [3] = "three"}
(gdb) print my_string
# $3 = "hello world"

# Manual activation (if pretty-printers not loaded):
(gdb) python import sys
(gdb) python sys.path.insert(0, '/usr/share/gdb/python')
(gdb) source /usr/share/gdb/python/libstdcxx/v6/printers.py
(gdb) register_libstdcxx_printers(None)

# Print specific element:
(gdb) print my_vector._M_impl._M_start[0]
```

---

## Valgrind for C++

```bash
g++ -g -O0 program.cpp -o program
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./program

# Valgrind catches in C++:
#   - new without delete (memory leak)
#   - Use-after-free on raw pointers
#   - new[] / delete[] mismatches (MismatchedFree)
#   - Conditional jumps on uninitialized values

# Suppression files for known false positives:
valgrind --suppressions=my_suppressions.supp ./program
```

---

## Cross-Links

- [[C++/02_Core/01_Smart_Pointers_and_Memory_Management]] for RAII memory patterns
- [[C++/02_Core/08_Undefined_Behavior_and_Low_Level_Cpp]] for UB sources
- [[C++/04_Playbooks/02_Debug_Concurrency_Issues]] for TSan debugging
