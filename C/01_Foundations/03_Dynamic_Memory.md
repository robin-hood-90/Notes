---
tags: [c, foundations, dynamic-memory, malloc, free, arena-allocator, memory-pool, alignment]
aliases: ["Dynamic Memory", "malloc", "free", "calloc", "realloc", "Memory Allocator", "Arena Allocator"]
status: stable
updated: 2026-05-09
---

# Dynamic Memory: malloc, free, and Custom Allocators

> [!summary] Goal
> Master dynamic memory allocation in C — from standard malloc/free internals to building custom arena allocators for performance-critical and OS development scenarios.

## Table of Contents

1. [Standard Allocation API](#standard-allocation-api)
2. [How malloc Works Internally](#how-malloc-works-internally)
3. [Common malloc Patterns](#common-malloc-patterns)
4. [Custom Arena Allocators](#custom-arena-allocators)
5. [Debugging Memory Issues](#debugging-memory-issues)
6. [Pitfalls](#pitfalls)

---

## Standard Allocation API

```c
#include <stdlib.h>
```

> [!info] malloc
> `malloc(size_t size)` allocates `size` bytes from the heap and returns a pointer to the start of the allocation. The memory is **not initialized** — its contents are indeterminate. Returns `NULL` on failure (size too large, out of memory).

```c
void *malloc(size_t size);      // Allocate uninitialized memory
void *calloc(size_t num, size_t size);  // Allocate + zero-initialize
void *realloc(void *ptr, size_t new_size);  // Resize existing allocation
void free(void *ptr);           // Deallocate

// Examples
int *arr = malloc(10 * sizeof(int));   // 40 bytes on 32-bit, uninitialized
int *zarr = calloc(10, sizeof(int));   // 40 bytes, all zeros

arr = realloc(arr, 20 * sizeof(int));  // Resize to 80 bytes (preserves first 10)

free(arr);   // Must be called exactly once per malloc'd pointer
```

### Allocation failure handling

```c
// malloc can return NULL — always check on large allocations
int *data = malloc(100 * sizeof(int));
if (!data) {
    fprintf(stderr, "malloc failed\n");
    exit(EXIT_FAILURE);
}
// ... use data ...
free(data);

// calloc can also fail — same pattern
struct large *p = calloc(1, sizeof(struct large));
if (!p) { /* handle error */ }
```

### malloc vs calloc vs realloc

| Function | Initialization | Use case |
|----------|:-------------:|----------|
| `malloc(n)` | **Uninitialized** (garbage values) | Overwriting immediately |
| `calloc(n, sz)` | **Zero-filled** | Sensitive data, sparse arrays |
| `realloc(p, n)` | **Preserves** first min(old,new) bytes | Growing/shrinking buffers |

---

## How malloc Works Internally

```mermaid
flowchart TD
    A["malloc(32) called"] --> B{Small allocation<br/>(< 128 KB)?}
    B -->|"Yes"| C["Check free list for<br/>suitable chunk"]
    B -->|"No (large)"| D["mmap: anonymous<br/>memory mapping"]
    C --> E{Found chunk?}
    E -->|"Yes, exact or split"| F["Return chunk to caller"]
    E -->|"No"| G["sbrk/brk: extend heap"]
    G --> F
    D --> H["mmap returns page-aligned<br/>memory, freed with munmap"]
```

### The free list

> [!info] Free list
> The heap is a linked list of **free chunks** and **allocated chunks**. Each chunk has a header (size, flags, next/prev pointers). `malloc` searches the free list for a chunk large enough. `free` returns the chunk to the free list and may coalesce adjacent free chunks.

```c
// Simplified chunk structure (actual glibc malloc is more complex)
struct chunk {
    size_t size;                // Size of this chunk (including header)
    struct chunk *next;         // Free list pointer
    struct chunk *prev;         // Free list pointer
    // ... user data follows ...
};
```

### Alignment guarantees

```c
// malloc always returns memory aligned to at least 16 bytes (64-bit)
// Suitable for any data type, including SIMD types

// For over-aligned types (C11):
#include <stdlib.h>
alignas(64) int cache_aligned_arr[1024];       // Stack with 64-byte alignment

// Heap with alignment:
int *aligned = aligned_alloc(64, 1024 * sizeof(int));  // C11, 64-byte aligned
```

### sbrk and brk

```c
// Low-level heap control (not used directly in practice)
#include <unistd.h>

void *sbrk(intptr_t increment);    // Increase/decrease heap by increment
int brk(void *addr);               // Set heap break to absolute address

// These are what malloc uses internally to grow the heap
// Use sbrk(0) to find current heap break
void *heap_end = sbrk(0);          // Current end of heap
```

---

## Common malloc Patterns

### Growing a buffer

```c
// Dynamic array that grows as needed
typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} DynArray;

void dynarray_push(DynArray *da, int value) {
    if (da->size >= da->capacity) {
        da->capacity = da->capacity ? da->capacity * 2 : 4;
        int *new_data = realloc(da->data, da->capacity * sizeof(int));
        if (!new_data) { /* handle error */ }
        da->data = new_data;
    }
    da->data[da->size++] = value;
}

void dynarray_free(DynArray *da) {
    free(da->data);
    da->data = NULL;
    da->size = da->capacity = 0;
}
```

### Multi-dimensional arrays

```c
// Contiguous 2D array (preferred — one allocation, better cache behavior)
int *matrix = malloc(rows * cols * sizeof(int));
matrix[row * cols + col] = 42;  // Index manually

// Array of pointers (slower, non-contiguous, but rows can have different lengths)
int **jagged = malloc(rows * sizeof(int*));
for (int i = 0; i < rows; i++) {
    jagged[i] = malloc(cols * sizeof(int));
}
// Free each row, then free jagged
```

### Structure allocation

```c
typedef struct {
    int id;
    char name[64];
    double balance;
} Account;

// Single structure
Account *a = malloc(sizeof(Account));
if (a) {
    a->id = 42;
    strcpy(a->name, "Alice");
    a->balance = 100.0;
}
free(a);

// Array of structures
Account *accounts = calloc(100, sizeof(Account));
// All zero-initialized — safe to use immediately
free(accounts);
```

---

## Custom Arena Allocators

> [!info] Arena allocator
> An arena (or region-based allocator) pre-allocates a large block of memory and sub-allocates from it incrementally. Freeing is O(1) — just reset the arena pointer. Used extensively in game development, OS kernels, and high-performance computing.

### Bump allocator (simplest arena)

```c
typedef struct {
    char *start;
    char *current;
    size_t capacity;
} Arena;

Arena arena_create(size_t capacity) {
    Arena a = {
        .start = malloc(capacity),
        .current = a.start,
        .capacity = capacity
    };
    return a;
}

void *arena_alloc(Arena *a, size_t size) {
    // Align to 16 bytes
    size = (size + 15) & ~15;
    
    if (a->current + size > a->start + a->capacity) {
        return NULL;  // Arena exhausted
    }
    
    void *ptr = a->current;
    a->current += size;
    return ptr;
}

void arena_reset(Arena *a) {
    a->current = a->start;  // O(1) free: just reset the pointer
}

void arena_destroy(Arena *a) {
    free(a->start);
    a->start = a->current = NULL;
    a->capacity = 0;
}

// Usage — all "allocations" are O(1), and freeing is O(1) via reset
Arena tmp = arena_create(1024 * 1024);  // 1 MB arena

int *arr = arena_alloc(&tmp, 100 * sizeof(int));
char *str = arena_alloc(&tmp, 256);
struct point *pts = arena_alloc(&tmp, 50 * sizeof(struct point));

arena_reset(&tmp);   // All memory reclaimed — no individual free() needed
arena_destroy(&tmp);
```

### Pool allocator (fixed-size objects)

```c
typedef struct PoolBlock {
    struct PoolBlock *next;
} PoolBlock;

typedef struct {
    PoolBlock *free_list;
    size_t block_size;
    void *arena_start;
    size_t arena_size;
} Pool;

Pool pool_create(size_t block_size, size_t block_count) {
    Pool p = {
        .block_size = (block_size >= sizeof(PoolBlock))
                       ? block_size : sizeof(PoolBlock),
        .free_list = NULL
    };
    
    size_t total = p.block_size * block_count;
    p.arena_start = malloc(total);
    p.arena_size = total;
    
    // Build free list
    char *ptr = (char*)p.arena_start;
    for (size_t i = 0; i < block_count; i++) {
        PoolBlock *block = (PoolBlock*)(ptr + i * p.block_size);
        block->next = p.free_list;
        p.free_list = block;
    }
    
    return p;
}

void *pool_alloc(Pool *p) {
    if (!p->free_list) return NULL;  // Pool exhausted
    PoolBlock *block = p->free_list;
    p->free_list = block->next;
    return (void*)block;
}

void pool_free(Pool *p, void *ptr) {
    PoolBlock *block = (PoolBlock*)ptr;
    block->next = p->free_list;
    p->free_list = block;
}

void pool_destroy(Pool *p) {
    free(p->arena_start);
    p->free_list = NULL;
}
```

---

## Debugging Memory Issues

### Compile-time checks

```bash
# Enable memory debugging with GCC
gcc -g -O0 -Wall -Wextra -fsanitize=address program.c -o program
./program   # ASan catches buffer overflows, use-after-free, etc.
```

### Runtime checks

```c
#include <stdlib.h>

// Enable glibc malloc debugging (set before any malloc calls)
// In code:
mallopt(M_CHECK_ACTION, 3);

// Or via environment variable:
// MALLOC_CHECK_=3 ./program

// Get malloc statistics
struct mallinfo info = mallinfo();
printf("Total allocated: %d bytes\n", info.uordblks);
```

### Valgrind

```bash
# Comprehensive memory check
gcc -g -O0 program.c -o program
valgrind --leak-check=full --show-leak-kinds=all ./program
```

---

## Pitfalls

### Use-after-free

```c
int *p = malloc(sizeof(int));
free(p);
*p = 5;  // ❌ Undefined behavior — p is freed!

// Fix: set pointer to NULL after free
free(p);
p = NULL;
```

### Double free

```c
int *p = malloc(sizeof(int));
free(p);
free(p);  // ❌ Undefined behavior — double free!

// Fix: never free the same pointer twice
```

### Memory leak

```c
void leak(void) {
    int *p = malloc(1000);
    // ... forgot to free(p)
}
// Every call leaks 1000 bytes. Over time, the program runs out of memory.

// Fix: every malloc must have a matching free
```

### Buffer overrun

```c
int *arr = malloc(5 * sizeof(int));
arr[5] = 42;  // ❌ Out of bounds! Corrupts heap metadata or adjacent data
```

### Forgetting to check malloc return value

```c
int *huge = malloc(SIZE_MAX);   // Will almost certainly fail
*huge = 5;                       // ❌ Dereferencing NULL → crash

// Fix: always check
if (!huge) { /* handle error */ }
```

---

> [!question]- Interview Questions
>
> **Q: How does malloc know how much memory to free?**
> A: The heap implementation stores metadata (size, flags) in a header just before the pointer returned to the caller. When `free(ptr)` is called, it looks at the header at `ptr - sizeof(header)` to know how many bytes to free. This is why you must pass the exact pointer returned by malloc — corrupted or different pointers cause undefined behavior.
>
> **Q: What is the difference between an arena allocator and malloc?**
> A: An arena allocator pre-allocates a large region and sub-allocates from it by bumping a pointer. Deallocation is O(1) — reset the pointer. `malloc` is general-purpose with free list management, coalescing, and fragmentation handling. Arena allocators are faster but less flexible — you must free everything at once (reset) or nothing.
>
> **Q: What is memory fragmentation?**
> A: After many `malloc`/`free` cycles, the heap may have many small free chunks interspersed with allocated chunks. A request for a large contiguous block may fail even though the total free space is sufficient. Fragmentation increases with varying allocation sizes. Pool allocators (fixed-size) avoid fragmentation entirely.
>
> **Q: What does `realloc` do internally?**
> A: If the existing chunk has enough free space after it, `realloc` extends in place (fast). Otherwise, it allocates a new larger chunk, `memcpy`s the old data, frees the old chunk, and returns the new pointer. The original pointer becomes invalid — always use the return value of `realloc`.
>
> **Q: When would you use a pool allocator?**
> A: When you frequently allocate and free objects of the **same fixed size** (e.g., network packet buffers, filesystem inodes, game entities). Pool allocators: (1) eliminate fragmentation, (2) are O(1) for both alloc and free, (3) improve cache locality by keeping objects of the same size close together.

---

## Cross-Links

- [[C/01_Foundations/02_Memory_Model_and_Allocation]] for stack vs heap and process layout
- [[C/01_Foundations/05_Structs_Unions_and_Bit_Fields]] for struct padding and alignment
- [[C/03_Advanced/06_Memory_Alignment_and_Endianness]] for aligned_alloc and alignment
- [[C/04_Playbooks/03_Valgrind_Leaks_and_Heap_Corruption]] for memory debugging
- [[C/05_Projects/01_Build_a_Memory_Arena_Arena_Allocator]] for custom arena allocator project
