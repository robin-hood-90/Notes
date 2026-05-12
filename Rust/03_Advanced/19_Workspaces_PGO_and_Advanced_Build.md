---
tags: [rust, advanced, cargo, workspaces, pgo, bolt, build-optimization, profile-guided]
aliases: ["Workspaces", "PGO", "BOLT", "Advanced Build", "Cargo Features", "Profile-Guided Optimization"]
status: stable
updated: 2026-05-11
---

# Workspaces, PGO, and Advanced Build

> [!summary] Goal
> Master Cargo workspace management, Profile-Guided Optimization (PGO), BOLT binary optimization, and advanced build techniques for production Rust projects.

## Table of Contents

1. [Why Advanced Build Matters](#why-advanced-build-matters)
2. [Cargo Workspaces](#cargo-workspaces)
3. [Profile-Guided Optimization (PGO)](#profile-guided-optimization)
4. [BOLT Binary Optimization](#bolt-binary-optimization)
5. [Advanced Cargo Features](#advanced-cargo-features)
6. [Pitfalls](#pitfalls)

---

## Why Advanced Build Matters

For large Rust projects, the default `cargo build --release` leaves significant performance on the table:
- **Workspaces** manage multi-crate repos with shared dependencies and build cache.
- **PGO** can improve throughput by 10-20% by using runtime profile data to guide inlining, branch layout, and function ordering.
- **BOLT** can improve binary performance by 5-15% by optimizing the layout of the compiled binary.
- **Cargo features** and `[patch]` control dependency resolution.

---

## Cargo Workspaces

> [!info] Workspace
> A Cargo workspace is a set of crates that share a common `Cargo.lock` and target directory. All crates in a workspace build with consistent dependency versions and share compiled artifacts when possible.

### Workspace layout

```toml
# Root Cargo.toml
[workspace]
members = [
    "crates/core",
    "crates/api",
    "crates/cli",
    "crates/macros",
]

# Optional: workspace-level metadata
[workspace.package]
version = "0.1.0"
edition = "2021"
authors = ["My Team"]

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
tracing = "0.1"
```

### Directory structure

```
my-project/
├── Cargo.toml              # Workspace definition
├── Cargo.lock              # Shared lockfile
├── crates/
│   ├── core/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   ├── api/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   ├── cli/
│   │   ├── Cargo.toml
│   │   └── src/main.rs
│   └── macros/
│       ├── Cargo.toml
│       └── src/lib.rs
├── examples/
└── tests/
```

### Inheriting dependencies from workspace

```toml
# crates/api/Cargo.toml
[package]
name = "my-api"
version.workspace = true
edition.workspace = true

[dependencies]
serde.workspace = true    # Inherits from workspace
tokio.workspace = true
tracing.workspace = true
```

### Workspace commands

```bash
# Build all workspace members
cargo build --workspace

# Test all members
cargo test --workspace

# Build only specific member
cargo build -p my-api

# Run only specific member's tests
cargo test -p my-core

# Run a command in every workspace member
cargo check --workspace
cargo clippy --workspace
cargo fmt --all

# Update all dependencies
cargo update --workspace
```

### Default members

```toml
# In root Cargo.toml — set default members for `cargo build` (without --workspace)
[workspace]
members = ["crates/core", "crates/api", "crates/cli"]
default-members = ["crates/cli"]
# `cargo build` builds only crates/cli
# `cargo build --workspace` builds all
```

---

## Profile-Guided Optimization (PGO)

> [!info] PGO
> Profile-Guided Optimization uses runtime profiling data to guide compiler decisions: which functions to inline, which branches are hot/cold, function layout for cache efficiency, and more. For Rust, PGO typically improves throughput by 10-20%.

### PGO workflow (3 steps)

```bash
# Step 1: Build with instrumentation
RUSTFLAGS="-Cprofile-generate=/tmp/pgo-data" \
    cargo build --release --target=x86_64-unknown-linux-gnu

# Step 2: Run the instrumented binary on representative workloads
./target/release/my-app --benchmark-data /path/to/data

# Step 3: Rebuild using the profile data
RUSTFLAGS="-Cprofile-use=/tmp/pgo-data -Cllvm-args=-pgo-warn-missing" \
    cargo build --release --target=x86_64-unknown-linux-gnu
```

### PGO best practices

```bash
# Use multiple training runs for better coverage
RUSTFLAGS="-Cprofile-generate=/tmp/pgo-data" \
    cargo build --release
./target/release/my-app train-run-1
./target/release/my-app train-run-2
./target/release/my-app train-run-3

# Merge profiles (LLVM does this automatically with the same directory)

# For the optimized build:
# -Cllvm-args=-pgo-warn-missing: warn if profile data is incomplete
# If you see many warnings, your training data doesn't cover enough of the code.
RUSTFLAGS="-Cprofile-use=/tmp/pgo-data -Cllvm-args=-pgo-warn-missing" \
    cargo build --release

# For CI: cache the profile data
# Save /tmp/pgo-data as a CI artifact from the training job
# Restore it for the optimized build job
```

### Training data quality

```text
PGO quality depends on training data quality:

✅ Good training data:
  - Covers all major code paths (request types, error paths, startup)
  - Uses production-like data sizes and access patterns
  - Runs long enough to trigger JIT warmup (if applicable)
  - Multiple runs with different inputs

❌ Bad training data:
  - Only exercises the happy path (cold paths won't be optimized)
  - Uses trivial inputs (branch predictors learn wrong patterns)
  - Too short (profile noise dominates)
  - Doesn't match production workload shape

Rule: profile with the workload you'll actually run in production.
If your production workload changes, regenerating PGO data is needed.
```

### PGO in CI

```yaml
# .github/workflows/release.yml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          RUSTFLAGS="-Cprofile-generate=$PWD/pgo-data" \
            cargo build --release
          ./target/release/my-app --train
      - uses: actions/upload-artifact@v4
        with:
          name: pgo-data
          path: pgo-data/

  build:
    runs-on: ubuntu-latest
    needs: train
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: pgo-data
      - run: |
          RUSTFLAGS="-Cprofile-use=$PWD/pgo-data" \
            cargo build --release
```

---

## BOLT Binary Optimization

> [!info] BOLT
> BOLT (Binary Optimization and Layout Tool) by Meta post-processes compiled binaries to optimize code layout for cache efficiency. It reorders functions, basic blocks, and improves indirect branch prediction. On top of PGO, BOLT can add 5-15% improvement.

### Installing BOLT

```bash
# BOLT ships with LLVM 15+. Install via:
# apt: llvm-15 bolt-15
# Or build from source: https://github.com/llvm/llvm-project/tree/main/bolt

# Verify installation:
llvm-bolt --version
```

### BOLT workflow

```bash
# Step 1: Build with perf integration
RUSTFLAGS="-C link-arg=-Wl,--emit-relocs" \
    cargo build --release

# Step 2: Collect perf data
perf record -e cycles:u -j any,u -o perf.data \
    ./target/release/my-app --benchmark

# Step 3: Convert perf data to BOLT format
perf2bolt ./target/release/my-app \
    -p perf.data \
    -o bolt.fdata

# Step 4: Optimize the binary with BOLT
llvm-bolt ./target/release/my-app \
    -o ./target/release/my-app-bolted \
    -data bolt.fdata \
    -reorder-blocks=ext-tsp \
    -reorder-functions=hfsort \
    -split-functions=3 \
    -split-all-cold \
    -icf=1 \
    -use-gnu-stack

# Step 5: Compare performance
# Without BOLT:
perf stat ./target/release/my-app --benchmark
# With BOLT:
perf stat ./target/release/my-app-bolted --benchmark
```

### BOLT flags explained

```bash
# -reorder-blocks=ext-tsp: Reorder basic blocks within functions
#   (ext-tsp = extended TSP solver, best quality)
# -reorder-functions=hfsort: Reorder functions based on call frequency
#   (hot functions grouped together → better icache locality)
# -split-functions=3: Split functions into hot/cold regions
#   (cold code moved away from hot path → better icache use)
# -split-all-cold: Move all cold basic blocks to separate section
# -icf=1: Identical Code Folding (merge identical functions)
# -use-gnu-stack: Mark stack as executable (if needed)
```

---

## Advanced Cargo Features

### `[patch]` — overriding dependencies

```toml
# Override a dependency for testing or patching
[patch.crates-io]
# Use a local git checkout instead of crates.io
serde = { git = "https://github.com/serde-rs/serde", branch = "my-fix" }

# Patch with a local path
my-crate = { path = "../my-crate-fork" }

# Patch works across the entire workspace —
# if any crate in the workspace depends on serde, it gets the patched version.
```

### `[replace]` — deprecated, use `[patch]`

```toml
# [replace] was the old (deprecated) mechanism.
# Always use [patch] for overrides.
```

### Feature resolution and unification

```rust
// Cargo unifies features across the dependency graph.
// If crate A depends on tokio with feature "full" and
// crate B depends on tokio with feature "rt",
// tokio is built once with features ["full", "rt"].

// This means features are ADDITIVE.
// A feature MUST NOT break compilation when enabled.

// ❌ Bad feature:
#[cfg(feature = "slow-path")]
fn do_something() { /* ... */ }
#[cfg(not(feature = "slow-path"))]
fn do_something() { /* ... */ }
// Error: both functions exist when feature is NOT set

// ✅ Good feature:
#[cfg(feature = "slow-path")]
fn do_something() { /* ... */ }
#[cfg(not(feature = "slow-path"))]
fn do_something_else() { /* ... */ }
```

### Conditional compilation with `cfg`

```rust
// Platform-specific code
#[cfg(target_os = "linux")]
fn platform_init() { /* linux-specific */ }

#[cfg(target_os = "macos")]
fn platform_init() { /* mac-specific */ }

#[cfg(not(target_os = "windows"))]
fn fallback_path() -> &'static str { "/tmp" }

// Feature-gated code
#[cfg(feature = "metrics")]
fn emit_metrics() { /* ... */ }

// cfg_attr — conditionally apply attributes
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
struct MyStruct;

// cfg! — runtime check (no conditional compilation)
if cfg!(target_os = "linux") {
    println!("Running on Linux");
}
```

### Cargo config profiles

```toml
# .cargo/config.toml

# Override for specific targets
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "target-cpu=native"]

# Per-profile settings
[profile.release]
opt-level = 3
lto = "fat"          # Link-time optimization (fat = full, thin = faster)
codegen-units = 1    # Better optimization at cost of compile time
strip = "symbols"    # Remove debug symbols from release binary
panic = "abort"      # No unwind tables (smaller binary, faster)
```

### Build cache optimization

```bash
# Shared build cache (for CI or team)
# Set CARGO_TARGET_DIR to a shared location
export CARGO_TARGET_DIR=/shared/cache/target

# sccache — distributed compiler cache
# Install: cargo install sccache
export RUSTC_WRAPPER=sccache
# First build: slow. Subsequent builds: fast (even on different machines).

# For CI: use GitHub Actions cache for Cargo
# actions/cache with key: ${{ hashFiles('**/Cargo.lock') }}
```

---

## Pitfalls

### PGO without representative training data

PGO optimized only the paths you trained on. If your training doesn't cover error paths, startup, or rare request types, those paths may run SLOWER than without PGO (because the compiler assumes they're never executed).

### BOLT adds build complexity

BOLT requires perf data collection and post-processing. For many projects, PGO alone (without BOLT) gives 80% of the benefit with 20% of the complexity. Add BOLT only after PGO and profiling show it's needed.

### Workspace `[patch]` doesn't apply to `cargo publish`

When publishing a crate, `[patch]` sections are ignored. Use workspace-level `[patch]` only for local development/testing.

### Feature explosion with additive features

If every crate in a workspace adds features, the total number of feature combinations grows exponentially. Keep features minimal and well-documented. Use `cargo features` to audit.

---

## Cross-Links

- [[Rust/01_Foundations/06_Modules_Crates_Cargo_and_Tooling]] for Cargo basics
- [[Rust/03_Advanced/11_Cargo_Features_and_Conditional_Compilation]] for feature details
- [[Rust/03_Advanced/03_Performance_Profiling_and_Allocation]] for profiling methodology
