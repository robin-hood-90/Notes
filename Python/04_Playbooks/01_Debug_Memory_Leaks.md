---
tags: [python, playbook, memory, leaks, tracemalloc, objgraph, gc, py-spy]
aliases: ["Debug Memory Leaks", "Memory Profiling", "tracemalloc", "objgraph", "gc module"]
status: stable
updated: 2026-05-29
---

# Playbook: Debug Memory Leaks and Performance

> [!summary] Goal
> Diagnose and fix Python memory issues — use `tracemalloc`, `objgraph`, the `gc` module, and `py-spy` to find leaks, slow allocations, and reference cycles.

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [tracemalloc](#tracemalloc)
3. [objgraph](#objgraph)
4. [gc Module](#gc-module)
5. [Common Leak Patterns](#common-leak-patterns)
6. [Pitfalls](#pitfalls)

---

## Quick Diagnosis

```bash
# 1. Check memory usage
ps aux | grep python
# or: htop, sort by MEM%

# 2. Enable GC debug
export PYTHONMALLOC=debug
python myapp.py

# 3. tracemalloc (no install)
python -X tracemalloc myapp.py

# 4. py-spy (sampling profiler)
py-spy record -o profile.svg -- python myapp.py

# 5. Show top objects
python -c "
import gc
for obj in gc.get_objects():
    if isinstance(obj, dict) and len(obj) > 1000:
        print(type(obj), len(obj))
"
```

---

## tracemalloc

```python
import tracemalloc

# Start with frame tracking
tracemalloc.start(25)                    # 25 frames of stack trace

# Take snapshot
snapshot = tracemalloc.take_snapshot()

# ... run your code ...
large_data = [object() for _ in range(100_000)]

# Take another snapshot
snapshot2 = tracemalloc.take_snapshot()

# Compare
stats = snapshot2.compare_to(snapshot, "lineno")
for stat in stats[:10]:
    print(stat)
    # test.py:10: size=7.8 MiB (+7.8 MiB), count=100000 (+100000), average=82 B
```

---

## objgraph

```python
# pip install objgraph
import objgraph

# Show most common types
objgraph.show_most_common_types(limit=20)
# dict           15000
# list           12000
# tuple          8000
# ...

# Show growth
objgraph.show_growth(limit=10)

# Find reference chain to an object (why is it alive?)
objgraph.show_backrefs(
    leaky_object,
    max_depth=10,
    filename="refs.png",
)

# Find objects that reference a specific type
objgraph.by_type("MyClass")
```

---

## gc Module

```python
import gc

# Enable debug
gc.set_debug(gc.DEBUG_SAVEALL | gc.DEBUG_LEAK)

# Force collection
collected = gc.collect()
print(f"GC collected {collected} objects")

# Find unreachable but uncollectable objects
gc.garbage          # Objects with __del__ that form cycles

# Count objects by type
for obj in gc.get_objects():
    if type(obj) is dict and len(obj) > 100:
        print(f"Large dict: {len(obj)} items")

# Track specific objects
obj_id = id(leaky_object)
for _ in range(10):
    # Check if object still exists
    if any(id(o) == obj_id for o in gc.get_objects()):
        print("Object still alive")
```

---

## Common Leak Patterns

### 1. Caches without eviction

```python
# ❌ Cache grows forever
_results_cache: dict[str, bytes] = {}

def get_data(key: str) -> bytes:
    if key not in _results_cache:
        _results_cache[key] = fetch_expensive(key)
    return _results_cache[key]

# ✅ Use LRU or TTL
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_data(key: str) -> bytes:
    return fetch_expensive(key)
```

### 2. Closures holding large objects

```python
def create_handler():
    large_data = load_giant_file()          # Held in closure
    def handler(event):
        return process(event, large_data)   # Closure keeps reference
    return handler

# ✅ Explicitly release when done
def create_handler():
    large_data = load_giant_file()
    def handler(event):
        return process(event, large_data)
    handler.cleanup = lambda: large_data.clear()
    return handler
```

### 3. Circular references with `__del__`

```python
class Node:
    def __init__(self):
        self.ref = None
    def __del__(self):
        print(f"Deleting {id(self)}")

a = Node(); b = Node()
a.ref = b; b.ref = a

# Without __del__, GC collects the cycle
# WITH __del__, GC can't collect — becomes garbage
gc.collect()
gc.garbage  # [<Node>, <Node>] — never freed!
```

### 4. Global state accumulation

```python
# ❌ Module-level list grows unbounded
all_requests = []
def log_request(r):
    all_requests.append(r)

# ✅ Use bounded structure or no global state
```

### 5. Unclosed file handles / connections

```python
# ❌ Forgets to close
def process():
    f = open("large_file.txt")
    data = f.read()
    # f.close() never called — file handle leak

# ✅ Context manager
def process():
    with open("large_file.txt") as f:
        data = f.read()
```

---

## Pitfalls

### `gc.set_debug` causes slowdown

Only enable in development. `gc.DEBUG_SAVEALL` keeps all collected objects alive in `gc.garbage`.

### `tracemalloc` overhead

`tracemalloc.start(25)` adds significant memory overhead (storing 25 frames per allocation). Lower the frame count for production.

### `objgraph.show_backrefs` on large objects

Rendering image files for objects with thousands of references can be very slow or hang. Limit with `max_depth` and `too_many`.

### `__del__` + cycles = permanent leak

Objects with `__del__` that form cycles are **never** freed. Avoid `__del__` in objects that may form cycles.

---

> [!question]- Interview Questions
>
> **Q: How do you find a memory leak in a running Python process?**
> A: Use `tracemalloc` to compare snapshots and identify growing allocations. Use `objgraph.show_growth()` to track object type growth over time. Use `gc.get_objects()` to inspect what's alive. For production, use `py-spy` to sample, and `PYTHONMALLOC=malloc` to disable pymalloc for better ASan detection.
>
> **Q: What causes circular garbage that can't be collected?**
> A: Objects with `__del__` methods that form reference cycles. The GC can detect cycles, but if a cycle has a `__del__`, the GC doesn't know the order to call destructors safely. These objects are stored in `gc.garbage` and never freed. Avoid `__del__` in classes that may form cycles.
>
> **Q: How do you debug "memory not freed"?**
> A: (1) Check `gc.garbage` for uncollectable cycles. (2) Use `tracemalloc` with snapshots to find growing allocations. (3) Use `objgraph.show_backrefs()` on leaking objects to see why they're retained. (4) Check for caches without eviction, unclosed files, and global state accumulation.

---

## Cross-Links

- [[Python/02_Core/01_CPython_Internals]] for GC and memory model
- [[Python/03_Advanced/02_Performance_Profiling]] for CPU profiling
- [[Python/02_Core/07_NumPy_Deep_Dive]] for NumPy memory
