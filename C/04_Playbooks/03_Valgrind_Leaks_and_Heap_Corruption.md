---
tags: [c, playbook, valgrind, memcheck, cachegrind, callgrind, heap-profiling]
aliases: ["Valgrind", "Memcheck", "Cachegrind", "Callgrind", "Massif", "Helgrind"]
status: stable
updated: 2026-05-09
---

# Playbook: Valgrind for Memory and Performance Analysis

> [!summary] Goal
> Use Valgrind to detect memory leaks, invalid memory accesses, and profile cache/CPU performance. Valgrind runs programs on a synthetic CPU, intercepting every memory access — it's slower but far more thorough than any other tool.

## Table of Contents

1. [Valgrind Tools Overview](#valgrind-tools-overview)
2. [Memcheck — Memory Errors](#memcheck-memory-errors)
3. [Cachegrind — Cache Profiling](#cachegrind-cache-profiling)
4. [Massif — Heap Profiling](#massif-heap-profiling)
5. [Helgrind — Race Detection](#helgrind-race-detection)
6. [Pitfalls](#pitfalls)

---

## Valgrind Tools Overview

> [!info] Valgrind
> Valgrind runs your program on a **synthetic CPU** (just-in-time translation). It intercepts every memory access, function call, and instruction. This gives it perfect knowledge of your program's behavior — at the cost of 5-20× slowdown. Always test with `-g -O0` first, then `-O1` (higher optimization may confuse Valgrind).

| Tool | Flag | Purpose | Slowdown |
|------|:----:|---------|:--------:|
| **Memcheck** | `--tool=memcheck` (default) | Memory errors, leaks | 10-20× |
| **Cachegrind** | `--tool=cachegrind` | Cache misses, branch prediction | 5-10× |
| **Callgrind** | `--tool=callgrind` | Call graph, function costs | 5-10× |
| **Massif** | `--tool=massif` | Heap memory usage over time | 10-20× |
| **Helgrind** | `--tool=helgrind` | POSIX thread data races | 10-50× |

---

## Memcheck — Memory Errors

```bash
gcc -g -O0 program.c -o program         # Compile with debug, no optimization
valgrind --leak-check=full --show-leak-kinds=all ./program

# More verbose (recommended for first run)
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./program
```

### Invalid write (buffer overflow)

```c
void invalid_write(void) {
    int *arr = malloc(5 * sizeof(int));
    arr[5] = 42;                   // ❌ Invalid write — past allocation
    free(arr);
}

// Valgrind output:
// ==12345== Invalid write of size 4
// ==12345==    at 0x10915E: invalid_write (example.c:3)
// ==12345==  Address 0x4a2c0d4 is 0 bytes after a block of size 20 alloc'd
// ==12345==    at 0x...: malloc
// ==12345==    by 0x10914F: invalid_write (example.c:2)
```

### Use-after-free

```c
void use_after_free(void) {
    int *p = malloc(10);
    free(p);
    p[0] = 42;                    // ❌ Writing to freed memory
}

// Valgrind output:
// ==12346== Invalid write of size 4
// ==12346==    at 0x1091A5: use_after_free (example.c:4)
// ==12346==  Address 0x4a2c0a0 is 0 bytes inside a block of size 10 free'd
// ==12346==    at 0x...: free
// ==12346==    by 0x1091A0: use_after_free (example.c:3)
```

### Memory leak

```c
void leak(void) {
    int *p = malloc(100);         // ❌ Never freed
}

// Valgrind output:
// ==12347== 100 bytes in 1 blocks are definitely lost in loss record 1 of 1
// ==12347==    at 0x...: malloc
// ==12347==    by 0x1091B5: leak (example.c:2)
```

### Uninitialized value

```c
int add(void) {
    int x;                        // Not initialized
    return x + 5;                 // ❌ Conditional jump depends on uninitialized value
}

// Valgrind output:
// ==12348== Conditional jump or move depends on uninitialised value(s)
// ==12348==    at 0x1091C8: add (example.c:3)
```

### Suppression files

```bash
# Generate a suppression file for known false positives
valgrind --gen-suppressions=all ./program 2> suppressions.txt

# Use suppression file
valgrind --suppressions=suppressions.txt ./program
```

---

## Cachegrind — Cache Profiling

```bash
gcc -g -O2 program.c -o program
valgrind --tool=cachegrind ./program

# Output: cachegrind.out.PID
# Analyze with:
cg_annotate cachegrind.out.12345
```

Cachegrind measures L1 data cache, L1 instruction cache, and last-level cache (LLC) misses:

```bash
# cg_annotate output:
# Ir (instructions), I1mr (L1 instruction misses), D1mr (L1 data read misses)
# DLmr (LL data read misses), Bc (conditional branches), Bcm (branch mispredictions)
#
# Ir        I1mr   D1mr   DLmr   file:function
# 500,000   2,000  10,000 5,000  matrix.c:multiply

# High D1mr/DLmr: poor cache locality — restructure data access
# High Bcm: unpredictable branches — use likely/unlikely hints
```

---

## Massif — Heap Profiling

```bash
gcc -g -O0 program.c -o program
valgrind --tool=massif ./program

# Output: massif.out.PID
# Visualize with:
ms_print massif.out.12345

# Tune snapshot granularity:
valgrind --tool=massif --time-unit=B   # Bytes between snapshots
valgrind --tool=massif --time-unit=ms  # Milliseconds between snapshots
```

```bash
# ms_print output:
#   MB
# 3.28^                                                    #
#     |                                                    #
#     |                                                    #
#     |                                                    #
#     |                                                    #
#     |                                                    :
#     |                                                    ::
#     |                                          @@@@@@@@::::
#     |                                          @        ::::
#     |                                          @        ::::
#   0 +------------------------------------------------------→s
#      0                                                        27.64
#
# Shows heap usage over time. Peaks indicate allocation bursts.
# Flat segments between peaks: no deallocation — potential leaks.
```

---

## Helgrind — Race Detection

```bash
gcc -g -O0 -lpthread program.c -o program
valgrind --tool=helgrind ./program

# Detects data races (threads accessing shared data without synchronization)
# Output:
# ==12349== Possible data race during write of size 4 at 0x... by thread #3
# ==12349==    at worker (example.c:6)
# ==12349==  This conflicts with a previous write of size 4 by thread #2
# ==12349==    at worker (example.c:6)
```

---

## Pitfalls

### Valgrind is slow

10-20× slowdown means it's for testing, not production. Use Valgrind in CI for regression testing. The slower it is, the more thorough (Memcheck vs Cachegrind).

### Optimization masks some bugs

Valgrind works best with `-O0`. Higher optimization can eliminate uninitialized variable usage or reorder instructions in ways that confuse Valgrind. Always test with `-O0` first, then `-O1`.

### False positives

Some well-known allocators and libraries trigger harmless Valgrind warnings. Use suppression files to filter them. Check online for standard suppressions for your libraries.

---

## Cross-Links

- [[C/02_Core/06_Undefined_Behavior_and_Memory_Safety]] for UB sources
- [[C/04_Playbooks/01_Debug_Segfaults_and_Invalid_Memory_Access]] for crash debugging
- [[C/04_Playbooks/02_Use_Sanitizers_ASan_UBSan_TSan]] for sanitizers (faster alternative)
- [[C/03_Advanced/08_Performance_Profiling_and_Optimization]] for perf profiling
- [[C/02_Core/03_Error_Handling]] for memory allocation error handling
