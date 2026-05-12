---
tags: [cpp, advanced, pmr, polymorphic-allocator, memory-resource, jthread, stop-token, latch, barrier, semaphore]
aliases: ["std::pmr", "Polymorphic Memory Resources", "std::jthread", "std::stop_token", "std::latch", "std::barrier", "std::semaphore"]
status: stable
updated: 2026-05-11
---

# PMR, `std::jthread`, and C++20 Synchronization

> [!summary] Goal
> Master C++20's allocator model (`std::pmr` — polymorphic memory resources) and synchronization primitives (`std::jthread` with `std::stop_token`, `std::latch`, `std::barrier`, `std::counting_semaphore`). Build faster, more composable concurrent code.

## Table of Contents

1. [Polymorphic Memory Resources (PMR)](#polymorphic-memory-resources)
2. [std::jthread and Cooperative Cancellation](#stdjthread-and-cooperative-cancellation)
3. [std::latch and std::barrier](#stdlatch-and-stdbarrier)
4. [std::counting_semaphore](#stdcountingsemaphore)
5. [Decision Guide](#decision-guide)

---

## Polymorphic Memory Resources (PMR)

> [!info] PMR
> C++17's `<memory_resource>` introduces polymorphic allocators: instead of each container binding to a specific allocator type (which changes the container's type), PMR uses a virtual interface (`std::memory_resource`) to dispatch allocation. This lets you change allocation strategy WITHOUT changing the container type: `std::pmr::vector<T>` is `std::vector<T, std::pmr::polymorphic_allocator<T>>`.

### Standard resources

```cpp
#include <memory_resource>
#include <vector>
#include <array>

// 1. monotonic_buffer_resource — bump allocator (fastest for short-lived work)
//   - Allocates from a pre-allocated buffer or falls back to new/delete
//   - NEVER deallocates individual allocations (clears entire buffer at reset)
//   - Perfect for temporary computations (parsing, serialization, per-request scratch)

std::array<std::byte, 1024> buffer;   // Stack buffer
std::pmr::monotonic_buffer_resource pool{buffer.data(), buffer.size(), std::pmr::new_delete_resource()};
std::pmr::vector<int> vec{&pool};     // Allocates from the pool, falls back to heap

// 2. unsynchronized_pool_resource — pool of fixed-size blocks (fast with allocations)
//   - Manages pools for specific block sizes (like slab allocator)
//   - NOT thread-safe (use synchronized_pool_resource for multi-threaded)
//   - Reclaims individual deallocations — no buffer reset needed

std::pmr::unsynchronized_pool_resource pool;
std::pmr::vector<int> v1{&pool};
std::pmr::string s1{&pool};

// 3. synchronized_pool_resource — thread-safe pool version
std::pmr::synchronized_pool_resource pool_shared;
// Thread-safe, but has lock overhead. Prefer unsynchronized for single-thread.

// 4. null_memory_resource — always throws std::bad_alloc
auto* null = std::pmr::null_memory_resource();
// std::pmr::vector<int> v_never{null};  // Always throws
```

### Custom resource

```cpp
// You can implement your own memory_resource for custom allocation strategies.
// Useful for: arena allocators, logging allocators, stack allocators.
// Override: do_allocate, do_deallocate, do_is_equal.

#include <memory_resource>

class BumpAllocator : public std::pmr::memory_resource {
    std::byte* const start_;
    std::byte* current_;
    const size_t size_;

public:
    BumpAllocator(std::byte* buffer, size_t size)
        : start_(buffer), current_(buffer), size_(size) {}

    void reset() { current_ = start_; }  // Reset for reuse

private:
    void* do_allocate(size_t bytes, size_t alignment) override {
        // Align current pointer
        auto* aligned = std::align(alignment, bytes, reinterpret_cast<void*&>(current_), size_ - (current_ - start_));
        if (!aligned) throw std::bad_alloc();
        current_ = reinterpret_cast<std::byte*>(aligned) + bytes;
        return aligned;
    }

    void do_deallocate(void*, size_t, size_t) override {
        // Bump allocator — never deallocates individually
    }

    bool do_is_equal(const memory_resource& other) const noexcept override {
        return this == &other;
    }
};

// Usage:
std::array<std::byte, 4096> buffer;
BumpAllocator arena{buffer.data(), buffer.size()};
std::pmr::vector<int> vec{&arena};  // All allocations from stack buffer
// No malloc/free calls — very fast!
```

### PMR containers

```cpp
// PMR container aliases (all use polymorphic_allocator):
std::pmr::vector<int> v;              // std::vector<int, polymorphic_allocator<int>>
std::pmr::string s;                    // std::basic_string<char, ..., polymorphic_allocator<char>>
std::pmr::map<int, int> m;            // std::map<...> with PMR allocator
std::pmr::unordered_map<int, int> um; // Same

// When no allocator is provided, PMR uses the default resource:
std::pmr::vector<int> default_vec;    // Same as std::vector<int> (uses new/delete)

// To use a custom resource:
std::array<std::byte, 4096> buf;
std::pmr::monotonic_buffer_resource pool{buf.data(), buf.size()};
std::pmr::vector<int> fast_vec{&pool};   // Uses stack buffer first, falls back to heap
```

### `std::pmr::new_delete_resource()` vs default

```text
std::pmr::vector<int> v1;                  // Uses get_default_resource() (usually new_delete_resource())
std::pmr::vector<int> v2{std::pmr::new_delete_resource()};  // Same (new/delete)

// Set global default:
std::pmr::set_default_resource(&my_custom_global_resource);
// All PMR containers without explicit resource now use my_custom_global_resource
```

---

## `std::jthread` and Cooperative Cancellation

> [!info] jthread
> `std::jthread` (C++20) extends `std::thread` with two features: **RAII join** (destructor calls `join()` — no `std::terminate` on destruction) and **built-in cancellation** via `std::stop_token`. This eliminates the most common thread bugs: forgetting to `join()` or `detach()`.

### RAII join

```cpp
#include <thread>

// std::thread: must join or detach before destruction, otherwise std::terminate
{
    std::thread t([]{ work(); });
    // t goes out of scope without join/detach → std::terminate!
}

// std::jthread: automatically joins on destruction
{
    std::jthread t([]{ work(); });   // Joins automatically on scope exit
}
```

### Cooperative cancellation with stop_token

```cpp
#include <stop_token>

std::jthread worker([](std::stop_token st) {
    while (!st.stop_requested()) {
        do_chunk();
    }
    cleanup();  // Clean exit on cancellation
});

// Cancel from outside:
worker.request_stop();  // Sets stop_token
// worker.join() happens automatically in destructor
```

### stop_source and stop_callback

```cpp
// You can also create cancellation sources independently of jthread:

std::stop_source shared_source;          // Shared cancellation state

// Create callback that fires when stop is requested:
std::stop_callback cb{shared_source.get_token(), [] {
    std::println("Cancellation requested — cleaning up");
}};

// Pass token to multiple consumers:
std::jthread t1([](std::stop_token st) {
    while (!st.stop_requested()) { do_work(); }
}, shared_source.get_token());

std::jthread t2([](std::stop_token st) {
    while (!st.stop_requested()) { do_other_work(); }
}, shared_source.get_token());

// Cancel all workers at once:
shared_source.request_stop();  // Both t1 and t2 see the cancellation
```

### stop_token patterns

```cpp
// Pattern 1: Polling
void worker(std::stop_token st) {
    while (!st.stop_requested()) {
        auto chunk = next_chunk();
        if (chunk.empty()) break;
        process(chunk);
    }
}

// Pattern 2: Blocking with interruption
void reader(std::stop_token st, std::queue<int>& q, std::mutex& mtx, std::condition_variable& cv) {
    while (!st.stop_requested()) {
        std::unique_lock lk(mtx);
        cv.wait(lk, [&] { return !q.empty() || st.stop_requested(); });
        if (st.stop_requested()) break;
        auto val = q.front(); q.pop();
        process(val);
    }
}
```

### jthread vs thread

```text
          std::thread                  std::jthread
─────────────────────────────────────────────────────────────
Join on   Does NOT auto-join          Auto-joins on destruction
destruct  (std::terminate if active)

Detach    Possible                    Also possible (cancels first)

Cancel    Manual (if implemented)     Built-in stop_token
API       —                           request_stop(), stop_token

Overhead  None (minimal wrapper)      Slight (stores stop_state)

Use when  Low-level thread mgmt       RAII-safe threads, cancellation
```

---

## `std::latch` and `std::barrier`

> [!info] Latch vs Barrier
> `std::latch` (C++20) is a single-use countdown synchronization point — threads decrement a counter and wait until it reaches zero. `std::barrier` (C++20) is reusable by default and supports a completion callback that runs when all threads arrive.

### `std::latch` — single-use countdown

```cpp
#include <latch>

std::latch work_done(3);  // Expect 3 threads

void worker(std::latch& latch) {
    do_work();
    latch.count_down();                     // Decrement counter
    // latch.arrive_and_wait()              // Decrement AND wait for zero
}

int main() {
    std::jthread t1(worker, std::ref(work_done));
    std::jthread t2(worker, std::ref(work_done));
    std::jthread t3(worker, std::ref(work_done));

    work_done.wait();                        // Wait for all workers
    std::println("All work completed");
}
```

### `std::barrier` — reusable with completion

```cpp
#include <barrier>
#include <vector>

std::barrier sync_point(3, []() noexcept {
    // Completion function — runs when ALL threads arrive
    // ONLY ONE thread runs this (the one that brings the count to 0)
    std::println("All threads at barrier — proceeding");
});

void phase_worker(int id, std::barrier<>& b) {
    compute_part(id, 1);
    b.arrive_and_wait();     // Wait for all → completion runs → all continue

    compute_part(id, 2);
    b.arrive_and_wait();     // Reusable: next phase

    compute_part(id, 3);
    b.arrive_and_wait();
}

// Dynamic participant count (default is more flexible template):
// std::barrier<> uses a lambda completion function
// std::barrier::arrive — don't wait (decrement, no block)
// std::barrier::wait — block until phase completes
```

---

## `std::counting_semaphore`

> [!info] Semaphore
> `std::counting_semaphore<max_value>` (C++20) is a light-weight synchronization primitive that controls access to a fixed number of resources. `std::binary_semaphore` is an alias for `std::counting_semaphore<1>`.

```cpp
#include <semaphore>

std::counting_semaphore<10> sem(3);   // Max 10, start with 3 permits

// Binary semaphore (like a simple lock, but without ownership):
std::binary_semaphore flag(1);

// Acquire:
sem.acquire();               // Block until permit available
sem.try_acquire();           // Non-blocking — returns bool
sem.try_acquire_for(100ms);  // Try with timeout
sem.try_acquire_until(time); // Try until absolute time

// Release:
sem.release();               // Add one permit (signal)
sem.release(2);              // Add two permits

// Example: bounded producer-consumer (without condition variable)
template<typename T>
class BoundedQueue {
    std::queue<T> queue_;
    std::counting_semaphore<> items_{0};    // Items available
    std::counting_semaphore<> slots_{N};    // Slots available
    std::mutex mtx_;

public:
    void push(T val) {
        slots_.acquire();           // Wait for a free slot
        {
            std::lock_guard lk(mtx_);
            queue_.push(std::move(val));
        }
        items_.release();           // Signal item available
    }

    T pop() {
        items_.acquire();           // Wait for an item
        T val;
        {
            std::lock_guard lk(mtx_);
            val = std::move(queue_.front());
            queue_.pop();
        }
        slots_.release();           // Signal slot free
        return val;
    }
};
```

---

## Decision Guide

```text
What do I need?                         Use
─────────────────────────────────────────────────────────
Fast per-request scratch allocations    monotonic_buffer_resource
Long-lived allocations, no sharing      unsynchronized_pool_resource
Thread-safe variable-size allocator     synchronized_pool_resource
Thread with auto-join + cancel          std::jthread
Cancel a thread from outside            stop_token + stop_source
One-time sync: all workers done         std::latch
Reusable multi-phase sync               std::barrier
Resource pool with N units              counting_semaphore
Notify one waiting thread               binary_semaphore (or cv)
```

---

## Cross-Links

- [[C++/02_Core/05_Concurrency_and_Parallelism]] for std::thread, std::mutex, std::async
- [[C++/02_Core/07_Atomics_Lock_Free_and_Memory_Model]] for atomic operations used internally
- [[C++/01_Foundations/02_Classes_and_RAII]] for RAII patterns underlying jthread and PMR
- [[C++/06_Build_Systems/01_CMake_Deep_Dive]] for CMake setup with C++20 features
