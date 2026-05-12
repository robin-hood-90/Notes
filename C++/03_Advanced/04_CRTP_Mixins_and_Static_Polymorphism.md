---
tags: [cpp, advanced, crtp, mixins, static-polymorphism, policy-based-design, enable-shared-from-this]
aliases: ["CRTP", "Curiously Recurring Template Pattern", "Static Polymorphism", "Mixin", "Policy-Based Design"]
status: stable
updated: 2026-05-09
---

# CRTP, Mixins, and Static Polymorphism

> [!summary] Goal
> Master the Curiously Recurring Template Pattern (CRTP), mixin classes, policy-based design, and how to achieve compile-time polymorphism without virtual functions. Understand when to use static vs dynamic polymorphism.

## Table of Contents

1. [CRTP](#crtp)
2. [Mixin Classes](#mixin-classes)
3. [Policy-Based Design](#policy-based-design)
4. [CRTP vs Virtual Functions](#crtp-vs-virtual-functions)
5. [Pitfalls](#pitfalls)

---

## CRTP

> [!info] CRTP (Curiously Recurring Template Pattern)
> A class template where the derived class passes itself as a template parameter to its base class. This allows the base to call derived class methods without virtual dispatch — all at compile time. CRTP achieves **static polymorphism** (compile-time virtual-like behavior without vtables).

```cpp
template<typename Derived>
struct Base {
    void interface() {
        // Calls derived implementation without virtual dispatch
        static_cast<Derived*>(this)->implementation();
    }
    
    // Optional: provide a default implementation
    void implementation() {
        std::cout << "Base implementation\n";
    }
};

struct Derived : Base<Derived> {
    void implementation() {
        std::cout << "Derived implementation\n";
    }
};

struct AnotherDerived : Base<AnotherDerived> {
    void implementation() {
        std::cout << "Another implementation\n";
    }
};

template<typename T>
void process(Base<T>& obj) {
    obj.interface();    // Calls the correct implementation at compile time
}
```

### CRTP for static interfaces

```cpp
template<typename Derived>
struct Comparable {
    friend bool operator!=(const Derived& a, const Derived& b) {
        return !(a == b);  // Assumes Derived defines operator==
    }
    
    friend bool operator>(const Derived& a, const Derived& b) {
        return b < a;      // Assumes Derived defines operator<
    }
    
    friend bool operator<=(const Derived& a, const Derived& b) {
        return !(b < a);
    }
    
    friend bool operator>=(const Derived& a, const Derived& b) {
        return !(a < b);
    }
};

struct Point : Comparable<Point> {
    int x, y;
    
    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
    
    bool operator<(const Point& other) const {
        return std::tie(x, y) < std::tie(other.x, other.y);
    }
};
// Point now has all 6 comparison operators from just defining == and <
```

### CRTP for object counting

```cpp
template<typename Derived>
struct ObjectCounter {
    static inline int count = 0;
    
    ObjectCounter() { ++count; }
    ObjectCounter(const ObjectCounter&) { ++count; }
    ObjectCounter(ObjectCounter&&) noexcept { ++count; }
    ~ObjectCounter() { --count; }
    
    static int alive() { return count; }
};

struct Widget : ObjectCounter<Widget> { };
struct Gadget : ObjectCounter<Gadget> { };

Widget w1, w2;
Gadget g1;
std::cout << Widget::alive();    // 2
std::cout << Gadget::alive();    // 1
```

---

## Mixin Classes

> [!info] Mixin
> A mixin is a template class that adds functionality to any type through inheritance. By composing multiple mixins, you can assemble types with various capabilities at compile time. Mixins are the template version of composition.

```cpp
// Mixins — each adds one capability
template<typename Base>
struct Named : Base {
    std::string name;
    void setName(const std::string& n) { name = n; }
    const std::string& getName() const { return name; }
};

template<typename Base>
struct Counted : Base {
    int counter = 0;
    int getCount() const { return counter; }
    void increaseCount() { ++counter; }
};

template<typename Base>
struct ComparableByID : Base {
    // Uses Base::id
    bool operator<(const ComparableByID& other) const {
        return this->id < other.id;
    }
};

// Compose mixins to create a complete type
struct Entity : Named<Counted<ComparableByID<Entity>>> {
    int id;
};

Entity e;
e.setName("Player");
e.increaseCount();
```

---

## Policy-Based Design

> [!info] Policy-based design
> Policy-based design breaks a class into orthogonal behaviors (policies) parameterized as template arguments. Each policy implements a single concern: allocation strategy, locking strategy, threading model, etc. The most famous example is `std::allocator` (the allocation policy for containers).

```cpp
// Policies
struct SingleThread {
    struct Lock { };
    struct LockGuard { };
};

struct MultiThread {
    struct Lock {
        std::mutex mtx;
        void lock() { mtx.lock(); }
        void unlock() { mtx.unlock(); }
    };
    
    struct LockGuard {
        Lock& lock;
        LockGuard(Lock& l) : lock(l) { lock.lock(); }
        ~LockGuard() { lock.unlock(); }
    };
};

template<typename T, typename ThreadingPolicy = SingleThread>
class Container {
    ThreadingPolicy::Lock mtx;
    std::vector<T> data;
    
public:
    void add(const T& value) {
        typename ThreadingPolicy::LockGuard guard(mtx);
        data.push_back(value);
    }
    
    size_t size() const {
        typename ThreadingPolicy::Lock guard(mtx);  // In real code: use const-correct lock
        return data.size();
    }
};

// Single-threaded (no synchronization overhead)
Container<int, SingleThread> fast_vec;

// Multi-threaded (mutex-protected)
Container<double, MultiThread> safe_vec;
```

---

## CRTP vs Virtual Functions

| Aspect | CRTP | Virtual Functions |
|--------|:----:|:----------------:|
| **Dispatch time** | Compile time | Runtime |
| **Overhead** | Zero (devirtualized) | Vtable lookup (~2 instructions) |
| **Polymorphic containers** | ❌ Can't store different types in one container | ✅ `vector<Base*>` works with derived types |
| **Binary size** | Larger (each instantiation generates code) | Smaller (shared vtable) |
| **Bloat** | Template bloat per type | Minimal |
| **Runtime selection** | ❌ Type must be known at compile time | ✅ Type can be determined at runtime |
| **CRTP features** | Adds comparison operators, object counting, mixins | Can't easily add features to multiple types |
| **Use when** | Performance critical, types known at compile time, add interface methods | Type varies at runtime, heterogeneous containers, dynamic plugins |

---

## Pitfalls

### Derived class passing wrong type to CRTP base

```cpp
struct Derived : Base<Derived> { };   // ✅ Correct
struct Wrong : Base<Derived> { };     // ❌ Wrong! Base<Derived>, not Base<Wrong>!
static_cast<Wrong*>(this) would cast to the wrong type
```

### CRTP code bloat

Each instantiation of a CRTP template generates separate code. If you have 10 types using CRTP, you get 10 copies of the same functions. For vtables, you get one copy plus a small table per type. Use CRTP only when the performance benefit outweighs the code size cost.

### Mixin name conflicts

If two mixins define the same member name, the compiler can't resolve which one to use. Resolve conflicts by renaming members or using disambiguating using declarations.

---

> [!question]- Interview Questions
>
> **Q: What is CRTP and what problem does it solve?**
> A: The Curiously Recurring Template Pattern passes the derived class as a template parameter to its base: `class Derived : public Base<Derived>`. This lets the base class call derived class methods via `static_cast<Derived*>(this)->method()` — achieving static polymorphism (compile-time virtual-like behavior) without the runtime overhead of a vtable lookup.
>
> **Q: What are mixins and how do they differ from multiple inheritance?**
> A: Mixins are template classes that add functionality to any type through inheritance. Unlike multiple inheritance (which inherits from multiple concrete bases), mixins are parameterized by their base type. This allows stacking abilities: `class Widget : Named<Counted<Widget>>`. Mixins avoid diamond problems and are easier to compose than multiple inheritance.
>
> **Q: When would you choose CRTP over virtual functions?**
> A: Choose CRTP when: (a) performance is critical and you can't afford vtable overhead, (b) you need static polymorphism (types known at compile time), (c) you want to add interface methods (like comparison operators) to multiple types. Choose virtual functions when: (d) types are determined at runtime, (e) you need heterogeneous containers, or (f) binary size matters more than micro-performance.

---

## Cross-Links

- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for template fundamentals
- [[C++/01_Foundations/03_Inheritance_Polymorphism_and_Virtual_Functions]] for virtual functions vs CRTP
- [[C++/03_Advanced/01_Template_Metaprogramming_SFINAE_Type_Traits]] for type traits with CRTP
- [[C++/03_Advanced/05_Type_Erasure_and_Design_Patterns]] for type erasure (alternative to CRTP)
- [[C++/02_Core/07_Atomics_Lock_Free_and_Memory_Model]] for policy-based threading
