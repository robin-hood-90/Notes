---
tags: [rust, advanced, allocator, global-allocator, memory, jemalloc]
aliases: ["Global Allocator", "Allocation", "Memory Allocators", "jemalloc", "mimalloc"]
status: stable
updated: 2026-05-03
---

# Global Allocators and Allocation

> [!summary] Goal
> Replace the default allocator and understand how Rust manages heap memory across different workloads.

## Table of Contents

1. [Why Global Allocators Matter](#why-global-allocators-matter)
2. [Default Allocator](#default-allocator)
3. [`#[global_allocator]`](#global_allocator)
4. [Implementing `GlobalAlloc`](#implementing-globalalloc)
5. [Allocation Profiling](#allocation-profiling)
6. [Pitfalls](#pitfalls)

---

## Why Global Allocators Matter

The global allocator is responsible for every heap allocation in a Rust program:
- `Box::new()`, `Vec::push()`, `String::from()`, `Rc::new()`
- `Arc::new()`, `HashMap` insertions
- All FFI allocations that go through Rust

```mermaid
flowchart LR
    A[Rust program] --> B[Box::new]
    A --> C[Vec::push]
    A --> D[String::from]
    A --> E[Arc::new]
    B --> F[#[global_allocator]]
    C --> F
    D --> F
    E --> F
    F --> G[os allocator / jemalloc / mimalloc]
```

> [!tip] Definition
> **`GlobalAlloc`**: the trait that defines how heap memory is allocated and deallocated. The `#[global_allocator]` static sets the program-wide allocator.

---

## Default Allocator

| Platform | Default allocator |
|----------|------------------|
| Linux/macOS | System allocator (`malloc`/`free`) |
| Windows | System allocator (`HeapAlloc`) |
| wasm32 | None (must provide one) |
| `no_std` | None (must provide one) |

The system allocator is fine for most applications. Replace it only when:
- Benchmarks show allocator bottlenecks
- You need specific performance characteristics (e.g., jemalloc for multi-threaded workloads)
- You're on a platform without a default allocator

---

## `#[global_allocator]`

### Using jemalloc

```toml
[dependencies]
tikv-jemallocator = "0.5"
```

```rust
use tikv_jemallocator::Jemalloc;

#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;

fn main() {
    // All allocations now go through jemalloc
    let v = vec![1, 2, 3];
}
```

### Using mimalloc

```toml
[dependencies]
mimalloc = "0.1"
```

```rust
use mimalloc::MiMalloc;

#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

fn main() {
    let v = vec![0u8; 1024];
}
```

### Comparison

| Allocator | Best for | Fragmentation | Multi-threaded | Speed |
|-----------|----------|--------------|----------------|-------|
| System (glibc) | General | Moderate | Good | Baseline |
| jemalloc | Multi-threaded, large heaps | Low | Excellent | Fast |
| mimalloc | Fast allocation/deallocation | Low | Very good | Very fast |
| snmalloc | Message passing workloads | Low | Excellent | Very fast |

---

## Implementing `GlobalAlloc`

```rust
use std::alloc::{GlobalAlloc, Layout};
use std::sync::atomic::{AtomicUsize, Ordering};

struct CounterAllocator;

unsafe impl GlobalAlloc for CounterAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        // Forward to system allocator
        let ptr = std::alloc::System.alloc(layout);
        ALLOC_COUNT.fetch_add(1, Ordering::Relaxed);
        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        std::alloc::System.dealloc(ptr, layout);
    }
}

#[global_allocator]
static ALLOCATOR: CounterAllocator = CounterAllocator;

static ALLOC_COUNT: AtomicUsize = AtomicUsize::new(0);
```

### The `Layout` type

```rust
pub struct Layout {
    size_: usize,
    align_: usize,  // must be a power of 2
}

impl Layout {
    pub fn new<T>() -> Layout { /* size_of::<T>(), align_of::<T>() */ }
    pub fn array<T>(n: usize) -> Result<Layout, LayoutErr> {
        // size = n * size_of::<T>(), aligned to align_of::<T>()
    }
}
```

---

## Allocation Profiling

### Using `dhat` for heap profiling

```toml
[dependencies]
dhat = "0.3"
```

```rust
use dhat::{Dhat, DhatAllocator};

#[global_allocator]
static ALLOC: DhatAllocator = DhatAllocator;

fn main() {
    let _dhat = Dhat::start_heap_profiling();
    // run your code...
    // dhat writes a JSON file: dhat-heap.json
}
```

View with: `dhat-view dhat-heap.json` or online at https://nnethercote.github.io/dh-view/

### Using jemalloc stats

```rust
use tikv_jemalloc_ctl::stats;

fn print_stats() {
    let allocated = stats::allocated::read().unwrap();
    let active = stats::active::read().unwrap();
    println!("allocated: {} MB, active: {} MB", allocated / 1024 / 1024, active / 1024 / 1024);
}
```

---

## Pitfalls

### Error on double `#[global_allocator]`

```rust
#[global_allocator]
static A: Jemalloc = Jemalloc;

#[global_allocator]  // ERROR: cannot define multiple global allocators
static B: MiMalloc = MiMalloc;
```

**Fix**: only one `#[global_allocator]` per program.

### Performance regression after changing allocator

jemalloc may be slower than the system allocator for single-threaded, short-lived programs. Always benchmark before switching.

### Custom allocator must be `Send + Sync`

```rust
#[global_allocator]
static ALLOC: MyAlloc = MyAlloc;  // MyAlloc must be Sync (used from multiple threads)
```

---

> [!question]- Interview Questions
>
> **Q: What is `#[global_allocator]`?**
> A: It sets the program-wide heap allocator. All `Box`, `Vec`, `String`, etc. allocations go through this allocator.
>
> **Q: When would you replace the default allocator?**
> A: When profiling shows allocator bottlenecks. jemalloc for multi-threaded workloads, mimalloc for fast allocation/deallocation, or custom allocators for tracing/profiling.
>
> **Q: What does `Layout` represent?**
> A: The size and alignment requirements for an allocation. Created from `Layout::new::<T>()` or `Layout::array::<T>(n)`.

---

## Cross-Links

- [[Rust/03_Advanced/09_no_std_and_Embedded_Rust]] for no_std allocator setup
- [[Rust/03_Advanced/03_Performance_Profiling_and_Allocation]] for profiling allocation hotspots
- [[Rust/03_Advanced/07_Memory_Layout_and_repr_Attributes]] for alignment constraints

---

## References

- [std::alloc::GlobalAlloc](https://doc.rust-lang.org/std/alloc/trait.GlobalAlloc.html)
- [The Rust Book: Global Allocator](https://doc.rust-lang.org/stable/embedded-book/static-allocation.html)
- [tikv-jemallocator](https://docs.rs/tikv-jemallocator/)
- [mimalloc-rust](https://docs.rs/mimalloc/)
- [dhat crate](https://docs.rs/dhat/)
