---
tags: [python, foundations, async, asyncio, await, coroutines, tasks, gather, aiohttp]
aliases: ["Async Python Basics", "asyncio", "async/await", "Coroutines", "Tasks"]
status: stable
updated: 2026-05-29
---

# Async Python Basics

> [!summary] Goal
> Understand Python's `async`/`await` syntax, the `asyncio` event loop, coroutines, tasks, and key async patterns — enough to write correct async code and build on in C03, C06, and A01.

## Table of Contents

1. [Async/Await Syntax](#asyncawait-syntax)
2. [The Event Loop](#the-event-loop)
3. [Coroutines](#coroutines)
4. [Tasks](#tasks)
5. [await vs asyncio.gather](#await-vs-asynciogather)
6. [asyncio.Queue](#asyncioqueue)
7. [Async Context Managers](#async-context-managers)
8. [Async Iterators](#async-iterators)
9. [asyncio.Lock and Semaphore](#asynciolock-and-semaphore)
10. [aiohttp Intro](#aiohttp-intro)
11. [Pitfalls](#pitfalls)

---

## Async/Await Syntax

```python
import asyncio

# A coroutine — defined with `async def`
async def fetch_data(url: str) -> dict:
    # Simulate network I/O
    await asyncio.sleep(1)
    return {"url": url, "status": 200}

# Running a coroutine
async def main():
    # `await` suspends main() until fetch_data() completes
    result = await fetch_data("https://example.com")
    print(result)

asyncio.run(main())   # Entry point — creates event loop, runs main(), closes loop
```

```mermaid
sequenceDiagram
    participant Loop as "Event Loop"
    participant Coro as "main()"
    participant Fetch as "fetch_data()"
    Loop->>Coro: run main()
    Coro->>Fetch: await fetch_data()
    Fetch->>Loop: asyncio.sleep(1) — yield control
    Loop->>Loop: Do other work, timer ticks
    Loop->>Fetch: 1s elapsed, resume fetch_data()
    Fetch-->>Coro: return result
    Coro->>Loop: main() done
```

> [!info] Key insight
> `await` suspends the **current coroutine**, not the whole program. The event loop runs other tasks while waiting. When the awaited operation completes, the coroutine resumes at the same point.

---

## The Event Loop

```python
import asyncio

# asyncio.run() — the correct entry point (Python 3.7+)
asyncio.run(main())

# Manual loop control (for advanced use only)
async def main():
    loop = asyncio.get_running_loop()
    print(f"Loop: {loop}")
    # You almost never need the loop directly
    # Use asyncio functions (gather, sleep, create_task) instead

# Getting the event loop
# Python 3.10+: asyncio.get_running_loop()  # from inside a coroutine
# Python 3.12+: asyncio.get_event_loop()     # deprecation warnings if no loop running
```

> [!warning] Don't mix sync and async carelessly
> Calling `time.sleep(n)` in an async function blocks the **entire event loop** — no other tasks run. Always use `await asyncio.sleep(n)`.

---

## Coroutines

```python
# A coroutine object is NOT the same as a function
coro = fetch_data("https://example.com")   # Creates coroutine object, doesn't run it!
# type(coro) → <class 'coroutine'>

# You MUST await it or schedule it as a task
await coro

# Calling a coroutine without await creates a coroutine object
# The coroutine will eventually be garbage collected with a warning
fetch_data("x")   # RuntimeWarning: coroutine was never awaited
```

### Awaitable types

| Type | Can `await`? | Creates task? |
|------|:------------:|:-------------:|
| Coroutine (`async def`) | ✅ Yes | ❌ No — runs inline |
| `asyncio.Task` | ✅ Yes | ✅ Already a task |
| `asyncio.Future` | ✅ Yes | ❌ Lower-level |
| Regular function | ❌ No | N/A |

---

## Tasks

> [!info] Tasks schedule a coroutine to run **concurrently** on the event loop
> Use `asyncio.create_task()` to run a coroutine in the background while continuing with other work.

```python
async def main():
    # Create two tasks — they run concurrently
    task1 = asyncio.create_task(fetch_data("https://api.example.com/a"))
    task2 = asyncio.create_task(fetch_data("https://api.example.com/b"))

    # Both tasks are now running in the background
    # Do other work while they execute
    await asyncio.sleep(0.5)

    # Wait for both to complete
    result1 = await task1
    result2 = await task2
    print(result1, result2)
```

```mermaid
sequenceDiagram
    participant Main as "main()"
    participant Loop as "Event Loop"
    participant T1 as "Task 1 (fetch A)"
    participant T2 as "Task 2 (fetch B)"
    Main->>Loop: create_task(T1)
    Main->>Loop: create_task(T2)
    Note over Main: T1 and T2 are now in the<br/>event loop's run queue
    Loop->>T1: start T1
    T1->>Loop: await asyncio.sleep()<br/>suspends T1
    Loop->>T2: start T2
    T2->>Loop: await asyncio.sleep()<br/>suspends T2
    Loop-->>T1: resume T1
    T1-->>Main: return result
    Loop-->>T2: resume T2
    T2-->>Main: return result
```

---

## await vs asyncio.gather

```python
# Sequential — each runs one after the other
async def sequential():
    a = await fetch_data("/a")     # 1s
    b = await fetch_data("/b")     # 1s
    # Total: ~2s

# Concurrent — all three run simultaneously
async def concurrent():
    results = await asyncio.gather(
        fetch_data("/a"),          # 1s
        fetch_data("/b"),          # 1s
        fetch_data("/c"),          # 1s
    )
    # Total: ~1s (not 3s)

# gather returns results in order
a_result, b_result, c_result = results

# Cancel all if one fails
try:
    results = await asyncio.gather(
        fetch_data("/a"),
        fetch_data("/b"),
        return_exceptions=False,    # Default — one failure cancels all
    )
except Exception:
    # All tasks are cancelled
    pass
```

> [!tip] Use `gather` for independent concurrent operations
> For dependent operations (result of one is needed by another), use sequential `await`. For independent work, use `create_task` or `gather`.

---

## asyncio.Queue

```python
# Producer-consumer pattern with asyncio.Queue

async def producer(queue: asyncio.Queue, n: int):
    for i in range(n):
        await queue.put(f"item_{i}")
        print(f"Produced item_{i}")
        await asyncio.sleep(0.1)
    await queue.put(None)           # Sentinel: signals end

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:            # Check for sentinel
            queue.task_done()
            break
        print(f"{name} consumed {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=10)
    prod = asyncio.create_task(producer(queue, 5))
    cons = asyncio.create_task(consumer(queue, "C1"))
    await prod                      # Wait for producer
    await queue.join()              # Wait until all items processed
    cons.cancel()                   # Stop consumer
```

---

## Async Context Managers

```python
# For async resources (connections, sessions, files)

class AsyncResource:
    async def __aenter__(self):
        print("Acquiring resource")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Releasing resource")
        await asyncio.sleep(0.1)

async def main():
    async with AsyncResource() as res:
        print("Using resource")
    # Resource is released automatically

# @contextmanager equivalent for async
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session():
    session = await create_session()
    try:
        yield session
    finally:
        await session.close()
```

---

## Async Iterators

```python
class AsyncCounter:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.limit:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)        # Simulate async work
        self.current += 1
        return self.current

async def main():
    async for x in AsyncCounter(5):
        print(x)                        # 1, 2, 3, 4, 5

# Async generator (Python 3.6+)
async def async_range(limit):
    for i in range(limit):
        await asyncio.sleep(0.1)
        yield i
```

---

## asyncio.Lock and Semaphore

```python
# asyncio.Lock — mutual exclusion in async code
lock = asyncio.Lock()

async def safe_update(resource_id):
    async with lock:                    # Only one coroutine at a time
        value = await get_value(resource_id)
        await set_value(resource_id, value + 1)

# asyncio.Semaphore — limit concurrency
sem = asyncio.Semaphore(5)             # Max 5 concurrent access

async def limited_request(url):
    async with sem:
        return await fetch_data(url)

# asyncio.gather with semaphore
async def crawl_many(urls):
    sem = asyncio.Semaphore(10)        # Max 10 concurrent requests
    async def bounded(url):
        async with sem:
            return await fetch_data(url)
    return await asyncio.gather(*[bounded(u) for u in urls])
```

---

## aiohttp Intro

```python
import aiohttp

async def fetch(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        return {"status": response.status, "url": url}

async def main():
    async with aiohttp.ClientSession() as session:
        urls = [
            "https://api.example.com/a",
            "https://api.example.com/b",
            "https://api.example.com/c",
        ]
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        print(results)

asyncio.run(main())
```

> [!tip] `aiohttp` is the standard async HTTP client
> Use it when you need many concurrent HTTP requests (scraping, API aggregation, microservices). For simpler use cases, `httpx` also supports async.

---

## Pitfalls

### Blocking the event loop

```python
async def bad():
    import time
    time.sleep(5)           # ❌ Blocks the ENTIRE event loop for 5 seconds
    # Use await asyncio.sleep(5) instead
```

### Forgetting to `await`

```python
async def main():
    fetch_data("/api")      # ❌ Creates coroutine object, doesn't run it!
    # RuntimeWarning: coroutine was never awaited
    result = await fetch_data("/api")  # ✅
```

### Not cancelling tasks on shutdown

```python
async def main():
    task = asyncio.create_task(worker())
    # On Ctrl+C or exception, task keeps running
    try:
        await asyncio.sleep(3600)
    finally:
        task.cancel()       # ✅ Proper cleanup
        try:
            await task
        except asyncio.CancelledError:
            pass
```

### Mixing asyncio and threading

`asyncio` coroutines are not thread-safe. Use `asyncio.run_coroutine_threadsafe()` to submit coroutines from other threads.

---

> [!question]- Interview Questions
>
> **Q: What's the difference between a coroutine and a task?**
> A: A coroutine is an awaitable function defined with `async def`. Creating a coroutine object (`fetch_data()`) doesn't schedule it. A task (`asyncio.create_task(coro)`) wraps the coroutine and schedules it on the event loop immediately. Tasks run concurrently with other tasks; raw coroutines are `await`ed inline (sequential).
>
> **Q: How does `asyncio.gather` work?**
> A: `gather` takes multiple awaitables, wraps each in a task, and runs them concurrently on the event loop. It returns a list of results in the same order as the inputs. If any awaitable raises, all others are cancelled (unless `return_exceptions=True`).
>
> **Q: What is the event loop?**
> A: The event loop is the core of asyncio. It maintains a queue of tasks and callbacks, and runs a loop checking for I/O readiness, timer expiry, and scheduled callbacks. When a coroutine does `await asyncio.sleep(n)`, it yields control back to the loop, which can run other tasks until the sleep completes.

---

## Cross-Links

- [[Python/02_Core/02_Concurrency_Parallelism]] for threading and multiprocessing comparison
- [[Python/02_Core/03_Network_Programming_HTTP]] for httpx async client
- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for async web applications
- [[Python/02_Core/04_Web_Scraping]] for async scraping patterns
- [[Python/03_Advanced/01_Async_Deep_Dive]] for event loop internals and advanced patterns
