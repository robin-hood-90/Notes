---
tags: [python, playbook, concurrency, debugging, deadlocks, race-conditions, asyncio, multiprocessing]
aliases: ["Debug Concurrency Issues", "Deadlocks", "Race Conditions", "Async Debugging"]
status: stable
updated: 2026-05-29
---

# Playbook: Debug Concurrency Issues

> [!summary] Goal
> Diagnose and fix concurrency problems — race conditions, deadlocks, asyncio debugging, multiprocessing pickling errors, and signal safety.

## Table of Contents

1. [Race Conditions](#race-conditions)
2. [Deadlocks](#deadlocks)
3. [Async Debugging](#async-debugging)
4. [Multiprocessing Pickling](#multiprocessing-pickling)
5. [Pitfalls](#pitfalls)

---

## Race Conditions

```python
import threading

# ❌ Race condition — += is not atomic
counter = 0
def increment():
    global counter
    for _ in range(100_000):
        counter += 1          # Read → increment → write (not atomic!)

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # Not 1_000_000!

# ✅ Fix with Lock
lock = threading.Lock()
def safe_increment():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1
```

### Detection

```bash
# 1. Enable race detection in tests
python -m pytest tests/ -v

# 2. Run with TSan (ThreadSanitizer) — detects data races
# Python 3.12+: ./configure --with-thread-sanitizer
# Or use GCC/Clang with -fsanitize=thread on C extensions

# 3. Stress testing
import random, threading, time

def stress_test(func, threads=10, iterations=1000):
    errors = []
    lock = threading.Lock()
    def worker():
        for _ in range(iterations):
            try:
                func()
            except Exception as e:
                with lock:
                    errors.append(e)
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts: t.start()
    for t in ts: t.join()
    print(f"Errors: {len(errors)}")
```

---

## Deadlocks

```python
import threading

# ❌ Deadlock — lock ordering violation
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread_1():
    with lock_a:
        time.sleep(0.1)
        with lock_b:              # Needs lock_b, held by thread_2
            pass

def thread_2():
    with lock_b:
        time.sleep(0.1)
        with lock_a:              # Needs lock_a, held by thread_1
            pass

# Both threads block forever → DEADLOCK
```

### Detection

```python
import threading, time, sys

# Deadlock detection with timeout
lock_a = threading.Lock()
lock_b = threading.Lock()

def try_lock(lock, timeout=2):
    """Attempt to acquire a lock with timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if lock.acquire(blocking=False):
            return True
        time.sleep(0.01)
    return False

def cautious_thread_1():
    with lock_a:
        if not try_lock(lock_b):
            print("Potential deadlock detected!")
            return
        lock_b.release()

# Or use with statement timeout (Python 3.12+)
# threading.SimpleLock().acquire(timeout=5)
```

```bash
# Debugging deadlocks
# 1. Ctrl+Break / SIGQUIT on Linux
kill -3 PID           # Prints thread stacks

# 2. GDB
gdb python PID
thread apply all bt   # All thread backtraces

# 3. Python 3.12+: faulthandler
python -X faulthandler script.py
# Ctrl+\ sends SIGQUIT, prints all thread stacks
```

---

## Async Debugging

```python
import asyncio

# 1. Enable debug mode
asyncio.run(main(), debug=True)

# 2. Check for blocking calls
async def bad():
    import time
    time.sleep(1)                    # Blocks event loop — debug warns
    await asyncio.sleep(1)           # ✅

# 3. Detect unawaited coroutines
async def main():
    fetch_data()                     # ❌ Coroutine created but not awaited
    # Debug: "coroutine was never awaited"

# 4. Inspect running tasks
async def inspect():
    for task in asyncio.all_tasks():
        print(f"Task: {task.get_name()}, done={task.done()}")
        if task.done() and not task.cancelled():
            exc = task.exception()
            if exc:
                print(f"  Exception: {exc}")

# 5. Timeout protection
async def fetch_with_timeout(url):
    try:
        async with asyncio.timeout(5):          # Python 3.12+
            return await fetch(url)
    except TimeoutError:
        return None
```

### Common async bugs

```python
# ❌ Calling sync code in async without offloading
async def handler():
    result = cpu_intensive()           # Blocks event loop!
    return result

# ✅ Offload to thread pool
async def handler():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, cpu_intensive)
    return result

# ❌ Creating tasks and forgetting to await
async def main():
    asyncio.create_task(worker())      # Fire and forget
    # Task may be cancelled when main() exits!

# ✅ Keep reference or use gather
async def main():
    task = asyncio.create_task(worker())
    await task                         # Wait for completion
```

---

## Multiprocessing Pickling

```python
import multiprocessing as mp

# ❌ Can't pickle lambdas
def bad():
    with mp.Pool() as pool:
        pool.map(lambda x: x * 2, [1, 2, 3])   # AttributeError

# ✅ Use named functions
def double(x): return x * 2
pool.map(double, [1, 2, 3])

# ❌ Can't pickle local classes
def outer():
    class Inner:
        pass
    pool.map(Inner(), [1])             # AttributeError

# ❌ Can't pickled nested functions
def outer():
    def inner(x): return x
    pool.map(inner, [1])              # AttributeError

# ✅ Use dill or cloudpickle for complex cases
import dill
def double(x): return x * 2
pool = mp.Pool()
pool.map(dill.dumps, [double])         # dill can pickle more types
```

### Debugging pickling errors

```python
import pickle, traceback

try:
    pickle.dumps(some_object)
except pickle.PicklingError:
    traceback.print_exc()
    # Example: "Can't pickle <function <lambda> at 0x...>"
```

---

## Pitfalls

### GIL doesn't protect against race conditions

The GIL protects CPython internals, NOT your data. `x += 1` is still a race even with the GIL.

### Thread vs async deadlocks

`threading` deadlocks are permanent (OS-level lock). `asyncio` deadlocks can sometimes be resolved by the event loop switching tasks.

### `asyncio.Task` cancellation

A cancelled task raises `CancelledError` at the next `await`. If the task doesn't handle it, resources leak. Always wrap cleanup in `try/finally`.

### Pickling C extensions

Many C extensions (like `_socket`, `_ssl`) can't be pickled. This limits what you can send between processes.

### Signal safety

Signal handlers run in the main thread. Avoid locks, complex operations, and async calls in signal handlers.

---

> [!question]- Interview Questions
>
> **Q: How do you detect a deadlock in Python?**
> A: Send SIGQUIT (Ctrl+\ or `kill -3 PID`) to print all thread stacks. Look for threads waiting on the same lock at different lines. Use `threading.Lock.acquire(timeout=5)` to fail instead of blocking forever. For async, enable debug mode to see task states.
>
> **Q: How do you debug async code?**
> A: Enable debug mode (`asyncio.run(main(), debug=True)`), which warns about blocking calls, slow coroutines, and unawaited tasks. Use `asyncio.all_tasks()` to inspect running tasks. Use `asyncio.timeout()` or `asyncio.wait_for()` to prevent hangs. Check for synchronous I/O or CPU work that blocks the event loop.
>
> **Q: Why can't you send a lambda to a multiprocessing.Pool?**
> A: `multiprocessing` serialises arguments using `pickle`. Lambdas, nested functions, and local classes can't be pickled because pickle serialises by name reference, and these objects don't have a module-level qualified name. Use named module-level functions, or use `dill`/`cloudpickle` for complex objects.

---

## Cross-Links

- [[Python/02_Core/02_Concurrency_Parallelism]] for threading patterns
- [[Python/03_Advanced/01_Async_Deep_Dive]] for async patterns
- [[Python/02_Core/01_CPython_Internals]] for GIL details
- [[Python/04_Playbooks/03_Production_Readiness]] for production monitoring
