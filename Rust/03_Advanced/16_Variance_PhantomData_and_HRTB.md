---
tags: [rust, advanced, variance, phantomdata, hrtb, subtyping, coerce]
aliases: ["Variance", "PhantomData", "HRTB", "Higher-Ranked Trait Bounds", "Subtyping"]
status: stable
updated: 2026-05-11
---

# Variance, `PhantomData`, and Higher-Ranked Trait Bounds

> [!summary] Goal
> Understand how Rust's type system reasons about subtyping, variance, and higher-ranked lifetimes. Master `PhantomData` for expressing ownership and variance in unsafe types. Design APIs with `for<'a>` bounds correctly.

## Table of Contents

1. [Why These Topics Belong Together](#why-these-topics-belong-together)
2. [Variance](#variance)
3. [PhantomData](#phantomdata)
4. [Higher-Ranked Trait Bounds (HRTB)](#higher-ranked-trait-bounds)
5. [Subtyping and Coercion](#subtyping-and-coercion)
6. [Pitfalls](#pitfalls)

---

## Why These Topics Belong Together

Variance, `PhantomData`, and HRTB are all about the same question: **how do generic type parameters relate to each other?**

- **Variance**: when is `T<Sub>` a subtype of `T<Super>`?
- **`PhantomData`**: how does a struct "pretend" to own or borrow a type at the type level?
- **HRTB**: how do you express "this bound holds for all possible lifetimes"?

Understanding all three together lets you design sound generic APIs and unsafe types that don't violate compiler assumptions.

---

## Variance

> [!info] Variance
> Variance describes how subtyping propagates through generic type constructors. If `'a: 'b` (`'a` outlives `'b`), then `'a` is a subtype of `'b`. Variance tells us what happens to `F<'a>` when we substitute `'b` for `'a`.

### The three variance kinds (recap)

| Kind | Meaning | Examples |
|:----:|---------|:--------:|
| **Covariant** | `F<Sub>` is subtype of `F<Super>` | `&'a T`, `Box<T>`, `Vec<T>`, `fn() -> T` |
| **Contravariant** | `F<Super>` is subtype of `F<Sub>` | `fn(T)` in argument position |
| **Invariant** | No subtyping relationship | `&mut T`, `Cell<T>`, `UnsafeCell<T>`, `*mut T` |

### Variance for lifetime and type parameters (full table)

```rust
// The variance of common types over both type T and lifetime 'a:

// Covariant over 'a and T:
&'a T                     // → covariant in 'a, covariant in T

// Invariant over 'a, covariant over T (actually invariant in both):
&'a mut T                 // → invariant in 'a, invariant in T
// Why? &mut T has unique write access — allowing subtyping could
// let a short-lived reference flow into a long-lived slot.

// Covariant over T, invariant over nothing:
Box<T>                    // → covariant in T
Vec<T>                    // → covariant in T

// Invariant over T:
Cell<T>                   // → invariant in T
RefCell<T>                // → invariant in T
UnsafeCell<T>             // → invariant in T (Cell and RefCell wrap UnsafeCell)
*mut T                    // → invariant in T

// Covariant over T:
*const T                  // → covariant in T
Option<T>                 // → covariant in T

// Function types — mixed variance:
fn(T) -> U                // → contravariant in T, covariant in U
// fn argument positions are contravariant!
// This means: a function accepting a wider type can substitute for
// one accepting a narrower type.

// Example:
fn takes_fn(f: fn(&'static str)) {}
let f: fn(&str) = |s| println!("{s}");
// f accepts &str (any string reference).
// takes_fn needs fn(&'static str) (only static references).
// This DOES compile — contravariance.
// A function accepting ANY &str can be used where a &'static str is needed.
```

### Why covariance works for `&'a T`

```rust
fn test_variance() {
    // &'a T is covariant over 'a:
    // If 'static: 'short, then &'static T can be used where &'short T is expected.

    let long_lived: &'static str = "hello";
    let short: &str;  // Lifetime `'_`

    short = long_lived;  // ✅ OK: covariant — &'static str is subtype of &'_
    // Intuition: a static reference is VALID for any shorter lifetime.

    let owned = String::from("world");
    let short_ref = &owned;
    // short = short_ref;  // ❌ ERROR: short_ref's lifetime is shorter
}
```

### Why invariance for `&mut T`

```rust
// &mut T is invariant — you CANNOT shorten the lifetime of a mutable reference.

fn mutate(x: &mut &'static str) {
    *x = "changed";
}

let mut s: &str = "temp";
// mutate(&mut s);
// ❌ ERROR: expected &mut &'static str, got &mut &str
// If this compiled, mutate() would write a 'static reference into s,
// but s doesn't live long enough → dangling pointer.
// Invariance prevents this.
```

### Variance and unsafe types

```rust
use std::marker::PhantomData;

// When designing unsafe types, the DEFAULT variance for raw pointers
// might not match what you need.

