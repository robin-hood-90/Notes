---
tags: [go, core, data-races, sync-map, atomics, race-detector, singleflight, semaphore]
aliases: ["Data Races", "sync.Map", "Typed Atomics", "atomic.Pointer", "singleflight", "Race Detector", "C03"]
status: stable
updated: 2026-05-11
---

# Data Races, `sync.Map`, Typed Atomics, and Advanced Sync

> [!summary] Goal
> Master Go's advanced synchronization: `sync.Map` (concurrent map with read-optimized internals), typed atomics (`atomic.Int64`, `atomic.Pointer`, `atomic.Bool`), the race detector, `singleflight` for call coalescing, `semaphore.Weighted` for resource limits, and `errgroup.SetLimit` for bounded concurrency.

## Table of Contents

1. [Race Detector](#race-detector)
2. [Typed Atomics (Go 1.19+)](#typed-atomics)
3. [sync.Map Internals and Trade-offs](#sync-map-internals-and-trade-offs)
4. [singleflight — Deduplicate Concurrent Calls](#singleflight-deduplicate-concurrent-calls)
5. [semaphore.Weighted — Resource Limits](#semaphore-weighted-resource-limits)
6. [errgroup.SetLimit — Bounded Concurrency](#errgroup-setlimit-bounded-concurrency)

---

## Race Detector

> [!info] Race detector
> Go's race detector (enabled with `-race`) instruments every memory access and reports when two goroutines access the same variable concurrently and at least one is a write. It's built into `go test`, `go build`, and `go run`. Add it to CI.

```bash
# Enable the race detector:
go test -race ./...
go build -race -o program .
go run -race main.go

# Runtime overhead: 2-20× slower, 5-10× more memory.
# Use in CI and testing. Ship binaries WITHOUT -race (SIGBUS risk on some platforms).

# The detector reports:
# WARNING: DATA RACE
# Read at 0x... by goroutine 7:
#   main.main() main.go:25 +0x...
# Previous write at 0x... by goroutine 6:
#   main.worker() main.go:15 +0x...

# Environment variables:
export GORACE="halt_on_error=1"         # Stop on first race
export GORACE="log_path=/tmp/race/log"  # Write logs to files
```

### Common data race patterns the detector finds

```go
// Pattern 1: Unprotected counter
var counter int
go func() { counter++ }()     // Write
go func() { fmt.Println(counter) }()  // Read — RACE!

// Pattern 2: Slice/map access without sync
var items []int
go func() { items = append(items, 1) }()
go func() { fmt.Println(len(items)) }()

// Pattern 3: Interface value mutation
var config interface{} = "v1"
go func() { config = "v2" }()           // Write to interface
go func() { fmt.Println(config) }()     // Read from interface — RACE!
// Fix: use atomic.Value
```

---

## Typed Atomics (Go 1.19+)

> [!info] Typed atomics
> Go 1.19 introduced typed atomic types in `sync/atomic`. These replace the older function-based API (`atomic.LoadInt64(&x)`) with method-based values (`var x atomic.Int64; x.Load()`). They're type-safe, easier to read, and prevent misuse of `unsafe.Pointer`.

```go
import "sync/atomic"

// The typed atomic types:
atomic.Int64
atomic.Uint64
atomic.Bool
atomic.Pointer[T]     // Go 1.19+: type-safe atomic pointer
atomic.Int32
atomic.Uint32
atomic.Uintptr
atomic.Value          // Pre-1.19: stores any type, no compile-time safety
```

### `atomic.Int64` / `atomic.Uint64`

```go
var counter atomic.Int64

// All methods:
counter.Load()                         // Get value
counter.Store(42)                      // Set value
counter.Add(5)                         // Add and return new value
old := counter.Swap(100)              // Set and return old value
swapped := counter.CompareAndSwap(100, 200) // CAS: returns true if swapped

// Pattern: metrics counter
var requests atomic.Uint64

func handleRequest() {
    requests.Add(1)
    // ...
}

func metricsHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "requests: %d\n", requests.Load())
}
```

### `atomic.Bool`

```go
var running atomic.Bool

running.Store(true)                     // Set
running.Load()                          // Get (no data race!)
running.CompareAndSwap(true, false)     // CAS only if current value matches
running.Swap(false)                     // Set and return old

// Pattern: graceful shutdown flag
var shuttingDown atomic.Bool

func healthHandler(w http.ResponseWriter, r *http.Request) {
    if shuttingDown.Load() {
        w.WriteHeader(http.StatusServiceUnavailable)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

### `atomic.Pointer[T]`

```go
// atomic.Pointer is the typed replacement for atomic.Value in most cases.
// It ensures compile-time type safety.

type Config struct {
    Port    int
    Timeout time.Duration
}

var config atomic.Pointer[Config]

// Writer:
func updateConfig(cfg *Config) {
    config.Store(cfg)
}

// Reader:
func getConfig() *Config {
    return config.Load()         // Non-blocking, no data race
}

// Pattern: hot reload configuration
func configWatcher() {
    for {
        cfg := loadConfigFromFile()
        config.Store(&cfg)      // Publish new config atomically
        time.Sleep(10 * time.Second)
    }
}
```

### `atomic.Value` (pre-1.19, use when the type is not known at compile time)

```go
var v atomic.Value

v.Store(42)           // Can store any type
v.Store("hello")      // REPLACES the type — panics if you store a different type!

val := v.Load().(int) // Must type-assert
```

---

## `sync.Map` Internals and Trade-offs

> [!info] sync.Map
> `sync.Map` is a concurrent map optimized for **write-once, read-many** workloads. It uses two internal maps: a **read-only** map (accessed via `sync.Value` for lock-free reads) and a **dirty** map (guarded by a mutex). It also tracks "misses" — when a read fails on the read-only map and must access the dirty map. After enough misses, the read-only map is promoted (amortized cost).

### When to use `sync.Map`

```go
var m sync.Map

// Store a key-value pair
m.Store("alice", 42)

// Load a value
val, ok := m.Load("alice")     // val = 42, ok = true
val, ok := m.Load("bob")       // val = nil, ok = false

// LoadOrStore — atomically: if key exists, return existing; otherwise store
val, loaded := m.LoadOrStore("alice", 99)
// val = 42 (existing), loaded = true (was already stored)

// Delete
m.Delete("alice")

// LoadAndDelete — atomically load and remove
val, loaded := m.LoadAndDelete("alice")

// Range (consistent snapshot of keys)
m.Range(func(key, value any) bool {
    fmt.Println(key, value)
    return true  // continue iteration
})

// CompareAndDelete / CompareAndSwap (Go 1.20+)
m.CompareAndDelete("alice", 42)   // Delete only if value == 42
m.CompareAndSwap("alice", 42, 99) // CAS on map entry
```

### Benchmarks: `sync.Map` vs `Mutex + map`

```text
Workload                        sync.Map       Mutex + map
─────────────────────────────────────────────────────────────
100% reads (no writes)          18ns/op         50ns/op        ← sync.Map wins
95% reads, 5% writes            60ns/op         80ns/op        ← sync.Map wins
50% reads, 50% writes           120ns/op        90ns/op        ← Mutex wins
100% writes (same key)          200ns/op        90ns/op        ← Mutex wins
Many keys, write once, read many 30ns/op        60ns/op        ← sync.Map wins

sync.Map is faster when:
  - Keys are written once then read many times (config maps, registry maps).
  - Read-heavy workloads with low write contention.
  - Different goroutines read/write DIFFERENT keys.

sync.Map is SLOWER than Mutex + map when:
  - Many writes to the same key (contention on dirty map).
  - Write-heavy workloads (frequent promotions).
  - Small maps (mutex contention is cheap).

Rule: default to `sync.RWMutex + map`. Use `sync.Map` only after profiling shows
it's faster for your workload.
```

### Internals

```go
// Simplified sync.Map structure:
type Map struct {
    mu     Mutex
    read   atomic.Pointer[readOnly]   // Lock-free readable map
    dirty  map[any]*entry             // Needs mu to access
    misses int                        // Read misses before promotion
}

type readOnly struct {
    m       map[any]*entry
    amended bool // true if dirty differs from read
}

type entry struct {
    p atomic.Pointer[any]             // Points to the value (or expunged sentinel)
}

// Load path:
//   1. Load from read (lock-free)          → hit? return
//   2. Lock mu
//   3. Load from dirty (under lock)
//   4. Increment misses; if misses ≥ len(dirty), promote dirty → read
//   5. Unlock mu
```

---

## `singleflight` — Deduplicate Concurrent Calls

> [!info] singleflight
> `singleflight` (from `golang.org/x/sync/singleflight`) coalesces multiple concurrent calls for the same key into a single execution. The first caller runs the function; subsequent callers wait for the result. This prevents the "thundering herd" problem — 100 concurrent requests for the same cache key all triggering a DB query.

```go
import "golang.org/x/sync/singleflight"

var group singleflight.Group

func fetchUser(id int) (User, error) {
    // Only ONE call to loadUser runs at a time per key.
    // The rest wait and receive the SAME result.
    result, err, shared := group.Do("user:"+strconv.Itoa(id), func() (interface{}, error) {
        return loadUser(id)  // DB query or HTTP call — runs once
    })
    if err != nil {
        return User{}, err
    }
    // shared == true if the result was shared with other callers
    return result.(User), nil
}

// With cache:
func fetchWithCache(id int) (User, error) {
    if user, ok := cache.Get(id); ok {
        return user, nil
    }

    // Even with 100 concurrent requests, only 1 DB call happens:
    result, err, _ := group.Do("user:"+strconv.Itoa(id), func() (interface{}, error) {
        user, err := loadUser(id)
        if err == nil {
            cache.Set(id, user)  // All waiters get the result
        }
        return user, err
    })
    if err != nil {
        return User{}, err
    }
    return result.(User), nil
}

// group.DoChan — async pattern with channel
ch := group.DoChan("key", fn)
select {
case result := <-ch:
    // ...
case <-ctx.Done():
    group.Forget("key")  // Allow new callers to retry
}

// group.Forget — drop the in-flight result so a new call starts
```

---

## `semaphore.Weighted` — Resource Limits

> [!info] semaphore.Weighted
> `semaphore.Weighted` (from `golang.org/x/sync/semaphore`) provides a weighted semaphore — acquire N permits, release N permits. Unlike Go channels (which act as a simple counting semaphore), `semaphore.Weighted` supports: arbitrary weights, `Acquire` with context cancellation, and `TryAcquire` non-blocking.

```go
import "golang.org/x/sync/semaphore"

// Limit to 10 concurrent DB connections
var dbSem = semaphore.NewWeighted(10)

func queryDB(ctx context.Context, query string) (Result, error) {
    // Acquire 1 permit (block until available or context canceled)
    if err := dbSem.Acquire(ctx, 1); err != nil {
        return Result{}, err  // Context canceled
    }
    defer dbSem.Release(1)

    return doQuery(query)  // At most 10 concurrent queries
}

// Weighted acquire (e.g., a large query that counts as 2)
func queryLarge(ctx context.Context) error {
    if err := dbSem.Acquire(ctx, 2); err != nil {
        return err
    }
    defer dbSem.Release(2)
    return nil
}

// TryAcquire — non-blocking
if !dbSem.TryAcquire(1) {
    // Return 503 instead of blocking
    return fmt.Errorf("too many concurrent requests")
}
defer dbSem.Release(1)
```

---

## `errgroup.SetLimit` — Bounded Concurrency

> [!info] errgroup.SetLimit (Go 1.20+)
> `errgroup` (from `golang.org/x/sync/errgroup`) was already used for goroutine groups with error propagation. Go 1.20 added `SetLimit(n)` to bound concurrency — at most `n` goroutines are active at once. This replaces manual channel-based throttling with a cleaner API.

```go
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10)  // At most 10 concurrent goroutines

items := []string{"a", "b", "c", /* ... 1000 items */}

for _, item := range items {
    item := item  // Capture loop variable
    g.Go(func() error {
        // Block if 10 goroutines are already running
        select {
        case <-ctx.Done():
            return ctx.Err()  // Early exit on cancel
        default:
        }
        return process(item)
    })
}

// Wait for all goroutines to complete
if err := g.Wait(); err != nil {
    log.Printf("processing failed: %v", err)
}
```

---

## Cross-Links

- [[Go/02_Core/02_Concurrency_Patterns_WorkerPools_FanInOut]] for sync.Mutex, errgroup, channels
- [[Go/01_Foundations/02_Goroutines_and_Channels]] for goroutine basics
- [[Go/03_Advanced/02_GC_Escape_Analysis_and_Performance]] for atomic.Value and allocation pressure
- [[Go/04_Playbooks/01_Debug_Goroutine_Leaks_and_Deadlocks]] for race detector in debugging
- [[Go/04_Playbooks/04_Production_Readiness_Checklist]] for -race in CI
