---
tags: [rust, foundations, edition, migration, cargo, tooling]
aliases: ["Edition Migration", "Rust Editions", "cargo fix", "Edition 2021", "Edition 2024"]
status: stable
updated: 2026-05-03
---

# Rust Editions

> [!summary] Goal
> Navigate Rust editions and migrate codebases between them safely.

## Table of Contents

1. [Why Editions Exist](#why-editions-exist)
2. [Edition Changes Overview](#edition-changes-overview)
3. [Migrating with `cargo fix`](#migrating-with-cargo-fix)
4. [Pitfalls](#pitfalls)

---

## Why Editions Exist

Rust editions allow the language to evolve without breaking existing code. Each edition is a set of opt-in breaking changes.

```toml
[package]
name = "my-crate"
edition = "2021"  # or "2015", "2018"
```

> [!tip] Definition
> **Edition**: a milestone in Rust's evolution where the language may introduce non-backward-compatible changes. Older editions continue to compile without changes. Crates in different editions can interoperate.

---

## Edition Changes Overview

| Edition | Key Changes |
|---------|-------------|
| **2015** | Original Rust 1.0 edition. Default for crates without an edition field. |
| **2018** | Module system (`use` paths), NLL borrow checker, `impl Trait`, `dyn Trait`, `..=` inclusive ranges, `?` operator. |
| **2021** | `Cargo.toml` edition field required, closures capture disjoint fields, `TryInto`/`TryFrom` prelude, const generics MVP, array `IntoIterator`. |
| **2024** | `!` fallback type changes, unsafe attributes, `unsafe_op_in_unsafe_fn` warning becomes error. |

---

## Migrating with `cargo fix`

```bash
# Check your current edition
grep edition Cargo.toml

# Run the automated migration
cargo fix --edition  # prepares code for the next edition
cargo build          # verify it compiles

# Update Cargo.toml
# Change edition = "2018" to edition = "2021"

# Run again to pick up any remaining changes
cargo fix --edition
cargo build
cargo test
```

---

## Pitfalls

### Mixed editions

```rust
// Crate A (edition 2021) can depend on Crate B (edition 2018)
// No issues — editions are per-crate
```

### `cargo fix` doesn't catch everything

Some changes require manual inspection (e.g., `async` keyword conflicts, `try` reserved).

### Edition is per-crate, not per-project

In a workspace, each crate can have a different edition. Run `cargo fix` in each.

---

## Cross-Links

- [[Rust/01_Foundations/06_Modules_Crates_Cargo_and_Tooling]] for Cargo workflow
- [[Rust/03_Advanced/11_Cargo_Features_and_Conditional_Compilation]] for target-specific code

---

## References

- [Edition Guide](https://doc.rust-lang.org/edition-guide/)
- [cargo fix](https://doc.rust-lang.org/cargo/commands/cargo-fix.html)