// *const T is covariant (like &T)
// *mut T is invariant (like &mut T)

struct MyIter<'a, T> {
    start: *const T,
    end: *const T,
    // What PhantomData should we use?
}

// If we use PhantomData<T>, the struct is INVARIANT over T.
// If we use PhantomData<&'a T>, the struct is COVARIANT over 'a and T.

// The correct choice (matching std::slice::Iter):
// Use PhantomData<&'a T> for covariance — so you can pass a longer-lived
// iterator where a shorter-lived one is expected.
```

---

## PhantomData

> [!info] PhantomData
> `PhantomData<T>` is a zero-sized marker that tells the compiler about conceptual ownership and variance relationships that aren't visible in the struct's fields. It's used in three main scenarios:

### Scenario 1: Expressing ownership for drop check

```rust
struct MyBox<T> {
    ptr: *mut T,
    // Without PhantomData, the compiler thinks MyBox doesn't own any T.
    // Drop may be called on MyBox before any T is dropped — UB!
    _marker: PhantomData<T>,
}

impl<T> Drop for MyBox<T> {
    fn drop(&mut self) {
        unsafe { std::ptr::drop_in_place(self.ptr) }
    }
}

// With PhantomData<T>:
// - The compiler knows this type CONCEPTUALLY owns T.
// - Drop order analysis won't drop T (or T's fields) before MyBox drops.
// - The type is INVARIANT over T (owns T).
```

### Scenario 2: Controlling variance

```rust
use std::marker::PhantomData;

// Choose the right PhantomData to match your variance needs:

// Owns T → invariant
PhantomData<T>                 // → invariant in T

// Borrows &T → covariant
PhantomData<&'a T>             // → covariant in 'a and T

// Borrows &mut T → invariant
PhantomData<&'a mut T>         // → invariant in 'a and T

// Example: implementing an iterator that wraps a raw pointer
// We want it to be covariant like &[T]::Iter
struct Iter<'a, T> {
    ptr: *const T,
    end: *const T,
    _phantom: PhantomData<&'a T>,  // → same variance as &'a [T]
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;
    fn next(&mut self) -> Option<Self::Item> {
        if self.ptr == self.end {
            None
        } else {
            let item = unsafe { &*self.ptr };
            self.ptr = unsafe { self.ptr.add(1) };
            Some(item)
        }
    }
}
```

### Scenario 3: Type-level state machines

```rust
use std::marker::PhantomData;

struct State<S> {
    _state: PhantomData<S>,
}

// State types (zero-sized, no runtime cost)
struct Idle;
struct Ready;
struct Active;

impl State<Idle> {
    fn new() -> Self { Self { _state: PhantomData } }
    fn start(self) -> State<Ready> { State { _state: PhantomData } }
}

impl State<Ready> {
    fn activate(self) -> State<Active> { State { _state: PhantomData } }
}

impl State<Active> {
    fn process(&self) { /* ... */ }
    fn stop(self) -> State<Idle> { State::new() }
}

// Usage — illegal states unrepresentable:
let s = State::<Idle>::new();
let s = s.start();           // Idle → Ready
// s.start();                // ❌ Compile error: Ready has no start()
// s.process();              // ❌ Compile error: Ready has no process()
let s = s.activate();        // Ready → Active
s.process();                 // ✅ Only Active can process
```

---

## Higher-Ranked Trait Bounds (HRTB)

> [!info] HRTB
> Higher-Ranked Trait Bounds (`for<'a>`) express that a bound holds **for all lifetimes** `'a`, not just one concrete lifetime. They're essential for function types, closures, and generic APIs that work with arbitrary borrows.

### The core pattern

```rust
// Without HRTB: the bound picks ONE specific lifetime
fn bad<'a, F>(f: F) where F: Fn(&'a str) {}
// f only accepts &'a str — we can't pass arbitrary strings.

// With HRTB: the bound holds for ALL lifetimes
fn good<F>(f: F) where F: for<'a> Fn(&'a str) {}
// f accepts ANY &str — it's polymorphic over the borrow lifetime.

// For Fn/FnMut/FnOnce, HRTB is implicit via elision:
fn works(f: impl Fn(&str) -> &str) {}  // = for<'a> Fn(&'a str) -> &'a str
```

### Where HRTB is required (not implicit)

```rust
// For Fn/FnMut/FnOnce: HRTB is IMPLICIT (you don't need for<'a>)
fn takes_closure(f: impl Fn(&str)) {}        // OK
fn takes_fn<F: Fn(&str)>(f: F) {}            // OK

// For CUSTOM traits: HRTB is REQUIRED
trait MyTrait<'a> {
    fn process(&'a self) -> &'a str;
}

// ❌ Wrong: binds to ONE specific lifetime
fn use_trait_bad<'a, T: MyTrait<'a>>(t: &T) {
    let s: &str = t.process();  // Only works for one lifetime
}

