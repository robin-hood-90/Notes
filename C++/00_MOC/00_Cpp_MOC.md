---
tags: [cpp, moc, index, learning-path]
aliases: ["C++ MOC", "C++ Index", "C++ Learning Path"]
status: stable
updated: 2026-05-11
---

# C++

> [!summary] Scope
> Complete C++ reference from fundamentals through expert-level: classes, RAII, templates, STL, move semantics, concurrency, metaprogramming, concepts, coroutines, game engine design, and driver development.

## Learning Path

```mermaid
flowchart TD
    F01["F01: C++ vs C, Syntax"] --> F02["F02: Classes & RAII"]
    F02 --> F03["F03: Inheritance & Virtual"]
    F01 --> F04["F04: Operator Overloading & Casts"]
    F02 & F03 --> F05["F05: Move Semantics"]
    F01 --> F06["F06: Templates"]
    F02 --> F07["F07: Exception Handling"]
    F01 --> F08["F08: Lambdas & Functional"]
    F05 & F02 --> C01["C01: Smart Pointers"]
    F06 --> C02["C02: STL Containers"]
    F08 & F06 --> C03["C03: Algorithms & Ranges"]
    C02 --> C04["C04: Iterators"]
    F05 & F08 --> C05["C05: Concurrency"]
    F07 --> C06["C06: File I/O & Filesystem"]
    C05 --> C07["C07: Atomics & Lock-Free"]
    F03 & F01 --> C08["C08: UB & Low-Level C++"]
    F06 --> A01["A01: Template Metaprogramming"]
    A01 --> A02["A02: Concepts (C++20)"]
    F05 & F08 --> A03["A03: Coroutines (C++20)"]
    F06 --> A04["A04: CRTP & Mixins"]
    F08 & A04 --> A05["A05: Type Erasure & Patterns"]
    C02 & F06 --> A06["A06: Modules & C++20/23"]
    C05 & C01 --> A07["A07: Performance & Cache"]
    C08 & C07 --> A08["A08: Game/Driver Dev"]
    style F02 fill:#e1f5ff
    style C01 fill:#fff4cc
    style A08 fill:#d9f7d6
```

## Topic Map

| Tier | Files | Topics |
|:----|:-----:|--------|
| **Foundations** | 10 | C++ vs C, classes/RAII, inheritance/virtual, operator overloading/casts, move semantics/value categories, templates (variadic, fold), exceptions/safety, lambdas/functional, attributes/consteval/constinit, **good coding practices** |
| **Core** | 10 | Smart pointers/allocators, STL containers deep dive, algorithms/ranges, iterators/categories, concurrency/async/parallel, file I/O/filesystem, atomics/lock-free, UB/object lifetimes, **optional/chrono/format**, **random/regex** |
| **Advanced** | 9 | Template metaprogramming/SFINAE, concepts (C++20), coroutines, CRTP/mixins, type erasure/patterns, modules/C++20/23 features, performance/cache, game engine/driver dev, **PMR/jthread/C++20 sync** |
| **Playbooks** | 4 | Debug memory (ASan/Valgrind/glibcxx debug), debug concurrency (TSan/Helgrind), **debug compile time/template errors**, production readiness/ABI |
| **Projects** | 3 | Custom vector, thread pool with work stealing |

## Build Systems

| File | Topics |
|------|--------|
| **B01** [[C++/06_Build_Systems/01_CMake_Deep_Dive]] | C++ standards in CMake, compiler detection, vcpkg/Conan, C++ library management, exporting C++ targets, C++ generator expressions |
| **B02** [[C++/06_Build_Systems/02_Make_Deep_Dive]] | C++ Makefile patterns, C++ flags, auto-dependency generation, template instantiation, C++20 modules in Make |

## Key by Career Path

| Path | Focus files |
|------|-------------|
| **Game Dev** | F02, C01, C05, A04, A07, A08, Pr02 |
| **Systems/Kernel** | C08, C07, A06, A08, A07 |
| **High-Perf Computing** | C05, C07, A07, C03, A01 |
| **Interview Prep** | F02, F03, F05, F06, C01, C05, A01 |
| **Modern C++ (C++20/23)** | A02, A03, A06, C03 (Ranges) |

## References

- [cppreference.com](https://en.cppreference.com/w/cpp)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/)
- [isocpp.org](https://isocpp.org/)
