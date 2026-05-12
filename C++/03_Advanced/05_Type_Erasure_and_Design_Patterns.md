---
tags: [cpp, advanced, type-erasure, variant, function, any, visit, design-patterns, strategy, command]
aliases: ["Type Erasure", "std::variant", "std::visit", "std::function internals", "std::any", "Strategy Pattern C++"]
status: stable
updated: 2026-05-11
---

# Type Erasure and Design Patterns in C++

> [!summary] Goal
> Master type erasure in C++ — `std::function` (internals, small buffer optimization, allocation), `std::any` (type erasure with dynamic type checking), `std::variant`/`std::visit` (discriminated unions), and modern C++ implementations of classic design patterns (Strategy, Command) using templates and type erasure.

## Table of Contents

1. [std::function Internals](#stdfunction-internals)
2. [std::any — Type Erasure Without a Signature](#stdany-type-erasure-without-a-signature)
3. [Design Patterns in Modern C++](#design-patterns-in-modern-c)

---

## `std::function` Internals

> [!info] std::function
> `std::function<R(Args...)>` is a type-erased wrapper around any callable (function pointer, lambda, functor, bind expression). It erases the callable's concrete type, keeping only the invocation interface. The key implementation choice: **small buffer optimization (SBO)** — store small callables inline, heap-allocate large ones.

### Small Buffer Optimization (SBO)

```cpp
// std::function must store any callable.
// If the callable fits in a small buffer (~16-32 bytes depending on impl),
// it stores it inline (no heap allocation). Otherwise, it heap-allocates.

// SBO size by implementation:
// libstdc++ (GCC):    16 bytes
// libc++ (Clang):     32 bytes
// MSVC STL:           32 bytes

// Which callables fit in SBO (libc++ 32 bytes)?
//   - Function pointer:                       8 bytes  ✅
//   - Lambda with no captures:                 8 bytes  ✅
//   - Lambda capturing 2 ints:                ~16 bytes ✅
//   - Lambda capturing a std::string:         ~40 bytes ❌ (heap allocate)
//   - std::bind with a few args:              ~32 bytes ✅ or ❌ (boundary)

// Heap allocation is used when the callable + vtable pointer exceed the SBO size.
// Minimizing heap allocations: keep capture lists small.
```

### Vtable layout

```cpp
// Internally, std::function uses a vtable-like mechanism:

// Conceptual structure (simplified):
template<typename R, typename... Args>
class function<R(Args...)> {
    // Pointer to the callable (either SBO or heap)
    // Pointer to a "vtable" of operations:
    //   invoke(R(*), Args...)  — call the stored callable
    //   copy(void* from, void* to) — copy or clone
    //   move(void* from, void* to) — move
    //   destroy(void*) — destruct

    // For SBO: the callable is stored in a small buffer inline
    // For heap: the callable is stored on the heap via operator new

    // Operation dispatch via the vtable pointer has indirect call overhead
    // but is still fast for most use cases (~10-20ns overhead per invocation).
};
```

### When to use (and avoid) std::function

```cpp
// ✅ DO use for:
//   - Storing callbacks for deferred invocation
//   - Type erasure when the callable's concrete type is not known
//   - Registry patterns (event handlers, plugin dispatch)
//   - APIs that accept "any callable" without templates

// ❌ DON'T use for:
//   - Hot paths (virtual call overhead, possible heap allocation)
//   - When you can use a template instead (compile-time dispatch)
//   - Trivial function pointers (use auto* directly)

// Performance note:
// std::function<void()> invocation costs ~10-20ns (SBO case).
// Direct lambda call: 0-2ns (inlined).
// Function pointer call: ~3-5ns.
```

---

## `std::any` — Type Erasure Without a Signature

> [!info] std::any
> `std::any` (C++17) stores a value of ANY type (like `void*` but type-safe). Unlike `std::function` (which only erases a specific call signature), `std::any` erases the TYPE. This is useful for: heterogeneous containers, passing unknown types through generic interfaces, and storing properties.

### Type erasure mechanism

```cpp
// std::any also uses the small buffer optimization + heap fallback:

// SBO size: typically 8-16 bytes (implementation-dependent).
// If T is small and trivially copyable → inline storage.
// If T is large → heap allocation.

// The vtable stores:
//   copy/delete operations for the stored type
//   type_info retrieval for any_cast

// Example:
std::any a = 42;                    // int fits in SBO → no allocation
std::any b = std::string(100, 'x'); // string too large → heap allocation
```

### Usage

```cpp
#include <any>

std::any value = 42;

// Check type:
if (value.has_value()) { /* has value */ }
if (value.type() == typeid(int)) { /* is int */ }

// Extract:
int i = std::any_cast<int>(value);           // Throws std::bad_any_cast if wrong
int* p = std::any_cast<int>(&value);         // Returns nullptr if wrong (no throw)

// Any container:
std::vector<std::any> mixed;
mixed.push_back(42);
mixed.push_back(std::string("hello"));
mixed.push_back(3.14);

for (const auto& v : mixed) {
    if (v.type() == typeid(int))
        std::println("int: {}", std::any_cast<int>(v));
    else if (v.type() == typeid(std::string))
        std::println("string: {}", std::any_cast<std::string>(v));
}
```

### When to use std::any

```text
✅ Use std::any when:
  - You need to store values of many different types in one container
  - You're implementing a dynamic property bag or message bus
  - The set of possible types is not known at compile time

❌ Don't use std::any when:
  - The number of types is fixed and known (use std::variant)
  - Type safety matters (any_cast can throw)
  - Performance is critical (type check + extraction overhead)
```

---

## Design Patterns in Modern C++

### Strategy Pattern with Type Erasure

```cpp
// Traditional Strategy (GoF): virtual base class + derived implementations.
// Modern C++: std::function provides built-in strategy via type erasure.

// ❌ Old way — virtual Strategy base:
struct Strategy {
    virtual ~Strategy() = default;
    virtual int execute(int) const = 0;
};
struct MultiplyStrategy : Strategy {
    int execute(int x) const override { return x * 2; }
};

// ✅ Modern C++ — std::function-based strategy:
class Processor {
    std::function<int(int)> strategy_;
public:
    // Accept any callable (function pointer, lambda, functor)
    explicit Processor(std::function<int(int)> s) : strategy_(std::move(s)) {}

    int process(int x) const { return strategy_(x); }
};

// Usage:
Processor p1([](int x) { return x * 2; });
Processor p2([](int x) { return x + 1; });
Processor p3(MultiplyByThree{});  // Custom functor
```

### Command Pattern with Type Erasure

```cpp
// The Command pattern encapsulates a request as an object.
// Modern C++: std::function as command.

// Traditional Command interface:
struct Command {
    virtual ~Command() = default;
    virtual void execute() = 0;
};

// Modern C++ — just a std::function:
using Command = std::function<void()>;

// Queue with commands:
class CommandQueue {
    std::deque<Command> queue_;
public:
    void push(Command cmd) { queue_.push_back(std::move(cmd)); }
    void execute_all() {
        while (!queue_.empty()) {
            auto cmd = std::move(queue_.front());
            queue_.pop_front();
            cmd();  // Execute
        }
    }
};
```

### External Polymorphism

```cpp
// External polymorphism: adapt an existing type to an interface without
// modifying the type (no base class). Uses type erasure.

// The interface we want:
template<typename T>
concept Drawable = requires(T t) { t.draw(); };

// Type-erased wrapper:
class DrawableObject {
    std::any value_;
    // Vtable-like dispatch:
    void (*draw_fn_)(const std::any&);

public:
    template<Drawable T>
    explicit DrawableObject(T val)
        : value_(std::move(val))
        , draw_fn_([](const std::any& v) { std::any_cast<const T&>(v).draw(); })
    {}

    void draw() const { draw_fn_(value_); }
};

// Now both Circle (which has draw()) and Rectangle can be stored
// without inheriting from a common base.
```

---

## Cross-Links

- [[C++/03_Advanced/04_CRTP_Mixins_and_Static_Polymorphism]] for CRTP vs type erasure
- [[C++/02_Core/01_Smart_Pointers_and_Memory_Management]] for std::function allocation patterns
- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for template primitives used in any/function
- [[C++/02_Core/03_STL_Algorithms_and_Ranges]] for functional composition with std::function
