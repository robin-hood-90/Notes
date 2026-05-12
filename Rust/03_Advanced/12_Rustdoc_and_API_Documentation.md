---
tags: [rust, advanced, documentation, rustdoc, doc-comments]
aliases: ["Rustdoc", "Documentation", "Doc Comments", "API Documentation"]
status: stable
updated: 2026-05-03
---

# Rustdoc and API Documentation

> [!summary] Goal
> Write documentation that is both human-readable and executable as tests.

## Table of Contents

1. [Why Rustdoc Matters](#why-rustdoc-matters)
2. [Doc Comments](#doc-comments)
3. [Doc Tests](#doc-tests)
4. [Linking and Re-exports](#linking-and-re-exports)
5. [Crate-Level Docs](#crate-level-docs)
6. [Pitfalls](#pitfalls)

---

## Why Rustdoc Matters

Rustdoc generates HTML documentation from code comments. It is a first-class part of the language — not an external tool.

```bash
cargo doc           # generate docs in target/doc/
cargo doc --open    # generate and open in browser
cargo doc --no-deps # only document your crate, not dependencies
```

> [!tip] Definition
> **Rustdoc**: the Rust documentation tool. It parses `///` and `//!` comments, renders them as HTML, and runs code blocks as tests.

---

## Doc Comments

### Item docs — `///` or `#[doc = "..."]`

```rust
/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// use my_crate::add;
/// assert_eq!(add(2, 3), 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

### Inner docs — `//!` for crate/module level

```rust
//! # My Crate
//!
//! `my_crate` is a collection of utilities for processing data.
//!
//! ## Features
//! - Fast parsing
//! - Zero-copy deserialization

pub mod parser;
```

---

## Doc Tests

All code blocks in doc comments are compiled and run by `cargo test`:

```rust
/// ```
/// let result = my_crate::compute(10);
/// assert_eq!(result, 42);
/// ```
pub fn compute(x: i32) -> i32 { x + 32 }
```

### Hiding setup lines

```rust
/// ```
/// # // The # hides this line from rendered docs, but it still compiles
/// # use my_crate::setup;
/// let data = setup();
/// assert!(data.is_ready());
/// ```
```

### Failing doc tests

```rust
/// ```should_panic
/// // This test expects a panic
/// let v = vec![1, 2, 3];
/// v[100];
/// ```
```

### Ignore doc tests

```rust
/// ```ignore
/// // This example compiles but is not run (e.g., needs external service)
/// let client = connect_to_db();
/// ```
```

---

## Linking and Re-exports

### Linking to other items

```rust
/// See also: [`compute`] for the main algorithm.
///
/// For more details, check the [module-level docs](crate::algorithms).
///
/// Reference: [Rust Book](https://doc.rust-lang.org/book/)
pub fn helper() {}
```

### Documenting re-exports

```rust
// lib.rs
pub use internal::Helper;  // rustdoc shows Helper in the top-level docs

// By default, rustdoc shows the original docs from internal::Helper
// Use #[doc(inline)] or #[doc(no_inline)] to control this
```

---

## Crate-Level Docs

```rust
//! # My Crate
//!
//! `my_crate` provides tools for data processing.
//!
//! ## Quick Start
//!
//! ```rust
//! use my_crate::Processor;
//! let mut p = Processor::new();
//! p.process("data.txt")?;
//! # Ok::<(), Box<dyn std::error::Error>>(())
//! ```
//!
//! ## Feature Flags
//!
//! - `serde` (default): enable serialization support
//! - `nightly`: use unstable features

#![doc(html_logo_url = "https://example.com/logo.png")]
#![doc(html_root_url = "https://docs.rs/my-crate")]
```

---

## Pitfalls

### Stale doc examples

Doc tests catch stale examples — if the API changes, the doc test fails. Always run `cargo test` after API changes.

### Missing `# Safety` sections for unsafe functions

```rust
/// # Safety
///
/// `ptr` must be non-null, aligned, and point to a valid `T`.
pub unsafe fn dangerous(ptr: *const u8) {}
```

### Over-documenting internals

Public API docs should focus on *how to use* the API, not how it's implemented:

```rust
// BAD — implementation detail in docs
/// Allocates a Vec with capacity 42, then...
pub fn process() {}

// GOOD — user-focused
/// Processes the input data and returns results.
pub fn process() -> Vec<u8> {}
```

---

> [!question]- Interview Questions
>
> **Q: What is the difference between `///` and `//!`?**
> A: `///` documents the following item (function, struct, trait). `//!` documents the containing item (crate or module).
>
> **Q: How do doc tests work?**
> A: Code blocks in `///` comments are compiled and run by `cargo test`. `# ` prefix hides lines from rendered docs. Use `should_panic` or `ignore` annotations for special cases.

---

## Cross-Links

- [[Rust/01_Foundations/06_Modules_Crates_Cargo_and_Tooling]] for `cargo doc` workflow
- [[Rust/01_Foundations/07_Testing_in_Rust]] for doc tests as part of test suite

---

## References

- [Rustdoc Book](https://doc.rust-lang.org/rustdoc/)
- [Documentation Tests](https://doc.rust-lang.org/rustdoc/documentation-tests.html)
- [Rust by Example: Documentation](https://doc.rust-lang.org/rust-by-example/meta/doc.html)
