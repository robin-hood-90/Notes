---
tags: [rust, advanced, inline-asm, miri, assembly, unsafe-testing, ub-detection]
aliases: ["Inline Assembly", "Miri", "core::arch::asm", "UB Detection", "Unsafe Testing"]
status: stable
updated: 2026-05-11
---

# Inline Assembly and Miri

> [!summary] Goal
> Use `core::arch::asm!` for architecture-specific operations and `Miri` to validate unsafe code soundness. Together they let you write low-level code with confidence.

## Table of Contents

1. [Why Inline Assembly and Miri Belong Together](#why-inline-assembly-and-miri-belong-together)
2. [Inline Assembly with asm!](#inline-assembly-with-asm)
3. [Miri for UB Detection](#miri-for-ub-detection)
4. [Pitfalls](#pitfalls)

---

## Why Inline Assembly and Miri Belong Together

Inline assembly (`asm!`) is one of the most powerful unsafe capabilities — it gives you direct CPU instruction control. Miri is one of the most important tools for checking that such low-level code is sound. Every `unsafe` block inside or next to inline assembly should be tested under Miri.

---

## Inline Assembly with asm!

> [!info] asm! macro
> `core::arch::asm!` (stabilized in Rust 1.59) provides safe-by-default inline assembly. You specify operands (inputs, outputs, clobbers) and the compiler handles register allocation, spilling, and constraints — like GCC's extended asm.

### Basic syntax

```rust
use std::arch::asm;

// Simplest form — no inputs/outputs:
unsafe {
    asm!("nop");  // No operation
}
```

### Inputs and outputs

```rust
use std::arch::asm;

let x: u64 = 42;
let mut y: u64 = 0;

unsafe {
    asm!(
        "mov {0}, {1}",  // {0} = output (y), {1} = input (x)
        out(reg) y,       // Output: y written to a register
        in(reg) x,        // Input: x read from a register
    );
}
assert_eq!(y, 42);

// Multiple operands:
let a: u64 = 10;
let b: u64 = 20;
let mut result: u64;

unsafe {
    asm!(
        "add {0}, {1}",   // result = a + b
        inout(reg) a => result,  // Input a, output result (same register)
        in(reg) b,
    );
}
```

### Register classes and constraints

```rust
// Specific registers:
unsafe {
    asm!("mov {0}, {1}",
        out(rax) _value,  // Force use of RAX
        in(rcx) input,    // Force use of RCX
    );
}

// Register classes:
//   reg  — any general-purpose register (compiler chooses)
//   eax, ebx, rcx, ... — specific register
//   xmm0, xmm1, ... — SSE register
//   v0, v1, ... — ARM NEON/SVE

// Memory operands:
unsafe {
    asm!("mov {0}, [{1}]",
        out(reg) value,    // Output in any reg
        in(reg) ptr,       // Pointer in any reg
    );
}
```

### Clobbers and options

```rust
// Clobber list: tell the compiler which registers are modified
unsafe {
    asm!(
        "cpuid",
        out("eax") eax,
        out("ebx") ebx,
        out("ecx") ecx,
        out("edx") edx,
        // All cpuid outputs are written to specific registers
    );
}

// Symbol operands (for accessing static variables):
static GLOBAL: u64 = 42;
unsafe {
    asm!("mov {0}, [{1}]",
        out(reg) value,
        sym GLOBAL,   // Reference to the static
    );
}

// Options:
unsafe {
    asm!(
        "nop",
        options(nostack),     // Doesn't touch stack
        options(nomem),       // Doesn't access memory
        options(preserves_flags),  // Doesn't modify condition flags
        options(noreturn),    // Function never returns
        options(readonly),    // Only reads memory (no writes)
    );
}
```

### Architecture-specific examples

```rust
// x86-64: Read timestamp counter
fn rdtsc() -> u64 {
    let low: u32;
    let high: u32;
    unsafe {
        asm!(
            "rdtsc",
            out("eax") low,
            out("edx") high,
        );
    }
    ((high as u64) << 32) | low as u64
}

// ARM64: Memory barrier
fn dmb_sy() {
    unsafe {
        asm!("dmb sy", options(nomem, nostack));
    }
}

// x86-64: Pause (spin-loop hint)
fn spin_loop_hint() {
    unsafe {
        asm!("pause", options(nomem, nostack));
    }
}

// x86-64: Atomic compare-and-exchange (for illustration — use std::sync::atomic)
fn cas(ptr: *mut u64, old: u64, new: u64) -> u64 {
    let mut prev = old;
    unsafe {
        asm!(
            "lock cmpxchg [{ptr}], {new}",
            ptr = in(reg) ptr,
            new = in(reg) new,
            inout("rax") prev => prev,  // RAX = expected (old), returns actual
            options(nostack),
        );
    }
    prev  // Returns old value (or new if CAS succeeded)
}
```

### When to use inline assembly vs. `std::arch` intrinsics

```text
Prefer std::arch intrinsics when:
  - They exist (e.g., _mm256_add_epi32 for SIMD).
  - You need cross-platform support (intrinsics are portable).
  - The compiler can optimize across intrinsic boundaries.

Use asm! when:
  - No intrinsic exists (CPUID, custom instruction, CSR access).
  - You need exact instruction ordering or specific encodings.
  - Intrinsics generate suboptimal code for your pattern.
  - You're implementing architecture-specific primitives.

Always:
  - Test with Miri (when possible on your architecture).
  - Add options(nostack, nomem) when applicable.
  - Document why this can't be expressed in safe Rust.
```

---

## Miri for UB Detection

> [!info] Miri
> [Miri](https://github.com/rust-lang/miri) is an interpreter for Rust's Mid-level IR (MIR). It runs your code in a virtual machine and detects Undefined Behavior that would be invisible in normal execution — but could manifest as crashes, corruption, or security vulnerabilities.

### What Miri detects

```rust
// Miri catches ALL of these:

// 1. Buffer overflow
let v = vec![1, 2, 3];
let _ = unsafe { *v.as_ptr().add(5) };  // Miri: out-of-bounds read!

// 2. Use-after-free
let p: *const i32;
{
    let x = 42;
    p = &x;
}
let _ = unsafe { *p };  // Miri: use after free!

// 3. Uninitialized memory
let u: MaybeUninit<i32> = MaybeUninit::uninit();
let v = unsafe { u.assume_init() };  // Miri: read of uninitialized memory!

// 4. Invalid alignment
let bytes = [0u8; 16];
let ptr = bytes.as_ptr() as *const u64;
let misaligned = unsafe { &*ptr.add(1) as *const u64 };  // Miri: misaligned read!

// 5. Invalid provenance
let a = [1, 2];
let b = [3, 4];
let p = a.as_ptr() as usize;
let q = p as *const i32;
let _ = unsafe { *q.add(2) };  // Miri: provenance violation!
```

### Running Miri in CI

```yaml
# .github/workflows/ci.yml
jobs:
  miri:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: nightly
          components: miri
      - name: Run tests under Miri
        run: cargo +nightly miri test
        env:
          MIRIFLAGS: "-Zmiri-strict-provenance"
```

### Miri flags

```bash
# Strict provenance checking:
MIRIFLAGS="-Zmiri-strict-provenance" cargo +nightly miri test

# Track specific allocations:
MIRIFLAGS="-Zmiri-tag-raw-pointers" cargo +nightly miri test

# Retag fields (for advanced aliasing checks):
MIRIFLAGS="-Zmiri-retag-fields" cargo +nightly miri test

# Per-object provenance (weaker than strict):
MIRIFLAGS="-Zmiri-permissive-provenance" cargo +nightly miri test

# Suppress errors (for gradual migration):
MIRIFLAGS="-Zmiri-suppress-ub-error" cargo +nightly miri test

# Ignore leaks (Miri detects memory leaks by default):
MIRIFLAGS="-Zmiri-ignore-leaks" cargo +nightly miri test

# Set the number of CPUs (Miri simulates concurrency):
MIRIFLAGS="-Zmiri-num-cpus=4" cargo +nightly miri test
```

### Testing strategy for unsafe code

```rust
// For every unsafe function, provide:
// 1. SAFETY docs explaining invariants
// 2. Tests under Miri that exercise the safety boundaries

/// SAFETY:
/// - `ptr` must be non-null and aligned to `align_of::<T>()`
/// - `ptr` must point to valid, initialized `T`
/// - The caller must ensure no aliasing violations
unsafe fn read_and_drop<T>(ptr: *mut T) -> T {
    let val = std::ptr::read(ptr);
    // After read, memory is logically uninitialized
    val
}

#[cfg(miri)]
#[test]
fn test_read_and_drop_smoke() {
    let x = Box::new(42);
    let ptr = Box::into_raw(x);
    let val = unsafe { read_and_drop(ptr) };
    assert_eq!(val, 42);
    // Box was already "dropped" by into_raw, no memory leak
}

// Miri-based property testing:
#[cfg(miri)]
proptest::proptest! {
    #![proptest_config = proptest::prelude::ProptestConfig::with_cases(100)]
    #[test]
    fn test_read_doesnt_crash(x: i32) {
        let v = Box::new(x);
        let p = Box::into_raw(v);
        let result = unsafe { std::ptr::read(p) };
        assert_eq!(result, x);
    }
}

// NOTE: property tests under Miri are slow — run a small subset.
// Run the full suite on normal Rust, and a reduced set under Miri.
```

### Integrating `loom` for concurrent UB detection

```rust
// loom (https://github.com/tokio-rs/loom) is like Miri for concurrency.
// It systematically explores thread interleavings to find data races
// and deadlocks. Use it alongside Miri for concurrent unsafe code.

// loom replacements for std types:
// loom::thread::spawn       instead of std::thread::spawn
// loom::sync::Mutex         instead of std::sync::Mutex
// loom::sync::AtomicBool    instead of std::sync::atomic::AtomicBool
// loom::cell::UnsafeCell    instead of std::cell::UnsafeCell

#[cfg(loom)]
#[test]
fn concurrent_unsafe_test() {
    loom::model(|| {
        let data = loom::sync::Arc::new(loom::cell::UnsafeCell::new(0));
        let data2 = data.clone();

        loom::thread::spawn(move || {
            unsafe { *data2.get() = 42; }
        });

        unsafe { *data.get() = 10; }
        // loom explores all possible interleavings
    });
}
```

---

## Pitfalls

### Miri can't detect all UB

Miri uses the Tree Borrows or Stacked Borrows aliasing model. Some valid programs under one model may be UB under the other. Miri also can't detect: deadlocks (use `loom`), data races (use `loom`), or platform-specific UB that depends on the hardware.

### Forgetting to run Miri on tests that exercise unsafe code

If your tests pass normally but you have unsafe code, you may have latent UB. Add a CI job that runs `cargo +nightly miri test` — even if only a subset of tests.

### Inline assembly is inherently unportable

`asm!` blocks are architecture-specific. Gate them with `#[cfg(target_arch = "...")]` and provide safe Rust fallbacks.

### `options(nostack)` doesn't mean your asm is stack-free

If the compiler can't verify the claim, it may spill registers to the stack anyway. Use `options(nostack)` only when you're certain the asm doesn't touch the stack.

### Clobber lists must be complete

If your asm modifies a register that's not in the clobber list, the compiler may allocate that register to hold a value — corrupting it. Always list every register your asm modifies.

---

## Cross-Links

- [[Rust/03_Advanced/02_Unsafe_Rust_and_FFI_Basics]] for unsafe fundamentals and catch_unwind
- [[Rust/03_Advanced/15_MaybeUninit_NonNull_and_Raw_Pointer_Patterns]] for raw pointer patterns
- [[Rust/03_Advanced/07_Memory_Layout_and_repr_Attributes]] for layout constraints relevant to asm
