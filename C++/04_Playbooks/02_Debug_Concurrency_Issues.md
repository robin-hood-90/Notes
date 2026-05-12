---
tags: [cpp, playbook, concurrency, data-races, deadlocks, tsan, helgrind, threadsanitizer, lock-free, folly-synchronized]
aliases: ["Debug Concurrency", "TSan C++", "Data Race Patterns", "Deadlock Detection", "libcpp debug concurrency"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug Concurrency Issues

> [!summary] Goal
> Diagnose data races, deadlocks, and thread safety issues in C++. Tools: ThreadSanitizer, Helgrind, `_LIBCPP_DEBUG`, and `folly::Synchronized` patterns.

## Table of Contents

1. [TSan for C++](#tsan-for-c)
2. [Data Race Patterns by Atomic Ordering](#data-race-patterns-by-atomic-ordering)
3. [Deadlock Detection](#deadlock-detection)
4. [std::async Pitfalls](#stdasync-pitfalls)

---

## TSan for C++

```bash
# Compile with ThreadSanitizer:
g++ -g -O1 -fsanitize=thread -lpthread program.cpp -o program
./program

# TSan reports:
# WARNING: ThreadSanitizer: data race
#   Write of size 4 at ... by thread T1:
#     #0 worker program.cpp:25
#   Previous write of size 4 at ... by thread T2:
#     #0 worker program.cpp:25

# Clang equivalent:
clang++ -g -O1 -fsanitize=thread program.cpp -o program

# MSVC:
# cl /fsanitize=thread program.cpp  (VS 2022 17.8+)

# TSan suppression file for known races:
# suppressions.txt
# race:my_known_race_function
export TSAN_OPTIONS="suppressions=suppressions.txt"
```

### Common C++ data race patterns

```cpp
// Pattern 1: Non-atomic shared counter
int counter = 0;
// Thread 1: ++counter;
// Thread 2: ++counter;
// → counter may be 1, not 2!

// Pattern 2: Vector access without synchronization
std::vector<int> data;
// Thread 1: data.push_back(42);
// Thread 2: size_t s = data.size();
// → UB: vector is not thread-safe

// Pattern 3: shared_ptr without atomic ops (pre-C++20)
std::shared_ptr<int> sp = std::make_shared<int>(42);
// Thread 1: sp = std::make_shared<int>(10);
// Thread 2: int v = *sp;
// → UB: shared_ptr is not atomic by default
// ✅ Fix: std::atomic<std::shared_ptr<int>> (C++20)
```

---

## Data Race Patterns by Atomic Ordering

```cpp
// Races that only happen with certain memory orders:

// Pattern 1: Relaxed + data dependency
std::atomic<bool> ready{false};
int data = 0;

// Thread 1 (writer):
data = 42;
ready.store(true, std::memory_order_relaxed);  // ⚠️ Too weak!

// Thread 2 (reader):
if (ready.load(std::memory_order_relaxed)) {   // ⚠️ Too weak!
    std::println("{}", data);  // May print 0! (relaxed doesn't order data)
}
// ✅ Fix: store(release) + load(acquire)

// Pattern 2: Acquire/release inversion
std::atomic<int> x{0}, y{0};

// Thread 1:
x.store(1, std::memory_order_release);
int ry = y.load(std::memory_order_acquire);

// Thread 2:
y.store(1, std::memory_order_release);
int rx = x.load(std::memory_order_acquire);
// ry == 0 && rx == 0 is POSSIBLE with acquire/release!
// (This is the IRIW (Independent Reads of Independent Writes) pattern)

// ✅ Fix: use seq_cst for both, or one seq_cst + one ordering-dependent
```

---

## `folly::Synchronized` pattern

```cpp
// folly::Synchronized<T> (from Meta's Folly library)
// Wraps T + mutex, provides RAII locking via operator->.
// Equivalent to manually wrapping with std::mutex.

// Manual:
struct Config {
    std::mutex mtx;
    int port;
    std::string host;
};

{
    std::lock_guard lk(config.mtx);
    use(config.port);
}

// folly::Synchronized:
// folly::Synchronized<Config> config;
// {
//     auto locked = config.wlock();
//     use(locked->port);
//     locked->host = "new";
// }
```

---

## Deadlock Detection

```bash
# TSan also detects deadlocks:
g++ -g -O1 -fsanitize=thread -lpthread program.cpp -o program
./program

# Helgrind (Valgrind):
valgrind --tool=helgrind ./program

# Helgrind output example:
# Thread #1: lock order "A before B" violated
#   (A was previously acquired, then B; now B then A)
#   at 0x...: operator new(unsigned long)
#   by 0x...: main (program.cpp:25)

# Prevention:
#   - Lock mutexes in same order everywhere
#   - Use std::lock(mtx1, mtx2) / std::scoped_lock (C++17) for multiple locks
```

---

## `std::async` Pitfalls

```cpp
// ❌ Pitfall 1: Future destruction blocks on destructor
void bad() {
    std::async(std::launch::async, []{ do_work(); });
    // Future is destroyed here → BLOCKS until work completes!
}
// ✅ Store the future:
auto fut = std::async(std::launch::async, []{ return 42; });

// ❌ Pitfall 2: Exception in std::async if get() never called
auto f = std::async([] { throw std::runtime_error("boom"); });
// f destructor checks exception stored: calls std::terminate!
// ✅ Always call get() on futures with potential exceptions
```

---

## Cross-Links

- [[C++/02_Core/05_Concurrency_and_Parallelism]] for concurrency fundamentals
- [[C++/02_Core/07_Atomics_Lock_Free_and_Memory_Model]] for atomics and lock-free
- [[C++/04_Playbooks/01_Debug_Memory_Issues]] for ASan integration
- [[C++/03_Advanced/09_PMR_jthread_and_Cpp20_Sync]] for C++20 sync primitives
