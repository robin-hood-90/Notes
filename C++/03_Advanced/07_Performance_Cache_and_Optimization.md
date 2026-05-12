---
tags: [cpp, advanced, performance, cache, optimization, profiling, pgo, simd, restrictive-keyword]
aliases: ["Performance", "Cache Optimization", "SoA vs AoS", "SSO", "PGO", "Profiling"]
status: stable
updated: 2026-05-09
---

# Performance, Cache, and Optimization

> [!summary] Goal
> Master C++ performance optimization — cache-friendly data structures, compiler optimizations, profiling tools, and the key C++ features that impact performance. Write performance-critical code for game engines, embedded systems, and high-frequency trading.

## Table of Contents

1. [Cache-Friendly Data Structures](#cache-friendly-data-structures)
2. [Compiler Optimizations](#compiler-optimizations)
3. [Profiling and Measurement](#profiling-and-measurement)
4. [Pitfalls](#pitfalls)

---

## Cache-Friendly Data Structures

> [!info] CPU cache hierarchy
> Modern CPUs have L1 (~32KB, ~1ns latency), L2 (~256KB, ~3-5ns), L3 (~8-32MB, ~10-20ns), and main memory (~100ns). A cache miss is 10-50× slower than a cache hit. The most impactful optimization is writing code that maximizes cache utilization.

### SoA vs AoS — the single most impactful optimization

> [!info] SoA (Struct of Arrays) vs AoS (Array of Structs)
> AoS (`struct { float x, y, z; } pos[N]`) stores all members of each element together. SoA (`struct { float x[N], y[N], z[N]; }`) stores each member in a separate contiguous array. SoA is much more cache-friendly when you only need some members (e.g., only `x` for a transformation). This is critical for SIMD vectorization.

```cpp
// ❌ AoS — Array of Structs (cache-inefficient for single-field access)
struct Particle {
    float x, y, z;           // position
    float vx, vy, vz;        // velocity
    float mass;
    int active;
    uint32_t color;
};
std::vector<Particle> particles(100000);

void update_x() {
    // Only reads x — but loads the entire struct (36 bytes!)
    // Cache line contains 4 particles (64/36 ≈ 1.7), waste 30 bytes
    for (auto& p : particles) {
        p.x += p.vx * dt;   // Only uses x and vx
    }
}

// ✅ SoA — Struct of Arrays (cache-efficient)
struct Particles {
    std::vector<float> x, y, z;
    std::vector<float> vx, vy, vz;
    std::vector<float> mass;
    std::vector<int> active;
    std::vector<uint32_t> color;
};

void update_x(Particles& p) {
    // Only loads the two arrays needed — x and vx
    // Fits in cache — 16 elements per cache line (64/4 = 16 floats)
    for (size_t i = 0; i < p.x.size(); ++i) {
        p.x[i] += p.vx[i] * dt;
    }
}
```

### Hot/cold splitting

```cpp
// Cache-friendly: separate frequently-used data from rarely-used data
struct Entity {
    // Hot data (accessed every frame) — keep together, cache-friendly
    float x, y;
    float vx, vy;
    int health;
    
    // Cold data (rarely accessed) — put in a separate structure
    struct ColdData {
        std::string name;
        std::string description;
        std::vector<int> questLog;
    };
    std::unique_ptr<ColdData> cold;  // Heap allocated — only loaded when needed
};
```

### SSO — Small String Optimization

> [!info] SSO
> `std::string` typically stores the string inline without heap allocation for strings up to ~15 characters (sizeof depends on platform). Larger strings are heap-allocated. Checking with `.capacity()` reveals the SSO threshold. Prefer short strings when possible; use `std::string_view` for read-only access.

---

## Compiler Optimizations

### Key optimization flags

```bash
# -O0: No optimization, fastest compile, best for debugging
# -O1: Basic optimizations
# -O2: Standard optimizations (recommended for release)
# -O3: Aggressive (may increase code size, loop unrolling)
# -Os: Optimize for size
# -Ofast: -O3 + fast-math (may break IEEE compliance)

# Link-time optimization
g++ -flto -O2 file1.cpp file2.cpp    # Whole-program optimization

# Profile-guided optimization
g++ -fprofile-generate -O2 program.cpp -o program
./program  # Run with representative data
g++ -fprofile-use -O2 program.cpp -o program_fast
```

### restrict and __restrict

```cpp
// Tells the compiler the pointer is the ONLY reference to that memory
// Enables better optimization (no aliasing concerns)
void copy(int* __restrict__ dest, const int* __restrict__ src, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        dest[i] = src[i];  // Can vectorize — no aliasing concern
    }
}
```

### [[likely]] / [[unlikely]] (C++20)

```cpp
int process(int* ptr) {
    if (!ptr) [[unlikely]] {
        return -1;      // Arranged as the less-common branch
    }
    return *ptr;        // Common case is the fall-through path
}
```

### noexcept and performance

`noexcept` functions allow the compiler to generate smaller code (no exception-handling bookkeeping). It also enables move semantics in std::vector (vector moves elements if their move is noexcept; copies if not).

---

## Profiling and Measurement

> [!info] Profiling
> Measure before optimizing. Without profiling, you're guessing. Use: perf (Linux), Intel VTune, AMD uProf, or Google Benchmark for micro-benchmarks.

```cpp
#include <benchmark/benchmark.h>

static void BM_VectorPushBack(benchmark::State& state) {
    for (auto _ : state) {
        std::vector<int> v;
        v.reserve(state.range(0));
        for (int i = 0; i < state.range(0); ++i) {
            v.push_back(i);
        }
    }
}
BENCHMARK(BM_VectorPushBack)->Range(8, 8<<10);

BENCHMARK_MAIN();
```

```bash
# Linux perf
perf stat ./program                         # Count cycles, instructions, cache misses
perf record -g ./program                    # Profile with call-graph
perf report                                 # Interactive analysis

# Cache miss analysis with cachegrind
valgrind --tool=cachegrind ./program
cg_annotate cachegrind.out.XXXXX

# Intel vtune
amplxe-cl -collect hotspots ./program
amplxe-cl -collect cache-misses ./program
```

---

## Pitfalls

### Profiling -O0 code

Profiling debug builds (`-O0`) is misleading. Optimization changes everything: inlining, register allocation, loop unrolling. Always profile with the optimization level you'll ship (`-O2` or `-O3`).

### std::unordered_map vs vector for small collections

For < 50 elements, a `std::vector` with linear search is often faster than `std::unordered_map` — the vector is cache-friendly, while the hash table requires multiple indirections. Measure, don't assume.

### False sharing in multithreaded code

Two threads writing to different variables on the same cache line cause 10-100× slowdown (each write invalidates the other's cache). Fix: pad to 64-byte boundaries:

```cpp
struct alignas(64) Counter {
    int value;           // Each Counter is on its own cache line
};
```

### Over-optimization

The best code is simple and correct. Optimize only the 5-10% of code that profiling identifies as hot. The rest should be written for clarity and maintainability.

---

> [!question]- Interview Questions
>
> **Q: What is the difference between AoS and SoA?**
> A: AoS (Array of Structs) stores one object's all members contiguously. SoA (Struct of Arrays) stores each member in a separate array. SoA is more cache-friendly when you access only some members (e.g., only positions). SoA also enables SIMD vectorization naturally. AoS is simpler to read and write. Choose based on access patterns.
>
> **Q: What is SSO and how does it affect std::string performance?**
> A: Small String Optimization stores short strings (typically < 16 chars) inline without heap allocation. This avoids the cost of malloc/free for the vast majority of strings. Use short strings where possible — they're allocation-free. Use `std::string_view` for read-only access to avoid copying.
>
> **Q: What is false sharing and how do you prevent it?**
> A: False sharing occurs when two threads write to different variables on the same cache line (64 bytes). The cache coherence protocol invalidates the cache line on each write, even though the threads use different data. Fix: align shared variables to 64 bytes (cache line size) so each thread's variable is on its own cache line.
>
> **Q: What profiling tools would you use for a C++ application?**
> A: Linux perf for CPU/hardware-counter profiling, Valgrind (cachegrind/callgrind) for detailed cache and call-graph analysis, Intel VTune/AMD uProf for comprehensive CPU optimization, Google Benchmark for micro-benchmarks. Always profile with release-level optimization (-O2 or higher).

---

## Cross-Links

- [[C++/02_Core/02_STL_Containers_Deep_Dive]] for container performance
- [[C++/02_Core/07_Atomics_Lock_Free_and_Memory_Model]] for cache effects on atomics
- [[C++/03_Advanced/08_Game_Engine_and_Driver_Dev]] for game-specific performance
- [[C++/01_Foundations/05_Move_Semantics_and_Value_Categories]] for move performance
- [[C++/04_Playbooks/03_Debug_Performance_Regressions]] for performance debugging
