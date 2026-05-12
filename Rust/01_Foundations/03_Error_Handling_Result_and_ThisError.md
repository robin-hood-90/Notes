---
tags: [rust, foundations, errors, result, option]
aliases: ["Rust Error Handling", "Result", "Error Handling in Rust"]
status: stable
updated: 2026-04-28
---

# Error Handling: `Result`, `?`, and Context

> [!summary] Goal
> Model failure explicitly, propagate errors ergonomically, and design error types that remain useful at both development time and production time.

## Table of Contents

1. [Why Rust Error Handling Is Different](#why-rust-error-handling-is-different)
2. [Recoverable vs Unrecoverable Failure](#recoverable-vs-unrecoverable-failure)
3. [Result and Option](#result-and-option)
4. [The `?` Operator](#the-operator)
5. [Designing Error Types](#designing-error-types)
6. [Context and Error Layers](#context-and-error-layers)
7. [thiserror and anyhow](#thiserror-and-anyhow)
8. [Pitfalls](#pitfalls)

---

## Why Rust Error Handling Is Different

Rust does not use exceptions for ordinary failure handling.

Instead, fallible operations usually return values like:
- `Option<T>` when something may be absent
- `Result<T, E>` when something may fail with an error

This means failure is part of the type signature and API contract.

---

## Recoverable vs Unrecoverable Failure

### Recoverable

Examples:
- file not found
- parse error
- HTTP timeout
- invalid user input

These should usually be represented with `Result`.

### Unrecoverable

Examples:
- violated internal invariant
- impossible branch reached
- bug in assumptions

These may justify `panic!`, but panics should not be your ordinary control flow for expected failures.

---

## Result and Option

### `Result<T, E>`

```rust
fn parse_id(s: &str) -> Result<i64, std::num::ParseIntError> {
    s.parse::<i64>()
}
```

### `Option<T>`

Use when there is no error story, only presence or absence.

```rust
fn first_char(s: &str) -> Option<char> {
    s.chars().next()
}
```

### Important difference

- `Option<T>` means “maybe no value, and that is expected”
- `Result<T, E>` means “operation can fail, and failure has a reason”

---

## The `?` Operator

`?` is one of the most important ergonomic tools in Rust.

What it does:
- on success, unwraps the `Ok` / `Some`
- on failure, returns early from the current function with the error/absence

```rust
fn read_file(path: &std::path::Path) -> std::io::Result<String> {
    let s = std::fs::read_to_string(path)?;
    Ok(s)
}
```

### Mental expansion

```rust
let s = match std::fs::read_to_string(path) {
    Ok(value) => value,
    Err(err) => return Err(err),
};
```

This is why `?` keeps Rust code readable while still making failure explicit.

---

## Designing Error Types

Use enums for domain/application errors.

```rust
#[derive(Debug)]
enum LoadUserError {
    NotFound,
    InvalidId(std::num::ParseIntError),
    Io(std::io::Error),
}
```

### Why enums are a good fit

- finite explicit failure cases
- pattern matching on error categories
- easy to attach source errors

### Good design principles

- preserve original causes where useful
- add boundary context
- distinguish user/input errors from infra/system errors
- avoid over-fragmenting into dozens of tiny error types without handling value

---

## Context and Error Layers

As errors cross layers, they usually need more context.

Example layers:
- parser layer
- repository/client layer
- service layer
- CLI or HTTP boundary

```mermaid
flowchart LR
    A[low-level IO error] --> B[domain-specific error enum]
    B --> C[boundary adds context]
    C --> D[user-facing log / response / CLI message]
```

### Example

```rust
fn load_config(path: &std::path::Path) -> Result<String, std::io::Error> {
    std::fs::read_to_string(path)
}
```

At a higher layer, you may add context such as which config file or command failed.

---

## thiserror and anyhow

### `thiserror`

Best when you want typed errors.

```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("user not found")]
    NotFound,

    #[error("io failure: {0}")]
    Io(#[from] std::io::Error),
}
```

Good for:
- libraries
- service/domain layers
- places where callers need to branch on error categories

### `anyhow`

Good for application binaries where ergonomic error propagation matters more than exposing typed error APIs.

```rust
use anyhow::{Context, Result};

fn run() -> Result<()> {
    let config = std::fs::read_to_string("app.toml")
        .context("failed to read app.toml")?;
    println!("{config}");
    Ok(())
}
```

Good for:
- CLIs
- top-level orchestration code
- application entrypoints

---

## Pitfalls

### Using `panic!` for ordinary failure

This usually makes programs less robust and less composable.

### Erasing useful distinctions too early

If everything becomes “something failed,” callers lose the ability to respond meaningfully.

### Adding no context at boundaries

Raw low-level errors often become much more useful when wrapped with file path, user id, command name, or external dependency context.

### Using `Option` where a real error matters

If callers need to know *why* something failed, use `Result`, not `Option`.

---

> [!question]- Interview Questions
>
> **Q: When should you use `Option` instead of `Result`?**
> A: Use `Option` when absence is expected and no error explanation is needed. Use `Result` when failure has a meaningful reason.
>
> **Q: What does the `?` operator do?**
> A: It unwraps success values and returns early on failure, propagating the error upward.
>
> **Q: When is `thiserror` better than `anyhow`?**
> A: When you need typed, structured errors that callers can match on.
>
> **Q: When is `anyhow` a good fit?**
> A: For binaries and application entrypoints where ergonomic propagation and contextual messages matter more than typed error APIs.

---

## Cross-Links

- [[Rust/01_Foundations/02_Structs_Enums_and_Pattern_Matching]]
- [[Rust/04_Playbooks/02_Debug_Panic_Backtraces_and_Error_Contexts]]

---

## References

- [Recoverable Errors with Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)
- [The `?` Operator](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#propagating-errors)
- [thiserror](https://docs.rs/thiserror/)
- [anyhow](https://docs.rs/anyhow/)
