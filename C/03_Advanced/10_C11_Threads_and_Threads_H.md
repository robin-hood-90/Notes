---
tags: [c, advanced, threads, c11-threads, thrd, mtx, cnd, tss, call-once]
aliases: ["C11 Threads", "threads.h", "thrd_t", "mtx_t", "cnd_t", "Standard Threads"]
status: stable
updated: 2026-05-11
---

# C11 Standard Threads (`<threads.h>`)

> [!summary] Goal
> Master the C11 threads API (`<threads.h>`): create and manage threads, synchronize with mutexes and condition variables, and use thread-specific storage. Compare with POSIX threads (pthreads) to understand portability trade-offs. Essential for writing portable C code on platforms that don't support pthreads (Windows, embedded).

## Table of Contents

1. [Why C11 Threads Exist](#why-c11-threads-exist)
2. [Thread Creation and Management](#thread-creation-and-management)
3. [Mutex Types](#mutex-types)
4. [Condition Variables](#condition-variables)
5. [Thread-Specific Storage](#thread-specific-storage)
6. [call_once](#callonce)
7. [C11 Threads vs Pthreads](#c11-threads-vs-pthreads)
8. [Pitfalls](#pitfalls)

---

## Why C11 Threads Exist

> [!info] C11 threads
> The C11 standard introduced `<threads.h>` as a portable threading API that doesn't depend on POSIX. It provides: `thrd_t` (thread handle), `mtx_t` (mutex), `cnd_t` (condition variable), `tss_t` (thread-specific storage), and `call_once`. Unlike pthreads, the C11 API is deliberately minimal — it covers the 80% use case and is available on platforms without POSIX (e.g., Windows via the Microsoft implementation, or embedded RTOS).

```text
The C11 threads API is OPTIONAL — conforming C11 implementations may
not provide <threads.h>. In practice:
  - Linux (glibc ≤ 2.33): NOT available (glibc didn't implement it)
  - Linux (glibc ≥ 2.34): Available
  - Windows (MSVC): Available (implemented on top of Win32 threads)
  - macOS (Apple Clang): NOT available
  - FreeBSD: Available
  - Embedded (Newlib, picolibc): May be available

For maximum portability: pthreads (POSIX) remains the standard.
C11 threads are useful when POSIX is not available (Windows without
pthreads-w32, embedded systems).
```

---

## Thread Creation and Management

```c
#include <threads.h>
#include <stdio.h>

// Thread function signature: int (*)(void *)
int worker(void *arg) {
    int id = *(int *)arg;
    printf("Thread %d: hello\n", id);
    return id;  // Return value available via thrd_join
}

int main(void) {
    thrd_t t;
    int id = 42;

    // Create a thread
    if (thrd_create(&t, worker, &id) != thrd_success) {
        fprintf(stderr, "Failed to create thread\n");
        return 1;
    }

    // Wait for thread to finish
    int result;
    if (thrd_join(t, &result) == thrd_success) {
        printf("Thread returned: %d\n", result);
    }

    // Detach (no join needed — resources freed automatically on exit)
    // thrd_detach(t);

    return 0;
}
```

### `thrd_create` return values

```c
thrd_success     // Thread created successfully
thrd_nomem       // Not enough memory to create thread
thrd_error       // Generic error
thrd_timedout    // Timeout (for timed operations)
thrd_busy        // Resource busy (for trylock)
```

### `thrd_current`, `thrd_equal`, `thrd_sleep`, `thrd_yield`

```c
#include <threads.h>

thrd_t self = thrd_current();          // Get handle to current thread
int eq = thrd_equal(t1, t2);          // Non-zero if same thread

// Sleep for specified duration
struct timespec ts = {.tv_sec = 0, .tv_nsec = 100000000};  // 100ms
thrd_sleep(&ts, NULL);

// Yield current thread's time slice
thrd_yield();
```

---

## Mutex Types

```c
#include <threads.h>

// Mutex types:
mtx_plain       // Normal, non-recursive mutex
mtx_recursive   // Recursive mutex (same thread can lock multiple times)
mtx_timed       // Supports timed locking (requires mtx_plain | mtx_timed)

// Create and destroy
mtx_t mutex;
mtx_init(&mutex, mtx_plain);               // Plain mutex
// mtx_init(&mutex, mtx_plain | mtx_timed); // Timed mutex

// Lock operations
mtx_lock(&mutex);          // Block until lock acquired
mtx_trylock(&mutex);       // Non-blocking: thrd_success or thrd_busy
mtx_timedlock(&mutex, &ts); // Try until absolute time ts (needs mtx_timed)

mtx_unlock(&mutex);

mtx_destroy(&mutex);       // Clean up
```

### Mutex example

```c
#include <threads.h>
#include <stdio.h>

mtx_t mutex;
long shared_counter = 0;

int incrementer(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        mtx_lock(&mutex);
        shared_counter++;
        mtx_unlock(&mutex);
    }
    return 0;
}

int main(void) {
    mtx_init(&mutex, mtx_plain);

    thrd_t t1, t2;
    thrd_create(&t1, incrementer, NULL);
    thrd_create(&t2, incrementer, NULL);

    thrd_join(t1, NULL);
    thrd_join(t2, NULL);

    printf("Counter: %ld (expected: 2000000)\n", shared_counter);

    mtx_destroy(&mutex);
    return 0;
}
```

---

## Condition Variables

```c
#include <threads.h>

cnd_t cond;
mtx_t mutex;

int producer(void *arg) {
    mtx_lock(&mutex);
    // Produce data...
    cnd_signal(&cond);    // Wake one waiter
    // cnd_broadcast(&cond);  // Wake all waiters
    mtx_unlock(&mutex);
    return 0;
}

int consumer(void *arg) {
    mtx_lock(&mutex);
    while (!data_ready) {                // ALWAYS loop (spurious wakeup)
        cnd_wait(&cond, &mutex);          // Atomically: unlock and wait, re-lock on wake
    }
    // Consume data...
    mtx_unlock(&mutex);
    return 0;
}
```

### Timed condition wait

```c
#include <threads.h>
#include <time.h>

int consumer_timed(void *arg) {
    mtx_lock(&mutex);

    // Calculate absolute timeout (C11 uses absolute time, not relative)
    struct timespec ts;
    timespec_get(&ts, TIME_UTC);           // Current time
    ts.tv_sec += 1;                         // 1 second from now

    while (!data_ready) {
        int ret = cnd_timedwait(&cond, &mutex, &ts);
        if (ret == thrd_timedout) {
            printf("Timeout waiting for data\n");
            break;
        }
        // ret == thrd_success: condition variable was signaled
    }

    mtx_unlock(&mutex);
    return 0;
}
```

### Spurious wakeup

```c
// ⚠️  Spurious wakeup: cnd_wait may return WITHOUT a corresponding cnd_signal.
// This is allowed by the C standard (and POSIX).
// ALWAYS check the condition in a while loop, not an if statement.

// ❌ WRONG:
// if (!data_ready) {
//     cnd_wait(&cond, &mutex);   // May return spuriously — data still not ready!
// }
// // data may NOT be ready here!

// ✅ CORRECT:
while (!data_ready) {
    cnd_wait(&cond, &mutex);   // Check again after wakeup
}
// data IS ready here
```

---

## Thread-Specific Storage

```c
#include <threads.h>
#include <stdio.h>
#include <stdlib.h>

// Thread-specific storage (TSS) — each thread has its own copy.
// Similar to POSIX pthread_key_t.

tss_t key;  // TSS key

void destructor(void *ptr) {
    free(ptr);  // Called when thread exits with non-NULL TSS value
}

int worker(void *arg) {
    // Allocate per-thread data
    int *buf = malloc(256 * sizeof(int));
    buf[0] = (int)(intptr_t)arg;

    // Store thread-specific value
    tss_set(key, buf);

    // Retrieve
    int *my_buf = tss_get(key);
    printf("Thread %d: buf[0] = %d\n", *(int *)arg, my_buf[0]);

    // buf is automatically freed by destructor when thread exits
    return 0;
}

int main(void) {
    tss_create(&key, destructor);  // Register destructor

    thrd_t t1, t2;
    int id1 = 1, id2 = 2;
    thrd_create(&t1, worker, &id1);
    thrd_create(&t2, worker, &id2);

    thrd_join(t1, NULL);
    thrd_join(t2, NULL);

    tss_delete(key);  // Clean up the key
    return 0;
}
```

---

## `call_once`

```c
#include <threads.h>
#include <stdio.h>

// call_once ensures a function is called exactly once,
// even if multiple threads call it simultaneously.

once_flag flag = ONCE_FLAG_INIT;  // Static initialization

void initialize_once(void) {
    printf("This runs exactly once\n");
    // Initialize global resources, open files, etc.
}

int worker(void *arg) {
    call_once(&flag, initialize_once);
    printf("Thread running\n");
    return 0;
}

int main(void) {
    thrd_t t1, t2, t3;
    thrd_create(&t1, worker, NULL);
    thrd_create(&t2, worker, NULL);
    thrd_create(&t3, worker, NULL);

    thrd_join(t1, NULL);
    thrd_join(t2, NULL);
    thrd_join(t3, NULL);

    // Output:
    //   This runs exactly once
    //   Thread running
    //   Thread running
    //   Thread running
    return 0;
}
```

---

## C11 Threads vs Pthreads

```text
Feature              C11 threads (threads.h)    POSIX threads (pthreads)
─────────────────────────────────────────────────────────────────────────
Thread type          thrd_t                     pthread_t
Create               thrd_create                pthread_create
Join                 thrd_join                  pthread_join
Detach               thrd_detach                pthread_detach
Exit                 thrd_exit                  pthread_exit
Self                 thrd_current               pthread_self

Mutex types          mtx_t                      pthread_mutex_t
Normal mutex         mtx_plain                  PTHREAD_MUTEX_DEFAULT
Recursive mutex      mtx_recursive              PTHREAD_MUTEX_RECURSIVE
Timed mutex          mtx_timed                  PTHREAD_MUTEX_TIMED_NP
Lock                 mtx_lock                   pthread_mutex_lock
Trylock              mtx_trylock                pthread_mutex_trylock
Timedlock            mtx_timedlock              pthread_mutex_timedlock
Unlock               mtx_unlock                 pthread_mutex_unlock
Destroy              mtx_destroy                pthread_mutex_destroy

Condition var        cnd_t                      pthread_cond_t
Wait                 cnd_wait                   pthread_cond_wait
Timed wait           cnd_timedwait              pthread_cond_timedwait
Signal               cnd_signal                 pthread_cond_signal
Broadcast            cnd_broadcast              pthread_cond_broadcast

TSS type             tss_t                      pthread_key_t
Create               tss_create                 pthread_key_create
Set                  tss_set                    pthread_setspecific
Get                  tss_get                    pthread_getspecific
Delete               tss_delete                 pthread_key_delete

Once                 once_flag + call_once      pthread_once_t + pthread_once

RW locks             NOT AVAILABLE              pthread_rwlock_t
Barriers             NOT AVAILABLE              pthread_barrier_t
Spinlocks            NOT AVAILABLE              pthread_spinlock_t
Error-check mutex    NOT AVAILABLE              PTHREAD_MUTEX_ERRORCHECK
```

### Key differences

```text
1. C11 threads are SIMPLER but have fewer features.
   Missing: read-write locks, barriers, spinlocks, error-checking mutexes,
   robust mutexes, priority inheritance.

2. C11 `cnd_timedwait` uses ABSOLUTE time (timespec from clock).
   Same as POSIX — you pass an absolute deadline, not a relative duration.

3. C11 destructors for TSS accept void* and return void.
   Same as POSIX.

4. C11 thread return values: int (not void*).
   Pthreads: void* — allows returning any pointer type.
   C11: int — simpler but limited to integer return codes.

5. Availability: pthreads is available on almost every platform.
   C11 threads: optional (missing on macOS, older glibc).
```

### Simple portability wrapper

```c
// If you need a simple portability layer between C11 threads and pthreads:

#ifdef __STDC_NO_THREADS__
// Fall back to pthreads
#include <pthread.h>
typedef pthread_t thrd_t;
typedef pthread_mutex_t mtx_t;
// ... wrap pthread functions ...
#else
#include <threads.h>
#endif
```

---

## Pitfalls

### C11 threads are optional — not all implementations provide them

Always check `__STDC_NO_THREADS__` before using `<threads.h>`:

```c
#ifndef __STDC_NO_THREADS__
#include <threads.h>
#else
// Fall back to pthreads or platform-specific API
#endif
```

### `cnd_timedwait` takes absolute time, not relative

Passing a relative duration (e.g., 1 second from now) requires adding the current time:

```c
struct timespec ts;
timespec_get(&ts, TIME_UTC);   // Get current time
ts.tv_sec += 5;                 // 5 seconds from now
cnd_timedwait(&cond, &mutex, &ts);  // Absolute deadline
```

### No RW locks or barriers

The C11 threads API lacks read-write locks and barriers. If you need these, use pthreads or implement them yourself with mutexes + condition variables.

### `tss_set` may fail

`tss_set` can fail if the implementation runs out of internal storage for TSS entries. Always check the return value.

---

## Cross-Links

- [[C/03_Advanced/01_Concurrency_with_Pthreads]] for pthreads (fuller API, more portable)
- [[C/03_Advanced/02_C11_Atomics_and_Memory_Model]] for atomic operations (lock-free alternative)
- [[C/02_Core/06_Undefined_Behavior_and_Memory_Safety]] for data race UB considerations
