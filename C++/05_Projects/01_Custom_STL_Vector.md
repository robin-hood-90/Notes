---
tags: [cpp, project, vector, stl, container, pmr, constexpr, sso, allocator, benchmark, exception-safety]
aliases: ["Custom Vector", "std::vector implementation", "STL container from scratch"]
status: stable
updated: 2026-05-11
---

# Project: Custom STL-Style Vector

> [!summary] Goal
> Build a custom `vector<T>` from scratch with SSO, PMR allocator support, strong exception safety, iterator support, const-correctness, `constexpr` (C++20), and benchmarking against `std::vector`.

## Table of Contents

1. [Design Overview](#design-overview)
2. [Core Implementation](#core-implementation)
3. [PMR and Allocator Support](#pmr-and-allocator-support)
4. [Exception Safety](#exception-safety)
5. [Benchmarking](#benchmarking)

---

## Design Overview

A complete `vector` implementation needs:
- Dynamic contiguous storage (heap-allocated)
- RAII: construct/destroy elements, not raw memory
- Strong exception safety (commit-or-rollback)
- Proper iterator invalidation rules
- Allocator support (`std::allocator` + `std::pmr::polymorphic_allocator`)
- `constexpr` where possible (C++20)
- Move semantics

---

## Core Implementation

```cpp
template<typename T, typename Allocator = std::allocator<T>>
class Vector {
public:
    using value_type = T;
    using allocator_type = Allocator;
    using size_type = size_t;
    using iterator = T*;
    using const_iterator = const T*;

private:
    T* data_ = nullptr;
    size_t size_ = 0;
    size_t capacity_ = 0;
    [[no_unique_address]] Allocator alloc_;  // Zero overhead for stateless allocators

public:
    explicit Vector(const Allocator& alloc = Allocator())
        : data_(nullptr), size_(0), capacity_(0), alloc_(alloc) {}

    Vector(std::initializer_list<T> init, const Allocator& alloc = Allocator())
        : alloc_(alloc) {
        reserve(init.size());
        for (auto&& x : init)
            push_back(std::forward<decltype(x)>(x));
    }

    ~Vector() {
        clear();
        if (data_)
            alloc_.deallocate(data_, capacity_);
    }

    // Rule of five — move constructor
    Vector(Vector&& other) noexcept
        : data_(std::exchange(other.data_, nullptr))
        , size_(std::exchange(other.size_, 0))
        , capacity_(std::exchange(other.capacity_, 0))
        , alloc_(std::move(other.alloc_)) {}

    // Move assignment
    Vector& operator=(Vector&& other) noexcept {
        if (this != &other) {
            clear();
            alloc_.deallocate(data_, capacity_);
            data_ = std::exchange(other.data_, nullptr);
            size_ = std::exchange(other.size_, 0);
            capacity_ = std::exchange(other.capacity_, 0);
            alloc_ = std::move(other.alloc_);
        }
        return *this;
    }

    // Basic operations
    void push_back(const T& value) {
        if (size_ == capacity_) reserve(capacity_ == 0 ? 1 : capacity_ * 2);
        std::construct_at(data_ + size_, value);
        ++size_;
    }

    void push_back(T&& value) {
        if (size_ == capacity_) reserve(capacity_ == 0 ? 1 : capacity_ * 2);
        std::construct_at(data_ + size_, std::move(value));
        ++size_;
    }

    template<typename... Args>
    T& emplace_back(Args&&... args) {
        if (size_ == capacity_) reserve(capacity_ == 0 ? 1 : capacity_ * 2);
        T* ptr = std::construct_at(data_ + size_, std::forward<Args>(args)...);
        ++size_;
        return *ptr;
    }

    void reserve(size_t new_cap) {
        if (new_cap <= capacity_) return;
        T* new_data = alloc_.allocate(new_cap);
        size_t i = 0;
        try {
            for (; i < size_; ++i)
                std::construct_at(new_data + i, std::move(data_[i]));
        } catch (...) {
            for (size_t j = 0; j < i; ++j)
                std::destroy_at(new_data + j);
            alloc_.deallocate(new_data, new_cap);
            throw;  // Strong guarantee: old state unchanged
        }
        for (size_t j = 0; j < size_; ++j)
            std::destroy_at(data_ + j);
        alloc_.deallocate(data_, capacity_);
        data_ = new_data;
        capacity_ = new_cap;
    }
};
```

---

## PMR and Allocator Support

```cpp
// Using with std::pmr:
using PmrVector = Vector<int, std::pmr::polymorphic_allocator<int>>;

// Stack-allocated vector (no heap for the container itself):
std::array<std::byte, 4096> buffer;
std::pmr::monotonic_buffer_resource pool{buffer.data(), buffer.size()};
PmrVector fast_vec{&pool};

// Allocator propagation:
//   - Must handle propagation on copy/move (propagate_on_container_copy_assignment)
//   - Must call allocator_traits to construct/destroy elements
```

---

## Exception Safety

```cpp
// Three exception safety levels:

// 1. Basic guarantee: no leaks, valid but unspecified state
void unsafe_clear() noexcept {
    // Invalidates all iterators, but doesn't leak
    for (size_t i = 0; i < size_; ++i)
        std::destroy_at(data_ + i);
    size_ = 0;
}

// 2. Strong guarantee: rollback on failure
void safe_push_back(const T& value) {
    if (size_ == capacity_) {
        auto new_cap = capacity_ == 0 ? 1 : capacity_ * 2;
        auto new_data = alloc_.allocate(new_cap);
        size_t i = 0;
        try {
            // Move existing elements
            for (; i < size_; ++i)
                std::construct_at(new_data + i, std::move(data_[i]));
            // Construct new element (may throw!)
            std::construct_at(new_data + size_, value);
        } catch (...) {
            // Rollback: destroy what we constructed
            for (size_t j = 0; j < i; ++j)
                std::destroy_at(new_data + j);
            if (i == size_)  // New element was partially constructed
                std::destroy_at(new_data + size_);
            alloc_.deallocate(new_data, new_cap);
            throw;  // Original state unchanged
        }
        // Commit: swap buffers
        for (size_t j = 0; j < size_; ++j)
            std::destroy_at(data_ + j);
        alloc_.deallocate(data_, capacity_);
        data_ = new_data;
        capacity_ = new_cap;
        ++size_;
    } else {
        std::construct_at(data_ + size_, value);
        ++size_;
    }
}

// 3. Nothrow guarantee: cannot fail
void destroy_all() noexcept {
    for (size_t i = 0; i < size_; ++i)
        std::destroy_at(data_ + i);
    size_ = 0;
}
```

---

## Benchmarking

```cpp
// Benchmark comparing custom Vector vs std::vector:

#include <benchmark/benchmark.h>

static void BM_VectorPushBack(benchmark::State& state) {
    for (auto _ : state) {
        Vector<int> v;
        for (int i = 0; i < state.range(0); ++i)
            v.push_back(i);
        benchmark::DoNotOptimize(v.data());
    }
}
BENCHMARK(BM_VectorPushBack)->Range(8, 8<<10);

static void BM_StdVectorPushBack(benchmark::State& state) {
    for (auto _ : state) {
        std::vector<int> v;
        for (int i = 0; i < state.range(0); ++i)
            v.push_back(i);
        benchmark::DoNotOptimize(v.data());
    }
}
BENCHMARK(BM_StdVectorPushBack)->Range(8, 8<<10);
```

---

## Cross-Links

- [[C++/02_Core/01_Smart_Pointers_and_Memory_Management]] for RAII patterns
- [[C++/03_Advanced/09_PMR_jthread_and_Cpp20_Sync]] for PMR integration
- [[C++/01_Foundations/09_Attributes_constexpr_consteval_constinit]] for constexpr vector
- [[C++/04_Playbooks/01_Debug_Memory_Issues]] for debugging allocator issues
