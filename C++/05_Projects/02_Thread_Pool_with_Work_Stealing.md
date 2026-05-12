---
tags: [cpp, project, thread-pool, work-stealing, concurrency, parallel, task-queue, future, exception-handling]
aliases: ["Thread Pool", "Work Stealing", "Task Queue", "Parallel Processing"]
status: stable
updated: 2026-05-11
---

# Project: Thread Pool with Work Stealing

> [!summary] Goal
> Build a thread pool with work stealing. Understand thread pool architecture, work-stealing deques, graceful shutdown, exception handling, thread pool sizing, and benchmarking vs `std::async`.

## Table of Contents

1. [Design Overview](#design-overview)
2. [Core Implementation](#core-implementation)
3. [Work Stealing](#work-stealing)
4. [Exception Handling and Pool Sizing](#exception-handling-and-pool-sizing)
5. [Benchmarking](#benchmarking)

---

## Design Overview

A thread pool:
- Creates N worker threads at startup
- Each worker has a task queue (deque)
- Tasks are submitted to the pool, queued to one worker
- Idle workers can "steal" tasks from other workers' deques
- Graceful shutdown: finish all tasks, then join all threads

---

## Core Implementation

```cpp
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <future>
#include <queue>
#include <vector>
#include <atomic>

class ThreadPool {
public:
    explicit ThreadPool(size_t num_threads = std::thread::hardware_concurrency())
        : stop_(false) {
        for (size_t i = 0; i < num_threads; ++i)
            workers_.emplace_back([this] { worker_loop(); });
    }

    ~ThreadPool() {
        {
            std::lock_guard lk(mutex_);
            stop_ = true;
        }
        cv_.notify_all();
        for (auto& w : workers_)
            if (w.joinable()) w.join();
    }

    // Submit a task, return a future for the result
    template<typename F, typename... Args>
    auto submit(F&& f, Args&&... args) -> std::future<decltype(f(args...))> {
        using ResultType = decltype(f(args...));
        auto task = std::make_shared<std::packaged_task<ResultType()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        std::future<ResultType> result = task->get_future();
        {
            std::lock_guard lk(mutex_);
            if (stop_) throw std::runtime_error("submit on stopped pool");
            tasks_.push([task]() { (*task)(); });
        }
        cv_.notify_one();
        return result;
    }

private:
    void worker_loop() {
        while (true) {
            std::function<void()> task;
            {
                std::unique_lock lk(mutex_);
                cv_.wait(lk, [this] { return stop_ || !tasks_.empty(); });
                if (stop_ && tasks_.empty()) return;
                task = std::move(tasks_.front());
                tasks_.pop();
            }
            task();  // Execute outside lock
        }
    }

    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<bool> stop_;
};
```

---

## Work Stealing

```cpp
// Work-stealing pool: each worker has its own deque.
// Idle workers steal from other dequeues' BACKs.

class WorkStealingPool {
    struct Worker {
        std::deque<std::function<void()>> queue;
        std::mutex mutex;
    };

    std::vector<Worker> workers_;
    std::vector<std::jthread> threads_;

public:
    WorkStealingPool(size_t n = std::thread::hardware_concurrency())
        : workers_(n) {
        for (size_t i = 0; i < n; ++i) {
            threads_.emplace_back([this, i](std::stop_token st) {
                worker_loop(i, st);
            });
        }
    }

    void submit(size_t worker_id, std::function<void()> task) {
        std::lock_guard lk(workers_[worker_id].mutex);
        workers_[worker_id].queue.push_front(std::move(task));  // LIFO: local worker pops front
    }

private:
    void worker_loop(size_t id, std::stop_token st) {
        while (!st.stop_requested()) {
            std::function<void()> task;
            bool got_task = try_pop_or_steal(id, task);
            if (got_task) {
                task();
            } else {
                std::this_thread::yield();  // No work — yield
            }
        }
    }

    bool try_pop_or_steal(size_t id, std::function<void()>& task) {
        // 1. Try own queue (pop front — LIFO, cache-friendly)
        {
            std::lock_guard lk(workers_[id].mutex);
            if (!workers_[id].queue.empty()) {
                task = std::move(workers_[id].queue.front());
                workers_[id].queue.pop_front();
                return true;
            }
        }
        // 2. Steal from others (pop back — FIFO, steals largest remaining)
        auto thief_rand = id + 1;
        for (size_t i = 1; i < workers_.size(); ++i) {
            size_t target = (thief_rand + i) % workers_.size();
            std::lock_guard lk(workers_[target].mutex);
            if (!workers_[target].queue.empty()) {
                task = std::move(workers_[target].queue.back());
                workers_[target].queue.pop_back();
                return true;
            }
        }
        return false;
    }
};
```

---

## Exception Handling and Pool Sizing

```cpp
// Exception handling in the pool:

// Option 1: Let exceptions propagate through std::future (preferred)
auto future = pool.submit([] {
    throw std::runtime_error("task failed");
    return 42;
});
try {
    int result = future.get();
} catch (const std::exception& e) {
    std::cerr << "Task threw: " << e.what() << "\n";
}

// Option 2: catch in the task and return an expected-like result
// (avoid throwing across thread boundaries in hot paths)

// Thread pool sizing:
//   - CPU-bound: std::thread::hardware_concurrency() (N = cores)
//   - I/O-bound: N = cores * (1 + wait_time / compute_time)
//   - Mixed: separate pools for CPU and I/O tasks

// Example: deducing pool size
size_t optimal_thread_count() {
    size_t cores = std::thread::hardware_concurrency();
    return cores == 0 ? 2 : cores + 1;  // +1 for I/O tasks
}
```

---

## Benchmarking

```cpp
// Benchmark vs std::async:

void benchmark_pool(ThreadPool& pool, size_t iterations) {
    std::vector<std::future<int>> futures;
    futures.reserve(iterations);
    auto start = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < iterations; ++i) {
        futures.push_back(pool.submit([i] {
            return static_cast<int>(i * i);
        }));
    }

    int sum = 0;
    for (auto& f : futures)
        sum += f.get();

    auto end = std::chrono::high_resolution_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::println("Pool: {} iterations in {}ms (sum={})", iterations, ms.count(), sum);
}
```

---

## Cross-Links

- [[C++/02_Core/05_Concurrency_and_Parallelism]] for concurrency fundamentals
- [[C++/02_Core/07_Atomics_Lock_Free_and_Memory_Model]] for lock-free deque patterns
- [[C++/04_Playbooks/02_Debug_Concurrency_Issues]] for TSan debugging
- [[C++/03_Advanced/01_Template_Metaprogramming_SFINAE_Type_Traits]] for submit() type deduction
