---
tags: [go, playbook, goroutines, leaks, deadlocks, trace, blocking-profile, stack-inspect]
aliases: ["Debug Goroutine Leaks", "Goroutine Leaks", "goleak", "Goroutine Debugging"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug Goroutine Leaks and Deadlocks

> [!summary] Goal
> Detect and fix goroutine leaks and deadlocks: use `goleak` in tests, analyze SIGQUIT dumps, interpret blocking profiles, read execution traces, and use common leak pattern detection.

## Tools Overview

| Tool | What it catches | Command |
|------|:---------------:|---------|
| `goleak` (test-time) | Goroutines left behind after tests | `goleak.VerifyTestMain(m)` |
| SIGQUIT dump (runtime) | All goroutine stacks at a point in time | `kill -QUIT <pid>` |
| `pprof` goroutine profile | Number of goroutines per call site | `/debug/pprof/goroutine` |
| `pprof` blocking profile | Sync primitives that block goroutines | `/debug/pprof/block` |
| `runtime/trace` | Execution timeline of goroutine activity | `go tool trace trace.out` |

## `uber-go/goleak` in Tests

```go
import "go.uber.org/goleak"

// Option 1: Verify across ALL tests in the package (TestMain):
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}

// Option 2: Per-test verification:
func TestSomething(t *testing.T) {
    defer goleak.VerifyNone(t)

    ch := make(chan int)
    go func() {
        <-ch  // Blocks forever — leak!
    }()
    // Test passes but goleak reports: "found unexpected goroutines"
}

// goleak ignores known runtime goroutines (finalizer, GC, etc.).
// Use goleak.Option to ignore additional goroutines:
//   goleak.VerifyNone(t, goleak.IgnoreTopFunction("internal/my.pkg.backgroundWorker"))
```

## Common Leak Patterns

```go
// Pattern 1: Unbuffered channel send without receiver
ch := make(chan int)
go func() {
    ch <- 42  // Blocks forever if nobody receives
}()

// Pattern 2: Missing <-ctx.Done() in select
go func() {
    select {
    case result <- doWork():
        // ...
    // ❌ Missing: case <-ctx.Done():
    }
}()

// Pattern 3: Ticker not stopped
ticker := time.NewTicker(1 * time.Second)
// go func() { for range ticker.C { ... } }()
// ticker.Stop() is never called → goroutines leak

// Pattern 4: HTTP response body not closed
go func() {
    resp, _ := http.Get("https://example.com")
    // ❌ Missing: defer resp.Body.Close()
    // Connection not returned to pool, goroutine stays alive
}()
```

## SIGQUIT Stack Dump Analysis

```bash
# Trigger a goroutine dump:
kill -QUIT <pid>       # Dumps to stderr
# Or via HTTP (net/http/pprof):
curl http://localhost:6060/debug/pprof/goroutine?debug=2

# What to look for in the dump:
#   goroutine 123 [chan send, 5 minutes]:
#   goroutine 456 [select, 10 minutes]:
#   goroutine 789 [semacquire, 30 minutes]:

# "5 minutes" means the goroutine has been blocked for 5 minutes.
# Take 2-3 dumps a few seconds apart:
#   A goroutine at the same stack in EVERY dump = likely stuck (leak or deadlock).
#   A goroutine at different stacks = making progress.

# Common stuck states:
#   [chan send] — sending on a channel nobody reads from
#   [chan receive] — waiting for a value nobody sends
#   [select] — all cases are blocking (forgot <-ctx.Done())
#   [semacquire] — blocked on sync.Mutex.Lock() (deadlock or contention)
#   [IO wait] — blocked on network I/O (normal for servers, abnormal for workers)
```

## Blocking Profile

```go
import _ "net/http/pprof"

// The blocking profile shows goroutines that spent significant time
// blocked on synchronization primitives. It must be enabled:

func init() {
    runtime.SetBlockProfileRate(1) // Track every blocking event (expensive)
    // In production, use a lower rate or disable:
    // runtime.SetBlockProfileRate(100 * 1000 * 1000) // Sample every 100ms of blocking
}

// View: go tool pprof http://localhost:6060/debug/pprof/block
// Shows: which mutex/chan/wait has the most cumulative blocking time
```

## Execution Trace

```go
import "runtime/trace"

// Traces capture a timeline of goroutine creation, blocking, GC, and syscalls.
f, _ := os.Create("trace.out")
trace.Start(f)
// ... run workload ...
trace.Stop()

// Analyze: go tool trace trace.out
// Shows: goroutine states over time (runnable, running, waiting)
// Look for: goroutines in "Waiting" state for long periods
```

---

## Cross-Links

- [[Go/02_Core/02_Concurrency_Patterns_WorkerPools_FanInOut]] for sync patterns
- [[Go/02_Core/03_Data_Races_Sync_Map_and_Typed_Atomics]] for -race, data races
- [[Go/03_Advanced/04_Profiling_pprof_and_Tracing]] for pprof and trace tools
- [[Go/04_Playbooks/02_Debug_High_CPU_and_GC_Pressure]] for CPU profiling
