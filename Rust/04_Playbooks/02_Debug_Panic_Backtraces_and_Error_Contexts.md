---
tags: [rust, playbook, panic, backtrace, debugging]
aliases: ["Debug Panic", "Backtraces", "Panic Handling"]
status: stable
updated: 2026-05-11
---

# Debug Panics, Backtraces, and Error Contexts

> [!summary] Goal
> Make Rust failures diagnosable by combining panic backtraces, typed error handling, and useful context at application boundaries.

## Fast Checklist

- enable `RUST_BACKTRACE=1` (or `RUST_LIB_BACKTRACE=1`)
- reproduce with debug symbols if needed
- identify panic site vs calling context
- determine whether panic indicates bug or violated precondition
- prefer `Result` for expected failures in libraries/services

## Panic Backtraces

```bash
# Enable full backtrace
RUST_BACKTRACE=1 ./my-app

# Enable backtrace only for library panics (not main)
RUST_LIB_BACKTRACE=1 ./my-app

# Full backtrace (includes all frames, not just application)
RUST_BACKTRACE=full ./my-app

# Capture backtrace at a specific point (not just panics)
# In code:
fn capture() {
    let bt = std::backtrace::Backtrace::capture();
    println!("{bt}");
}
```

## Panic Hooks

```rust
use std::panic;

// Custom panic hook — logs panic details to your structured logger
fn main() {
    panic::set_hook(Box::new(|panic_info| {
        let payload = panic_info.payload()
            .downcast_ref::<&str>()
            .copied()
            .or_else(|| {
                panic_info.payload()
                    .downcast_ref::<String>()
                    .map(|s| s.as_str())
            })
            .unwrap_or("(no message)");

        let location = panic_info.location()
            .map(|l| format!("{}:{}", l.file(), l.line()))
            .unwrap_or_else(|| "(unknown)".into());

        let backtrace = std::backtrace::Backtrace::force_capture();

        // Log to your tracing subscriber
        tracing::error!(
            panic.message = %payload,
            panic.location = %location,
            panic.backtrace = %backtrace,
            "Thread panicked",
        );
    }));

    // Normal app code...
}
```

## catch_unwind for Boundary Safety

```rust
use std::panic::catch_unwind;

// catch_unwind catches panics and returns them as Err.
// Useful at FFI boundaries and in thread pools.

fn main() {
    let result = catch_unwind(|| {
        // Code that might panic
        panic!("something went wrong");
    });

    match result {
        Ok(val) => println!("Success: {val:?}"),
        Err(panic) => {
            // Extract the panic message
            if let Some(msg) = panic.downcast_ref::<&str>() {
                eprintln!("Panic: {msg}");
            } else if let Some(msg) = panic.downcast_ref::<String>() {
                eprintln!("Panic: {msg}");
            } else {
                eprintln!("Panic with unknown payload");
            }
        }
    }
}

// In a thread pool:
let handles: Vec<_> = (0..10).map(|i| {
    std::thread::spawn(move || {
        let result = catch_unwind(|| {
            worker(i);
        });
        if result.is_err() {
            eprintln!("Worker {i} panicked!");
        }
    })
}).collect();
```

## abort vs unwind

```text
Rust can handle panics in two ways:
  - unwind (default): runs destructors, then propagates the panic.
  - abort: terminates the process immediately (no cleanup).

Configure in Cargo.toml:
  [profile.release]
  panic = "abort"

Considerations:
  - abort: smaller binary (~2% smaller), no unwinding overhead,
    BUT no destructors run, no graceful shutdown.
  - unwind: larger binary, destructors run,
    BUT may leave state inconsistent if panics cross library boundaries.

Production recommendation:
  - Use panic = "abort" for services with health checks and auto-restart.
  - Use panic = "unwind" for libraries that might be embedded.
  - Wrap FFI boundaries with catch_unwind regardless.
```

---

## Cross-Links

- [[Rust/01_Foundations/03_Error_Handling_Result_and_ThisError]] for Result-based error handling
- [[Rust/03_Advanced/02_Unsafe_Rust_and_FFI_Basics#catch_unwind-and-poisoning]] for catch_unwind at FFI boundaries
