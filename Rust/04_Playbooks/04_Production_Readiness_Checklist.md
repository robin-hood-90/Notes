---
tags: [rust, playbook, production, observability, tracing, metrics]
aliases: ["Production Readiness", "Rust Production Checklist"]
status: stable
updated: 2026-05-11
---

# Production Readiness Checklist

> [!summary] Goal
> Review the highest-risk operational issues before shipping a Rust service or worker.

## Observability

```text
[ ] Structured logging with tracing (fmt or JSON) configured
[ ] tracing subscriber installed (events not silently dropped!)
[ ] RUST_LOG or EnvFilter configured for runtime log level
[ ] Performance metrics exported (counter, gauge, histogram)
[ ] Health check endpoint (GET /health)
[ ] Readiness check endpoint (shows when service is ready to serve)
[ ] Startup log message (version, config summary, listening address)
[ ] Graceful shutdown: SIGTERM → drain active requests → exit
```

## Concurrency and Async

```text
[ ] spawn_blocking used for blocking / CPU-heavy work
[ ] No std::sync::MutexGuard held across .await
[ ] Timeouts on all outbound I/O (HTTP, DB, message queue)
[ ] Bounded channels with explicit backpressure handling
[ ] select! in event loops has at least timeout branch to prevent starvation
[ ] Tokio runtime configured with appropriate worker threads
```

## Resource Management

```text
[ ] Connection pool limits configured (DB, HTTP, Redis)
[ ] Drop implementations do NOT panic
[ ] Thread local storage with remove() in thread pools (if used)
[ ] Arc cycles avoided (use Weak when needed)
[ ] OOM protection: bounded queues, buffers, and caches
```

## Error Handling

```text
[ ] All expected errors return Result (not panic)
[ ] Error types implement std::error::Error (via thiserror)
[ ] Panic hook set (logs to tracing, includes backtrace)
[ ] FFI entry points wrapped in catch_unwind
[ ] Mutex poisoning handled explicitly
```

## Build

```text
[ ] Release profile: opt-level=3, lto="fat", codegen-units=1
[ ] panic = "abort" (unless library)
[ ] Cargo deny / cargo audit for dependency vulnerabilities
[ ] Feature flags are additive (no feature-dependent API breaks)
[ ] Workspace dependencies are consistent (shared versions)
```

## Testing

```text
[ ] Unit tests covering all error paths
[ ] Integration tests for key HTTP/DB flows
[ ] Property-based tests (proptest) for stateful logic
[ ] Async tests with tokio::test
[ ] Miri tests for unsafe code paths
[ ] Benchmark with criterion for hot paths
[ ] Load testing with production-like workload
```

## Deployment

```text
[ ] Graceful shutdown: handle SIGTERM, drain, then exit
[ ] Readiness probe before accepting traffic
[ ] Liveness probe for crash detection
[ ] Metrics endpoint for Prometheus
[ ] Distributed tracing headers parsed and propagated
[ ] Configuration via environment variables (not hardcoded paths)
```

---

## Cross-Links

- [[Rust/03_Advanced/17_Tracing_Logging_and_Observability]] for tracing setup
- [[Rust/02_Core/04_Async_Await_Tokio_Basics]] for async runtime design
- [[Rust/04_Playbooks/02_Debug_Panic_Backtraces_and_Error_Contexts]] for panic handling
- [[SystemDesign/02_Core/05_Observability_Logs_Metrics_Traces]] for system design
