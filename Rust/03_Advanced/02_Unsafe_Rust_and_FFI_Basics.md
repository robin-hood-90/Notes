---
tags: [rust, advanced, unsafe, ffi, maybeuninit, nonnull, inline-asm, miri]
aliases: ["Unsafe Rust Deep Dive", "FFI", "MaybeUninit", "NonNull", "Inline Assembly", "Miri"]
status: stable
updated: 2026-05-11
---

# Unsafe Rust, FFI, and Low-Level Patterns

> [!summary] Goal
> Understand what `unsafe` means at the language level, master tools for safe unsafe code (`MaybeUninit`, `NonNull`), handle FFI correctly, use inline assembly when needed, and validate soundness with Miri.

## Table of Contents

1. [What unsafe Means](#what-unsafe-means)
2. [Raw Pointer Mental Model](#raw-pointer-mental-model)
3. [MaybeUninit](#when-not-to-use-maybeuninit)
4. [NonNull](#nonnull)
5. [Unsafe Trait Implementations](#unsafe-trait-implementations)
6. [Inline Assembly](#inline-assembly)
7. [catch_unwind and Poisoning](#catchunwind-and-poisoning)
8. [FFI Safety Patterns](#ffi-safety-patterns)
9. [Testing Unsafe Code with Miri](#testing-unsafe-code-with-miri)
10. [Pitfalls](#pitfalls)

---

## What `unsafe` Means

> [!info] Unsafe
> `unsafe` does NOT turn off the compiler, borrow checker, or type system. It grants access to five specific capabilities that the compiler cannot prove safe, and YOU must uphold the invariants.

### The five unsafe capabilities

1. **Dereference a raw pointer** (`*const T`, `*mut T`)
2. **Call an unsafe function** (including `extern` functions)
3. **Access or modify a mutable static** (`static mut`)
4. **Implement an unsafe trait** (like `Send`, `Sync`)
5. **Access fields of unions**

```rust
// Every unsafe block must come with a // SAFETY: comment explaining
// why the operation is correct.

let mut x = 10;
let r = &mut x as *mut i32;

unsafe {
    // SAFETY: r points to x, which is valid and properly aligned
    *r = 20;
}
```

### Safety invariants vs correctness invariants

```text
Safety invariant: a property the compiler assumes is always true for a type.
  - Example: &T is always non-null, aligned, and points to valid initialized data.
  - If you break this, you get UB immediately.

Correctness invariant: a property your API requires but does NOT cause UB
  if violated (just wrong results).
  - Example: HashMap's load factor stays balanced.
  - Violating this doesn't cause UB, just worse performance.

In unsafe code, you must uphold ALL safety invariants. The price of failure is UB.
```

---

## Raw Pointer Mental Model

```rust
// Two raw pointer types:
// *const T — immutable, may be null or dangling
// *mut T   — mutable, (conceptually) uniquely writable

let x = 10;
let p: *const i32 = &x;  // Created from a reference — valid pointer
let null: *const i32 = std::ptr::null();  // Null pointer

// Dereferencing is unsafe:
unsafe {
    println!("{}", *p);   // OK: p is valid
    // println!("{}", *null);  // UB! dereferencing null
}

// *mut T is INVARIANT (see A01 for variance rules):
// *const T is COVARIANT (like &T)
```

### Pointer provenance

```rust
// Pointer provenance: a pointer is only valid for accesses that derive
// from the original allocation. You cannot:
//   1. Take address of one allocation
//   2. Cast to an integer, add an offset, cast back
//   3. Access a DIFFERENT allocation through this pointer

let a = [1, 2, 3];
let b = [4, 5, 6];

let p = &a as *const i32;
// let q = unsafe { &*p.add(3) };  // UB! p only covers a's 3 elements
// Even if a happens to be adjacent to b in memory, this is UB (provenance).

// The compiler uses provenance to optimize — assuming two pointers from
// different allocations never alias. Breaking provenance breaks the optimizer.
```

### `std::ptr` operations

```rust
use std::ptr;

let mut x = 42;
let p = &mut x as *mut i32;

unsafe {
    // Read value
    let val = ptr::read(p);        // Copy value out (like *p)
    
    // Write value (does NOT drop old value)
    ptr::write(p, 100);            // Overwrites x with 100
    
    // Swap values
    let mut y = 0;
    ptr::swap(p, &mut y as *mut i32);  // x=0, y=100
    
    // Replace (drop old value, write new)
    let old = ptr::replace(p, 200);    // old=0, x=200
    
    // Drop in place
    let s = String::from("hello");
    let ps = &s as *const String;
    ptr::drop_in_place(ps as *mut String);  // Runs ~String destructor
    // After this, s is NOT safe to use (memory is uninitialized)
}
```

---

## `MaybeUninit<T>`

> [!info] MaybeUninit
> `MaybeUninit<T>` is a union-based type that represents potentially uninitialized memory of type `T`. It replaced `mem::uninitialized()` (which was UB for most types) and `mem::zeroed()` (which was also UB for types where all-zeros is invalid).

### Creating and using uninitialized memory

```rust
use std::mem::MaybeUninit;

// Stack allocation without initialization
let mut uninit: MaybeUninit<[i32; 1000]> = MaybeUninit::uninit();

// Initialize via pointer write
let p = uninit.as_mut_ptr();
unsafe {
    for i in 0..1000 {
        (*p)[i] = i as i32;      // Initialize each element
    }
}

// Assume it's initialized — SAFETY: we initialized all 1000 values
let initialized: [i32; 1000] = unsafe { uninit.assume_init() };

// Common pattern: initialize field-by-field
struct Large {
    x: i64,
    y: i64,
    buf: [u8; 4096],
}

let mut large = MaybeUninit::<Large>::uninit();
let ptr = large.as_mut_ptr();

unsafe {
    // SAFETY: ptr is valid and properly aligned
    (*ptr).x = 1;
    (*ptr).y = 2;
    (*ptr).buf.fill(0);
    let large = large.assume_init();  // Now fully initialized
}
```

### Array initialization without `Vec` overhead

```rust
// Before Rust 1.63, you couldn't initialize arrays from iterators directly.
// MaybeUninit solves this:

fn init_array<T, F>(mut f: F) -> [T; 1024]
where
    F: FnMut(usize) -> T,
{
    // Create uninitialized array
    let mut arr: [MaybeUninit<T>; 1024] =
        unsafe { MaybeUninit::uninit().assume_init() };
    // NOTE: initializing [MaybeUninit; 1024] from MaybeUninit::uninit() is fine
    // because MaybeUninit can be "uninitialized" — no UB.

    for (i, elem) in arr.iter_mut().enumerate() {
        elem.write(f(i));  // write() initializes the MaybeUninit
    }

    // SAFETY: all elements were initialized above
    unsafe { std::mem::transmute::<_, [T; 1024]>(arr) }
}
```

### When NOT to use `MaybeUninit`

```rust
// Don't use MaybeUninit for:
// 1. Simple Option patterns — just use Option<T>
// 2. Lazy initialization — use OnceCell, OnceLock, or LazyLock
// 3. Default values — #[derive(Default)] or T::default()

// MaybeUninit is for performance-critical cases where:
//   - You MUST avoid zero-initialization overhead
//   - You're constructing large arrays element-by-element
//   - You're working with FFI buffers that C fills in
```

---

## `NonNull<T>`

> [!info] NonNull
> `NonNull<T>` is a raw pointer wrapper that guarantees non-nullness. It's the pointer equivalent of `&T` (non-null) but without lifetime or aliasing guarantees. It carries the niche optimization (like `Option<NonNull<T>>` is the same size as `*mut T`).

```rust
use std::ptr::NonNull;

// Creating NonNull
let mut x = 42;
let nn = NonNull::new(&mut x);           // Some(NonNull)
let nn_from_ptr = NonNull::new(&mut x as *mut i32); // Some(NonNull)
let null_nn = NonNull::new::<i32>(std::ptr::null_mut()); // None

// Dereferencing
let val = unsafe { nn.unwrap().as_ref() };   // &i32
let mut_val = unsafe { nn.unwrap().as_mut() }; // &mut i32

// Where NonNull is used in std:
//   - Box<T>:           Internally stores NonNull<T>
//   - Rc<T>, Arc<T>:    Internally stores NonNull<T>
//   - Vec<T>:            Internally uses NonNull<T> for buffer
//   - String:            Same as Vec
//   - HashMap:           NonNull for table entries

// Niche optimization:
// NonNull<T> is a *mut T that can't be null.
// Option<NonNull<T>> = *mut T (no extra discriminant byte!)
// This is why Option<Box<T>> is the same size as Box<T>.
assert_eq!(
    std::mem::size_of::<Option<NonNull<i32>>>(),
    std::mem::size_of::<*mut i32>(),
);
```

### When to use NonNull vs raw pointers

```rust
// Use *const T / *mut T when:
//   - Null is a valid and expected value
//   - You're writing FFI and C can legitimately return NULL

// Use NonNull<T> when:
//   - You want to codify "this pointer is never null"
//   - You want Option<NonNull<T>> to be pointer-sized
//   - You're building a safe abstraction over raw pointers
//   - You need to store a pointer in a struct but can't use references
//     (because references carry lifetime/aliasing rules that don't fit)

// Unsafe struct example:
struct MyVec<T> {
    ptr: NonNull<T>,         // Never null, even for empty Vec (has a valid aligned addr)
    len: usize,
    cap: usize,
}

// With raw pointer: every use must check for null
// With NonNull: compiler enforces non-nullness in safe code
```

---

## Unsafe Trait Implementations

```rust
// unsafe traits: the trait has safety invariants that implementors must uphold.
// The two most common unsafe traits: Send and Sync.

// Send: T can be safely transferred to another thread.
// Sync: T can be safely shared (via &T) between threads.

// Most types are automatically Send + Sync. You only need unsafe impl
// when you're wrapping types that the compiler CAN'T prove are safe.

// Example: wrapping a raw pointer in a Send/Sync type
struct MySharedPtr<T> {
    ptr: *mut T,
}

// The compiler can't prove *mut T is Send/Sync — it might be a dangling pointer.
// But if we know it's a valid, thread-safe allocation:
unsafe impl<T> Send for MySharedPtr<T> {}
unsafe impl<T> Sync for MySharedPtr<T> {}

// Example: raw pointer to a thread-safe FFI type
struct ForeignHandle(*mut std::os::raw::c_void);

unsafe impl Send for ForeignHandle {}  // The FFI library says it's thread-safe
unsafe impl Sync for ForeignHandle {}  // OR just one, depending on the API

// ⚠️  Adding Send/Sync incorrectly can cause data races in SAFE code.
// Test with loom or careful review for thread safety.
```

---

## Inline Assembly

> [!info] Inline assembly
> Rust's `core::arch::asm!` macro (stabilized in Rust 1.59) lets you write inline assembly with operand constraints, clobbers, and register management — similar to C's `__asm__`. Available on all architectures.

```rust
use std::arch::asm;

// Basic example: read the CPU cycle counter (x86)
fn read_timestamp() -> u64 {
    let mut cycles: u64;
    unsafe {
        asm!("rdtsc", out("eax") cycles, out("edx") _);
        // rdtsc writes low 32 bits to eax, high 32 bits to edx
        // We combine them: cycles = (edx << 32) | eax
    }
    cycles
}

// Full example: x86-64 cpuid instruction
fn cpuid(leaf: u32) -> (u32, u32, u32, u32) {
    let (eax, ebx, ecx, edx);
    unsafe {
        asm!(
            "cpuid",
            in("eax") leaf,     // input: leaf in eax
            out("eax") eax,     // output: eax
            out("ebx") ebx,     // output: ebx
            out("ecx") ecx,     // output: ecx
            out("edx") edx,     // output: edx
        );
    }
    (eax, ebx, ecx, edx)
}

// ARM example: data memory barrier
fn dmb() {
    unsafe {
        asm!("dmb ish", options(nostack, nomem));
        // ish = inner shareable domain
        // options(nostack, nomem): doesn't access memory or stack
    }
}
```

### Operand types

```text
Operand        Meaning
──────────────────────────────────────────────────
in(reg) x      Pass x in a general-purpose register
out(reg) x      Read x from a register after asm
inout(reg) x    Read and write x from register
lateout(reg) x  Like out, but may reuse input registers
clobber_abi     Clobbers all registers in a calling convention
options(...)    Modifiers: nostack, nomem, readonly, preserves_flags, noreturn

Register classes:
reg              Any general-purpose register
eax, ebx, ...    Specific register
xmm0, xmm1, ...  SSE registers (x86)
v0, v1, ...      NEON/SVE registers (ARM)
```

### When to use inline assembly

```text
Use asm! when:
  - There's no equivalent in std (CPUID, custom instructions, CSR reads).
  - You need exact CPU instruction sequences (embedded, OS dev).
  - The compiler can't generate optimal code for a specific pattern.
  - You're implementing architecture-specific optimizations (SIMD, crypto).

Don't use asm! when:
  - std::arch provides a better abstraction (std::arch::x86_64::_mm_...).
  - You can express the same thing in safe Rust with similar performance.
  - You're not willing to test on every target architecture.

Always:
  - Add options(nostack, nomem) when the asm doesn't touch memory or stack.
  - Add options(preserves_flags) when the asm doesn't modify condition flags.
  - Document what each register does and why.
```

---

## `catch_unwind` and Poisoning

> [!info] catch_unwind
> `std::panic::catch_unwind` captures a panic and returns it as a `Result`. It's the Rust equivalent of `try`/`catch` for panics. Critical for FFI boundaries (to prevent panics from unwinding into C code, which is UB).

### FFI panic safety

```rust
use std::panic::catch_unwind;
use std::ffi::CString;

// ❌ BAD: if this panics, it unwinds through the C stack → UB
#[no_mangle]
pub extern "C" fn process_data(data: *const std::os::raw::c_char) -> i32 {
    let s = unsafe { std::ffi::CStr::from_ptr(data) };
    let rs = s.to_str().unwrap();  // Could panic!
    do_work(rs);
    0
}

// ✅ GOOD: catch panics before they reach C
#[no_mangle]
pub extern "C" fn process_data_safe(data: *const std::os::raw::c_char) -> i32 {
    let result = catch_unwind(|| {
        let s = unsafe { std::ffi::CStr::from_ptr(data) };
        let rs = s.to_str().map_err(|_| "invalid UTF-8")?;
        do_work(rs);
        Ok::<_, &str>(())
    });

    match result {
        Ok(Ok(())) => 0,     // Success
        Ok(Err(e)) => {      // Rust error (not a panic)
            eprintln!("{e}");
            -1
        }
        Err(panic) => {      // Panic caught
            eprintln!("Panic: {:?}", panic.downcast_ref::<&str>());
            -2
        }
    }
}
```

### Poisoning in mutexes

```rust
// std::sync::Mutex and RwLock are "poisoned" when a thread panics while
// holding the lock. After poisoning, .lock() returns Err (the poison error).

use std::sync::{Mutex, PoisonError};

let lock = Mutex::new(0);

// If a thread panics while holding the lock:
let result = std::panic::catch_unwind(|| {
    let mut guard = lock.lock().unwrap();
    *guard = panic!("crash");
});

// The lock is now poisoned:
match lock.lock() {
    Ok(mut guard) => *guard += 1,
    Err(PoisonError { .. }) => {
        // The value may be in an inconsistent state
        // You can choose to ignore the poison:
        let mut guard = lock.lock().into_inner().unwrap_or_else(|e| e.into_inner());
        *guard = 0;  // Reset to known state
    }
}
```

---

## FFI Safety Patterns

### Calling C from Rust

```rust
// Use std::ffi for string conversion
use std::ffi::{CStr, CString};
use std::os::raw::c_int;

// Import C function
extern "C" {
    fn strlen(s: *const std::os::raw::c_char) -> usize;
}

// Safe wrapper
fn safe_strlen(s: &str) -> usize {
    let cstr = CString::new(s).expect("String contains null byte");
    unsafe {
        // SAFETY: cstr is a valid C string, non-null, properly terminated
        strlen(cstr.as_ptr())
    }
}

// Handling nullable pointers from C
fn nullable_from_c(ptr: *const std::os::raw::c_char) -> Option<&str> {
    if ptr.is_null() {
        return None;
    }
    unsafe {
        // SAFETY: ptr is non-null, caller guarantees it points to valid C string
        Some(CStr::from_ptr(ptr).to_str().unwrap_or("(invalid UTF-8)"))
    }
}
```

### C calling Rust (callbacks)

```rust
// Exposing a Rust function to C with #[no_mangle] and extern "C"

// The function must be safe at the C ABI boundary:
// - Must not panic (wrap in catch_unwind)
// - Argument types must have stable ABI (repr(C) for structs)
// - No trait objects, no generics in the signature

#[repr(C)]
struct Point {
    x: f64,
    y: f64,
}

#[no_mangle]
pub extern "C" fn compute_distance(p1: *const Point, p2: *const Point) -> f64 {
    let result = std::panic::catch_unwind(|| {
        let p1 = unsafe { &*p1 };  // SAFETY: caller guarantees valid pointers
        let p2 = unsafe { &*p2 };
        ((p1.x - p2.x).powi(2) + (p1.y - p2.y).powi(2)).sqrt()
    });
    result.unwrap_or(f64::NAN)
}
```

### Ownership conventions in FFI

```text
At FFI boundaries, you MUST document who owns what.

Common convention: C side allocates, C side frees.
  - Rust side receives a pointer, copies data out, does NOT free it.
  - Use: CString::new() → .into_raw() → pass to C. C calls free().

Common convention: Rust side allocates, Rust side frees.
  - Rust side creates a CString, passes as_ptr() to C.
  - C uses it, does NOT free it.
  - When C returns, Rust side retrieves the string and drops it (or uses from_raw).

The -sys crate pattern:
  - my_library_sys: raw FFI bindings (build.rs + bindgen)
  - my_library: safe Rust wrapper over the -sys crate
  - my_library_sys handles extern blocks, my_library handles safety
```

### `extern` types (RFC 1861)

```rust
// Extern types (unstable in some contexts, stabilized for specific use cases):
// An extern type has no known size at compile time.
// All extern types are !Sized.

// Currently stable via: extern { type MyOpaque; }
// This is used for FFI where C only passes opaque pointers.

// In many cases, extern types are represented as:
//   - *mut c_void (most common, but loses type info)
//   - A zero-sized type with PhantomData (for type-safe handles)

// Alternative for opaque types — safe wrapper pattern:
mod ffi {
    use std::ffi::c_void;

    extern "C" {
        fn my_create() -> *mut c_void;
        fn my_destroy(handle: *mut c_void);
        fn my_process(handle: *mut c_void, input: i32) -> i32;
    }

    pub struct Handle {
        inner: *mut c_void,
    }

    impl Handle {
        pub fn new() -> Option<Self> {
            let ptr = unsafe { my_create() };
            if ptr.is_null() { None } else { Some(Self { inner: ptr }) }
        }

        pub fn process(&self, input: i32) -> i32 {
            unsafe { my_process(self.inner, input) }
        }
    }

    impl Drop for Handle {
        fn drop(&mut self) {
            unsafe { my_destroy(self.inner); }
        }
    }
}
```

---

## Testing Unsafe Code with Miri

> [!info] Miri
> [Miri](https://github.com/rust-lang/miri) is an interpreter for Rust's mid-level IR. It runs your code inside a virtual machine and detects Undefined Behavior: dereferencing dangling/null pointers, uninitialized memory reads, provenance violations, out-of-bounds accesses, incorrect `layout` assumptions, and more.

### Installing and running Miri

```bash
# Install (nightly required)
rustup +nightly component add miri

# Run tests with Miri
cargo +nightly miri test

# Run a specific test
cargo +nightly miri test my_unsafe_function

# Run with tree borrows (stricter aliasing model)
MIRIFLAGS="-Zmiri-tree-borrows" cargo +nightly miri test

# Run with tracking specific allocations
MIRIFLAGS="-Zmiri-tag-raw-pointers" cargo +nightly miri test
```

### What Miri catches

```rust
// Miri catches these UB patterns:

// 1. Use-after-free
unsafe {
    let p = &42 as *const i32;
    drop(Box::new(0));          // This doesn't invalidate p (stack allocation)
    // But:
    let b = Box::new(42);
    let p = &*b as *const i32;
    drop(b);                    // b is freed
    // println!("{}", *p);      // Miri catches: use-after-free!
}

// 2. Uninitialized memory reads
use std::mem::MaybeUninit;
let mut uninit = MaybeUninit::<i32>::uninit();
// let val = unsafe { uninit.assume_init() };  // Miri catches: read of uninit!

// 3. Out-of-bounds pointer access
let arr = [1, 2, 3];
let p = &arr as *const i32;
// let _ = unsafe { *p.add(5) };  // Miri catches: out-of-bounds!

// 4. Invalid alignment
let aligned = [0u8; 8];
let misaligned = unsafe { &*(aligned.as_ptr().add(1) as *const u32) };
// Miri catches: misaligned read!
```

### Testing strategy for unsafe code

```rust
// 1. Run ALL tests under Miri (CI job on nightly)
// 2. For each unsafe function, write a test that specifically exercises
//    the safety invariants

/// SAFETY: `ptr` must be non-null, aligned to align_of::<T>(),
///         and point to valid initialized data of type T.
unsafe fn read_value<T>(ptr: *const T) -> T {
    std::ptr::read(ptr)
}

// Test that Miri catches violation:
#[cfg(miri)]
#[test]
fn test_read_null_pointer() {
    let ptr: *const i32 = std::ptr::null();
    unsafe {
        // Miri will catch this — we expect it to detect UB
        let _ = read_value(ptr);
    }
}

// For soundness testing, use quickcheck + Miri:
// "If the test passes under Miri, the unsafe code is sound for that input."
```

---

## Pitfalls

### Dereferencing a raw pointer outside unsafe

Raw pointers have no borrow-checker guarantees. Wrapping a raw pointer dereference in `unsafe { }` doesn't make it safe — you must verify the pointer is valid.

### `MaybeUninit::assume_init()` without initializing all bytes

Calling `assume_init()` on partially initialized memory is UB, even for integer types. Always ensure every byte is written before assuming initialization.

### Forgetting `PhantomData` in types holding raw pointers

If you store a `*const T` but don't add `PhantomData<T>`, the compiler doesn't know your struct owns `T`. Drop order optimization may drop `T` before your struct finishes using the pointer.

### Panicking across FFI boundaries

A panic that unwinds through C frames is UB. Always wrap FFI-entry-point functions in `catch_unwind`.

---

> [!question]- Interview Questions
>
> **Q: What is the difference between *const T and &T?**
> A: `&T` is non-null, aligned, valid for the lifetime, and follows Rust's aliasing rules (no mutation during shared borrow). `*const T` has no such guarantees — it may be null, dangling, misaligned, or point to mutated data. Dereferencing `*const T` is `unsafe` because the compiler can't verify these properties.
>
> **Q: What is MaybeUninit and when should you use it?**
> A: `MaybeUninit<T>` represents potentially uninitialized memory of type `T`. Use it when: (a) you must avoid zero-initialization overhead for large arrays, (b) you're filling a buffer piece by piece in a hot path, or (c) you're receiving uninitialized memory from FFI (a C function writes into a buffer). Use `assume_init()` only after every byte has been initialized.
>
> **Q: How does Miri help with unsafe code?**
> A: Miri interprets Rust's IR and detects Undefined Behavior: use-after-free, uninitialized reads, out-of-bounds accesses, provenance violations, and invalid alignment. Run `cargo +nightly miri test` to find UB that may not manifest during normal testing. Miri is the standard tool for verifying unsafe code soundness.
>
> **Q: Why must you not let a panic unwind across an FFI boundary?**
> A: The C ABI does not support Rust's unwinding mechanism. A panic crossing C frames is Undefined Behavior — it can corrupt the C stack, leave C state inconsistent, or crash the process. Always use `std::panic::catch_unwind` at FFI entry points to convert panics to error returns.

---

## Cross-Links

- [[Rust/03_Advanced/01_Lifetimes_In_Depth_and_Borrow_Checker_Mental_Model]] for PhantomData and variance in unsafe types
- [[Rust/03_Advanced/07_Memory_Layout_and_repr_Attributes]] for repr(C), alignment, and layout for FFI
- [[Rust/03_Advanced/08_Build_Scripts_and_FFI_Deep]] for build.rs, bindgen, cc, and -sys crate patterns
- [[Rust/03_Advanced/10_Global_Allocators_and_Allocation]] for custom allocator patterns
