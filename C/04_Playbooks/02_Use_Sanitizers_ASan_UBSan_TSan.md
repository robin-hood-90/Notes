---
tags: [c, playbook, sanitizers, asan, ubsan, tsan, msan, memory-safety]
aliases: ["Sanitizers", "Address Sanitizer", "Undefined Behavior Sanitizer", "Thread Sanitizer", "ASan", "UBSan", "TSan"]
status: stable
updated: 2026-05-09
---

# Playbook: Use Sanitizers (ASan, UBSan, TSan, MSan)

> [!summary] Goal
> Detect memory bugs, undefined behavior, and data races at runtime using GCC/Clang sanitizers. These tools instrument the binary at compile time to catch errors that would otherwise cause subtle, hard-to-find bugs.

## Table of Contents

1. [Sanitizer Overview](#sanitizer-overview)
2. [AddressSanitizer (ASan)](#addresssanitizer)
3. [UndefinedBehaviorSanitizer (UBSan)](#undefinedbehaviorsanitizer)
4. [ThreadSanitizer (TSan)](#threadsanitizer)
5. [MemorySanitizer (MSan)](#memorysanitizer)
6. [CI Integration](#ci-integration)
7. [Pitfalls](#pitfalls)

---

## Sanitizer Overview

> [!info] Sanitizer
> A sanitizer is a compile-time instrumentation tool that adds runtime checks to your program. It detects specific classes of bugs and reports them with source file, line number, and a detailed diagnostic message. Sanitizers have moderate overhead (1-3× slowdown) and are intended for testing, not production.

| Sanitizer | Flag | Catches | Overhead |
|-----------|:----:|---------|:--------:|
| **ASan** | `-fsanitize=address` | Buffer overflows, use-after-free, double free, stack/global overflow | ~2× CPU, ~2× memory |
| **UBSan** | `-fsanitize=undefined` | Signed overflow, shift overflow, null pointer, misaligned access | ~1.1× CPU |
| **TSan** | `-fsanitize=thread` | Data races between threads | ~5-10× CPU, ~5× memory |
| **MSan** | `-fsanitize=memory` | Reading uninitialized memory | ~3× CPU |

---

## AddressSanitizer (ASan)

```bash
# Compile with ASan
gcc -g -O1 -fsanitize=address program.c -o program

# Run — ASan checks every memory access
./program
```

### Detecting buffer overflow

```c
// example.c
#include <stdlib.h>
int main(void) {
    int *arr = malloc(5 * sizeof(int));
    arr[5] = 42;              // ❌ Overflow: index 5 is past the end
    free(arr);
    return 0;
}

// ASan output:
// ==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x603... at pc ...
//   WRITE of size 4 at 0x603... thread T0
//     #0 main example.c:5
//   0x603... is located 0 bytes after 20-byte region [0x603...,0x603...)
//   allocated by malloc:
//     #0 __interceptor_malloc
//     #1 main example.c:4
```

### Detecting use-after-free

```c
int main(void) {
    int *p = malloc(10);
    free(p);
    p[0] = 42;                 // ❌ Use after free
    return 0;
}

// ASan output:
// ==12346==ERROR: AddressSanitizer: heap-use-after-free on address ...
//   WRITE of size 4 at ...
//     #0 main example.c:5
//   freed by:
//     #0 __interceptor_free
//     #1 main example.c:4
```

### Detecting double free

```c
int main(void) {
    int *p = malloc(10);
    free(p);
    free(p);                   // ❌ Double free
    return 0;
}

// ASan output:
// ==12347==ERROR: AddressSanitizer: attempting double-free on address ...
```

---

## UndefinedBehaviorSanitizer (UBSan)

```bash
gcc -g -O1 -fsanitize=undefined program.c -o program
./program
```

### Detecting signed overflow

```c
#include <limits.h>
int main(void) {
    int x = INT_MAX;
    int y = x + 1;             // ❌ Signed integer overflow (UB)
    return 0;
}

// UBSan output:
// example.c:5: runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

### Detecting shift overflow

```c
int main(void) {
    int x = 1;
    int y = x << 33;           // ❌ Shift by >= bit width
    return 0;
}
```

### UBSan flags

```bash
# Individual checks (all included in -fsanitize=undefined)
-fsanitize=shift              # Shift by >= type width
-fsanitize=integer-overflow   # Signed overflow
-fsanitize=null              # Null pointer dereference
-fsanitize=align             # Unaligned access
-fsanitize=vla-bound         # VLA with non-positive size
-fsanitize=float-divide-by-zero  # Float division by zero

# All of the above (recommended)
-fsanitize=undefined

# With trap instead of error message (no libubsan needed)
-fsanitize=signed-integer-overflow -fsanitize-trap=all
```

---

## ThreadSanitizer (TSan)

```bash
# Compile with TSan (MUST use -O1 or higher, -fsanitize=thread)
gcc -g -O1 -fsanitize=thread -lpthread program.c -o program
./program
```

### Detecting data races

```c
#include <pthread.h>
int counter = 0;              // ❌ Shared without synchronization

void *worker(void *arg) {
    for (int i = 0; i < 100000; i++) {
        counter++;             // Race: concurrent non-atomic increment
    }
    return NULL;
}

int main(void) {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, worker, NULL);
    pthread_create(&t2, NULL, worker, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}

// TSan output:
// WARNING: ThreadSanitizer: data race (pid=...)
//   Write of size 4 at ... by thread T1:
//     #0 worker example.c:6
//   Previous write of size 4 at ... by thread T2:
//     #0 worker example.c:6
//   Location is global 'counter' of size 4 at ...
```

---

## MemorySanitizer (MSan)

```bash
# Compile with MSan (MUST instrument ALL libraries)
gcc -g -O1 -fsanitize=memory -fsanitize-memory-track-origins program.c -o program
./program
```

### Detecting uninitialized reads

```c
int main(void) {
    int x;                     // Not initialized
    if (x > 0) {               // ❌ Reading uninitialized variable
        printf("positive\n");
    }
    return 0;
}
```

---

## CI Integration

```makefile
# Makefile target for sanitizer builds
test-asan: CFLAGS += -g -O1 -fsanitize=address -fno-omit-frame-pointer
test-asan: program
    ./program
    @echo "ASan tests passed"

test-ubsan: CFLAGS += -g -O1 -fsanitize=undefined
test-ubsan: program
    ./program
    @echo "UBSan tests passed"

test-tsan: CFLAGS += -g -O1 -fsanitize=thread
test-tsan: LDFLAGS += -lpthread
test-tsan: program
    ./program
    @echo "TSan tests passed"
```

```bash
# CI script snippet
gcc -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer program.c -o program
./program || exit 1
```

---

## Pitfalls

### TSan requires all code to be instrumented

TSan catches data races between threads, but ALL code that accesses shared memory must be compiled with TSan. If a library is not TSan-instrumented, TSan can't detect races through it.

### MSan requires instrumented libraries

MSan requires `-fsanitize=memory` on ALL code, including system libraries. Use `-fsanitize-memory-track-origins` to find where the uninitialized value came from.

### ASan and static linking

ASan on some platforms requires dynamic linking. If you see "ASan runtime does not come first in initializer list" errors, compile with `-shared-libasan` or ensure ASan is the first library linked.

---

## Cross-Links

- [[C/02_Core/06_Undefined_Behavior_and_Memory_Safety]] for UB sources
- [[C/04_Playbooks/01_Debug_Segfaults_and_Invalid_Memory_Access]] for crash debugging
- [[C/02_Core/07_Debugging_with_GDB]] for GDB debugging
- [[C/01_Foundations/06_Preprocessor_and_Compilation]] for compiler flags
- [[C/02_Core/08_Build_Systems_and_Makefiles]] for Makefile integration