// ✅ Correct: works for ALL lifetimes
fn use_trait_good<T: for<'a> MyTrait<'a>>(t: &T) {
    let s: &str = t.process();  // Works for any borrow duration
}

// Real example: serde's Deserialize
// Deserialize<'de> has a lifetime parameter for borrowed data.
// fn deserialize<'de, D: Deserialize<'de>>(data: &'de [u8]) -> D {}
// This ties the output lifetime to the input — an HRTB pattern.
```

### HRTB with iterator patterns

```rust
// HRTB in iterator filters:
fn filter_map<'a, I, F>(iter: I, f: F) -> impl Iterator<Item = &'a str>
where
    I: Iterator<Item = &'a str>,
    F: for<'b> Fn(&'b str) -> Option<&'b str>,  // Works for ANY borrow
{
    iter.filter_map(f)
}

// Without HRTB, if we tied the closure's lifetime to 'a specifically,
// it wouldn't compose well with other iterator adapters.
```

---

## Subtyping and Coercion

> [!info] Coercion
> Rust automatically coerces types in certain positions: references are coerced to longer-lived references (covariant shortening), `Box<T>` to `&T`, `&mut T` to `&T`, and array references to slices.

### Common coercions

```rust
// 1. Reference shortening (lifetime coercion)
let s: &'static str = "hello";
let t: &str = s;  // &'static str → &'_ str  (lifetime shortened)

// 2. Deref coercion (via Deref trait)
fn takes_str(s: &str) {}
let owned = String::from("hello");
takes_str(&owned);  // &String → &str via Deref<Target=str>

// 3. Box coercion
fn takes_slice(s: &[i32]) {}
let boxed = Box::new([1, 2, 3]);
takes_slice(&boxed);  // &Box<[i32; 3]> → &[i32]

// 4. &mut T → &T (reborrow)
fn read_only(s: &i32) {}
let mut x = 42;
read_only(&mut x);  // &mut i32 → &i32 (reborrow)

// 5. Function pointer coercion
fn takes_fn_ptr(f: fn(i32) -> i32) {}
let closure: fn(i32) -> i32 = |x| x + 1;
takes_fn_ptr(closure);  // fn pointer (not a closure!) → fn pointer
```

### When coercion fails

```rust
// Vec<T> does NOT coerce to &[T] automatically in all positions:
fn takes_slice_mut(s: &mut [i32]) {}
let mut v = vec![1, 2, 3];
takes_slice_mut(&mut v);  // ✅ OK: &mut Vec → &mut [i32] (DerefMut)

// BUT:
fn expect_boxed_slice(b: Box<[i32]>) {}
let v = vec![1, 2, 3];
// expect_boxed_slice(v);  // ❌ ERROR: Vec → Box<[i32]> is not automatic
let b: Box<[i32]> = v.into_boxed_slice();  // ✅ Explicit conversion
```

---

## Pitfalls

### Adding `PhantomData<T>` when you should use `PhantomData<&'a T>`

If your struct wraps a raw pointer that conceptually borrows data, use `PhantomData<&'a T>` (covariant) not `PhantomData<T>` (invariant). Wrong variance can cause your type to reject valid lifetime relationships — or accept invalid ones.

### Forgetting that `fn` arguments are contravariant

```rust
fn takes_fn(f: fn(&'static str)) {}
let f: fn(&str) = |s| println!("{s}");
takes_fn(f);  // ✅ OK: fn(&str) is subtype of fn(&'static str)
// Intuition: "a function handling any &str also handles &'static str"

// But NOT the reverse:
// fn takes_fn_short(f: fn(&str)) {}
// let f: fn(&'static str) = |s| println!("{s}");
// takes_fn_short(f);  // ❌ ERROR: can't pass fn(&'static str) where fn(&str) expected
// Why? fn(&'static str) can only handle 'static data.
// fn(&str) needs to handle ANY &str — including short-lived ones.
// Contravariance: Fn(Super) is subtype of Fn(Sub).
```

### Using HRTB inside a struct where you meant one specific lifetime

If a struct stores a reference, the bound should be on the struct's lifetime parameter, not HRTB:

```rust
// ❌ Wrong:
struct Wrapper<F: for<'a> Fn(&'a str)> { f: F }
// Every instance of Wrapper accepts F that works for ALL lifetimes.

// ✅ (likely what you want):
struct Wrapper<'a, F: Fn(&'a str)> { f: F }
// Each instance of Wrapper has one specific lifetime for the closure.
```

---

## Cross-Links

- [[Rust/03_Advanced/01_Lifetimes_In_Depth_and_Borrow_Checker_Mental_Model]] for base lifetime concepts
- [[Rust/03_Advanced/02_Unsafe_Rust_and_FFI_Basics]] for PhantomData in unsafe types
- [[Rust/02_Core/09_Into_From_AsRef_AsMut_and_Cow]] for coercion patterns
- [[Rust/02_Core/06_Closures_and_Fn_Traits]] for Fn/FnMut/FnOnce trait hierarchy
