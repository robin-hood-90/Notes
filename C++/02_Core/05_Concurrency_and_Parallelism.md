---
tags: [cpp, core, concurrency, threads, mutex, async, future, atomics, memory-ordering, parallel-algorithms]
aliases: ["Concurrency", "std::thread", "std::mutex", "std::async", "std::atomic", "Parallel Algorithms"]
status: stable
updated: 2026-05-09
---

# Concurrency and Parallelism

> [!summary] Goal
> Master C++ concurrency — threads, mutexes, condition variables, async/future, atomics, memory ordering, and parallel algorithms (C++17). Build thread-safe, performant concurrent code.

## Table of Contents

1. [Threads](#threads)
2. [Mutexes and Locks](#mutexes-and-locks)
3. [Condition Variables](#condition-variables)
4. [std::async and std::future](#stdasync-and-stdfuture)
5. [Parallel Algorithms (C++17)](#parallel-algorithms)
6. [C++20 Synchronization Primitives](#c20-synchronization-primitives)
7. [Pitfalls](#pitfalls)

---

## Threads

> [!info] std::thread
> `std::thread` represents a single thread of execution. Create it with a callable (function, lambda, functor). Always `join()` or `detach()` before the `thread` object is destroyed (otherwise `std::terminate` is called). Threads share the same address space — synchronize access to shared data with mutexes.

```cpp
#include <thread>
#include <iostream>

// Basic thread
void worker(int id) {
    std::cout << "Thread " << id << " running\n";
}

std::thread t1(worker, 1);
std::thread t2(worker, 2);

t1.join();     // Wait for t1 to finish
t2.detach();   // Let t2 run independently (can't join later)

// Lambda
std::thread t3([]{
    std::cout << "Lambda thread\n";
});
t3.join();

// Hardware concurrency
unsigned int n = std::thread::hardware_concurrency();  // Number of cores
std::cout << n << " concurrent threads supported\n";
```

---

## Mutexes and Locks

> [!info] Mutex
> A mutex (mutual exclusion) prevents multiple threads from accessing shared data simultaneously. `std::mutex` is the basic type. `lock_guard` and `unique_lock` use RAII to ensure the mutex is always released, even if an exception is thrown.

```cpp
#include <mutex>

std::mutex mtx;
int shared_counter = 0;

void increment() {
    std::lock_guard<std::mutex> lock(mtx);  // RAII: lock automatically
    ++shared_counter;
    // Automatically unlocked when lock goes out of scope
}
```

### Mutex types

| Mutex type | Description | Use case |
|------------|-------------|----------|
| `std::mutex` | Basic mutex (non-recursive, non-timed) | Most cases |
| `std::recursive_mutex` | Same thread can lock multiple times | Recursive functions |
| `std::timed_mutex` | `try_lock_for`, `try_lock_until` | Timeout-based locking |
| `std::shared_mutex` (C++17) | Multiple readers, single writer | Reader-writer locks |

### Lock guards

```cpp
// lock_guard — simple RAII lock (C++11)
std::lock_guard<std::mutex> lock(mtx);     // Lock on construction
// Auto-unlock on destruction

// unique_lock — more flexible (C++11)
std::unique_lock<std::mutex> lock(mtx);    // Can defer, lock/unlock manually
std::unique_lock<std::mutex> defer_lock(mtx, std::defer_lock);  // Don't lock yet
lock.lock();                               // Manual lock
lock.unlock();                             // Manual unlock

// scoped_lock — lock multiple mutexes without deadlock (C++17)
std::scoped_lock lock(mtx1, mtx2);         // Locks both in a deadlock-free way
```

### Deadlock avoidance

```cpp
// ❌ DEADLOCK: two threads lock mutexes in different order
// Thread 1: lock(a), lock(b)
// Thread 2: lock(b), lock(a)  → Both wait forever!

// ✅ Correct: lock in the same order, or use scoped_lock
std::scoped_lock lock(mtx1, mtx2);  // Locks both atomically — no deadlock

// ✅ Alternative: std::lock
std::lock(mtx1, mtx2);              // Lock both without deadlock
std::lock_guard<std::mutex> lock1(mtx1, std::adopt_lock);  // Adopt the already-locked mutex
std::lock_guard<std::mutex> lock2(mtx2, std::adopt_lock);
```

---

## Condition Variables

> [!info] Condition variable
> `std::condition_variable` lets threads wait for a condition (e.g., "data is ready"). It's used with a mutex. `wait()` atomically unlocks the mutex and blocks. When signaled, it re-acquires the mutex and returns. Always check the condition in a loop (spurious wakeup).

```cpp
#include <condition_variable>

std::mutex mtx;
std::condition_variable cv;
std::vector<int> data;
bool ready = false;

// Producer
void producer() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        data = {1, 2, 3, 4, 5};
        ready = true;
    }
    cv.notify_one();   // Wake one waiting consumer
    // cv.notify_all(); // Wake all waiting threads
}

// Consumer
void consumer() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return ready; });   // Wait until ready is true
    // Now data is available — locked again
    for (int x : data) { /* process */ }
}
```

### Bounded producer-consumer queue

```cpp
template<typename T>
class ThreadSafeQueue {
    std::queue<T> queue;
    std::mutex mtx;
    std::condition_variable not_empty;
public:
    void push(T value) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            queue.push(std::move(value));
        }
        not_empty.notify_one();
    }

    T pop() {
        std::unique_lock<std::mutex> lock(mtx);
        not_empty.wait(lock, [this]{ return !queue.empty(); });
        T value = std::move(queue.front());
        queue.pop();
        return value;
    }
};
```

---

## std::async and std::future

> [!info] std::async
> `std::async` runs a function asynchronously (possibly in a separate thread). It returns a `std::future` that will contain the result. The function is executed on the async's thread pool or a new thread. Use `std::launch::async` to force async execution, `std::launch::deferred` to defer until `.get()` is called.

```cpp
#include <future>

// Basic async
int compute(int x) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return x * x;
}

auto future = std::async(std::launch::async, compute, 42);
// ... do other work ...
int result = future.get();              // Blocks until result is ready

// Multiple async tasks
std::vector<std::future<int>> futures;
for (int i = 0; i < 10; ++i) {
    futures.push_back(std::async(std::launch::async, compute, i));
}

int sum = 0;
for (auto& f : futures) {
    sum += f.get();
}

// std::promise (manual future)
std::promise<int> promise;
auto future = promise.get_future();

std::thread t([&promise] {
    try {
        promise.set_value(42);           // Fulfill the promise
    } catch (...) {
        promise.set_exception(std::current_exception());  // Or set exception
    }
});

future.get();                            // 42
t.join();

// std::packaged_task (callable → future)
std::packaged_task<int(int, int)> task([](int a, int b) { return a + b; });
auto fut = task.get_future();
std::thread t2(std::move(task), 10, 20);
std::cout << fut.get();                  // 30
t2.join();
```

---

## Parallel Algorithms (C++17)

> [!info] Parallel algorithms
> C++17 adds execution policies to ~60 algorithms. `std::execution::seq` (sequential — default), `std::execution::par` (parallel — may parallelize), `std::execution::par_unseq` (parallel + vectorized — more aggressive). The implementation decides how to parallelize based on hardware.

```cpp
#include <execution>

std::vector<int> data(1'000'000);
std::iota(data.begin(), data.end(), 0);

// Sequential (default — as before C++17)
std::sort(std::execution::seq, data.begin(), data.end());

// Parallel (may use multiple threads)
std::sort(std::execution::par, data.begin(), data.end());

// Parallel + Vectorized (may use threads + SIMD)
std::sort(std::execution::par_unseq, data.begin(), data.end());

// Parallel algorithms examples
std::for_each(std::execution::par, data.begin(), data.end(), [](int& x) { x *= 2; });
auto result = std::find(std::execution::par, data.begin(), data.end(), 42);
int sum = std::reduce(std::execution::par, data.begin(), data.end(), 0);
std::transform(std::execution::par, data.begin(), data.end(), data.begin(),
    [](int x) { return x * x; });

// ⚠️ The parallel versions require no data races!
// Accessing shared data from inside a parallel algorithm is UB.
```

---

---

## C++20 Synchronization Primitives

> [!info] C++20 sync
> C++20 introduced `std::jthread` (RAII thread with cancellation), `std::latch` (single-use countdown), `std::barrier` (reusable phased synchronization with completion callback), and `std::counting_semaphore` / `std::binary_semaphore` (lightweight permit-based synchronization). These are implemented on top of the same OS primitives as the C++11 types but provide safer and more expressive interfaces.

### `std::jthread` — RAII Thread with Auto-join and Cancellation

`std::jthread` joins automatically on destruction (no more `std::terminate`). It also carries a `std::stop_token` for cooperative cancellation:

```cpp
#include <stop_token>
#include <thread>
#include <iostream>

// RAII join:
{   std::jthread t([] { do_work(); });  }   // Auto-joins on scope exit

// Cooperative cancellation:
std::jthread worker([](std::stop_token st) {
    while (!st.stop_requested()) {
        process_chunk();
    }
    cleanup();
});
worker.request_stop();  // Sets the stop token; worker sees stop_requested() == true
// worker destructor auto-joins

// Multiple-stop-source pattern:
std::stop_source source;
std::jthread t1([](std::stop_token st) { while (!st.stop_requested()) work1(); }, source.get_token());
std::jthread t2([](std::stop_token st) { while (!st.stop_requested()) work2(); }, source.get_token());
source.request_stop();  // Cancels BOTH t1 and t2
```

| Feature | `std::thread` | `std::jthread` |
|:--------|:-------------:|:--------------:|
| Destructor behavior | `std::terminate` if joinable | `join()` then continues |
| Cancellation built-in | No | Yes (via `std::stop_token`) |
| Overhead | Minimal | Slight (stores `stop_state`) |
| RAII safe | No (manual join/detach) | Yes |

### `std::latch` and `std::barrier` — Synchronization Points

```cpp
#include <latch>
#include <barrier>

// Latch: one-shot countdown (all threads wait for N to arrive)
std::latch work_done(3);          // Expect 3 workers
work_done.count_down();           // One worker finished
work_done.wait();                 // Block until count is 0
// work_done.arrive_and_wait();   // count_down() + wait() in one call
// After reaching 0: latch is DONE (cannot reset)

// Barrier: reusable multi-phase synchronization with completion callback
std::barrier barrier(3, []() noexcept {
    std::cout << "All threads reached barrier — next phase\n";
});
// In each worker:
for (int phase = 0; phase < 10; ++phase) {
    compute_phase(phase);
    barrier.arrive_and_wait();    // Wait for all 3 → completion runs → all proceed
}
```

### `std::counting_semaphore` — Permit-Based Synchronization

```cpp
#include <semaphore>

// Binary semaphore (like a lock without ownership):
std::binary_semaphore flag(1);       // Max 1
flag.acquire();                      // Take permit (block if not available)
flag.release();                      // Return permit

// Counting semaphore (N permits):
std::counting_semaphore<10> pool(5); // Max 10, start with 5
pool.release(3);                     // Add 3 more (total 8)
pool.try_acquire();                  // Non-blocking
pool.try_acquire_for(100ms);        // Block up to 100ms
```

### Decision: When to use each C++20 primitive

```text
Need                                      Use
────────────────────────────────────────────────────
RAII-safe thread with auto-join           std::jthread
Cancel a thread independently             stop_source + stop_token
Run code when a stop is requested         stop_callback
One-time wait for N threads to arrive     std::latch
Reusable barrier, multiple phases         std::barrier
Limit access to N resources               counting_semaphore
Bounded producer-consumer (simple)        binary_semaphore (or cv)
```

---

## Pitfalls

### Not joining a thread

If a `std::thread` goes out of scope without `join()` or `detach()`, `std::terminate` is called. Always join or detach:

```cpp
{
    std::thread t(worker);
    // t goes out of scope without join or detach → terminate!
}

// RAII wrapper:
class ThreadGuard {
    std::thread& t;
public:
    explicit ThreadGuard(std::thread& t_) : t(t_) {}
    ~ThreadGuard() { if (t.joinable()) t.join(); }
};
```

### Data race on shared data

```cpp
int counter = 0;
std::vector<std::thread> threads;

for (int i = 0; i < 10; ++i) {
    threads.emplace_back([&counter] {
        for (int j = 0; j < 1000; ++j) {
            counter++;     // ❌ Data race! Not atomic and not mutex-protected
        }
    });
}
// counter may be anything from 0 to 10000 — not just 10000
```

### std::async destruction blocks

When a `std::future` returned by `std::async` is destroyed, if the async task hasn't completed, the destructor BLOCKS until it does. This can cause unexpected serialization if futures go out of scope early:

```cpp
void bad() {
    std::async(std::launch::async, []{ /* work */ });  // ❌ Future destroyed → blocks!
    // Code after this doesn't execute until the async task completes
}
auto future = std::async(std::launch::async, []{ /* work */ });
// ✅ OK: future lives and doesn't block until get() is called
```

### std::atomic not used for shared flags

```cpp
bool ready = false;         // ❌ Not atomic — reading/writing from different threads is UB
std::atomic<bool> ready{false};  // ✅ Correct
```

---

> [!question]- Interview Questions
>
> **Q: What's the difference between `std::lock_guard` and `std::unique_lock`?**
> A: Both use RAII. `lock_guard` is simpler (lock on construction, unlock on destruction). `unique_lock` is more flexible — supports deferred locking, manual `lock()`/`unlock()`, and works with condition variables (which need `unique_lock` for `wait()`). Use `lock_guard` by default; use `unique_lock` when you need the extra flexibility.
>
> **Q: How does std::async work?**
> A: `std::async` runs a function asynchronously and returns a `std::future` holding the result. With `std::launch::async`, the function runs on a new thread. With `std::launch::deferred`, the function runs when `.get()` is called (lazy evaluation). The default policy may choose either.
>
> **Q: What is a condition variable and what is a spurious wakeup?**
> A: A condition variable allows threads to wait for a specific condition. `wait()` atomically unlocks the mutex and blocks until `notify_one()` or `notify_all()` is called. A spurious wakeup is when `wait()` returns even though the condition hasn't been met — always use `wait(lock, predicate)` that checks the condition in a loop.
>
> **Q: What are C++17 parallel algorithms?**
> A: Execution policies (`seq`, `par`, `par_unseq`) that can be passed to ~60 standard algorithms. `par` may parallelize (multiple threads). `par_unseq` may also vectorize (SIMD). The implementation decides the degree of parallelism. The data must be race-free — parallel algorithms don't protect shared data.
>
> **Q: How do you prevent deadlocks in C++?**
> A: (1) Lock mutexes in the same order everywhere. (2) Use `std::lock(mtx1, mtx2)` which locks multiple mutexes atomically. (3) Use `std::scoped_lock` (C++17) which is a variadic RAII deadlock-free lock. (4) Avoid nested locks when possible.

---

## Cross-Links

- [[C++/02_Core/07_Atomics_Lock_Free_and_Memory_Model]] for atomics and lock-free programming
- [[C++/01_Foundations/07_Exception_Handling_and_Safety]] for exception propagation with futures
- [[C++/02_Core/01_Smart_Pointers_and_Memory_Management]] for shared_ptr thread safety
- [[C++/03_Advanced/08_Game_Engine_and_Driver_Dev]] for concurrency in game engines
- [[C++/04_Playbooks/02_Debug_Concurrency_Issues]] for debugging data races
