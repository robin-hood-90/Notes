---
tags: [rust, advanced, lifetimes, borrow-checker, variance, nll, hrtb, phantom-data]
aliases: ["Lifetimes Deep Dive", "Variance", "NLL", "HRTB", "PhantomData", "Borrow Checker Mental Model"]
status: stable
updated: 2026-05-11
---

# Lifetimes In Depth: Variance, NLL, HRTB, and Borrow Checker Mental Model

> [!summary] Goal
> Understand lifetimes as compile-time constraints that prove references are valid, not as runtime durations. Master variance, subtyping, NLL, HRTB, PhantomData, and the borrow checker's internal reasoning so you can design APIs that compile without fighting the compiler.

## Table of Contents

1. [What Lifetimes Actually Are](#what-lifetimes-actually-are)
2. [Elision Rules](#elision-rules)
3. [Variance](#variance)
4. [Subtyping and Outlives](#subtyping-and-outlives)
5. [Non-Lexical Lifetimes (NLL)](#non-lexical-lifetimes)
6. [Higher-Ranked Trait Bounds (HRTB)](#higher-ranked-trait-bounds)
7. [PhantomData](#phantomdata)
8. [Lifetime Bounds on Trait Objects](#lifetime-bounds-on-trait-objects)
9. [Lifetime Capture in Closures](#lifetime-capture-in-closures)
10. [Pitfalls](#pitfalls)

---

## What Lifetimes Actually Are

> [!info] Lifetime
> A lifetime is a **compile-time region** in the source code during which a reference is known to be valid. Lifetimes do not extend object lifetimes — they describe **proven validity relationships** between references and the data they point to. The borrow checker verifies that no reference outlives its referent.

```rust
fn example() {
    let x;                     // ─┐ x is initialized
    {                          //  │
        let y = 42;            //  │ y lives here
        x = &y;                //  │ borrow y
    }                          // ─┘ y is dropped, x is now dangling
    println!("{x}");           // ERROR: x's referent no longer valid
}
```

Every reference has a lifetime that must be **contained within** the lifetime of the value it points to. The compiler proves this by tracking:

- Where the reference is created
- Where the reference is last used
- Where the referent is dropped
- Whether any conflicting borrows exist between those points

---

## Elision Rules

> [!info] Lifetime elision
> Rust's lifetime elision rules let you omit explicit lifetimes in common patterns. The compiler fills them in automatically. Learning elision means writing less `'a` noise while still being correct.

### The three elision rules (for function signatures)

```rust
// Rule 1: each parameter that is a reference gets its own lifetime parameter.
// Rule 2: if there is exactly one input lifetime, it's assigned to all output references.
// Rule 3: if there are multiple input lifetimes but one is &self or &mut self,
//         that lifetime is assigned to all output references.

// Rule 1 example:
fn first_word(s: &str) -> &str
// Elides to: fn first_word<'a>(s: &'a str) -> &'a str

// Rule 2 example:
fn longest(a: &str, b: &str) -> &str
// DOES NOT COMPILE: two input lifetimes, no &self
// Must write: fn longest<'a>(a: &'a str, b: &'a str) -> &'a str

// Rule 3 example:
impl MyStruct {
    fn get_ref(&self) -> &str
    // Elides to: fn get_ref<'a>(&'a self) -> &'a str
}
```

### When elision fails

```rust
// Two input references, no &self — elision can't decide which output lifetime to use
fn pick(a: &str, b: &str) -> &str;  // ERROR: elision can't infer
fn pick<'a>(a: &'a str, b: &'a str) -> &'a str;  // FIX: explicit lifetime

// Output reference with no input references — impossible
fn new() -> &str;  // ERROR: no input to borrow from
fn new() -> &'static str;  // FIX: return 'static
```

---

## Variance

> [!info] Variance
> Variance describes how subtyping of generic types relates to subtyping of their type arguments. For lifetimes, it answers: if `'a: 'b` (`'a` outlives `'b`), then how does `T<'a>` relate to `T<'b>`? Variance is **critical** for understanding when the compiler accepts or rejects lifetime relationships.

### Three kinds of variance

| Name | Meaning | If `Sub` is subtype of `Super`: | Rust example |
|:----:|---------|:-------------------------------:|:------------:|
| **Covariant** | Relationship preserved | `F<Sub>` is subtype of `F<Super>` | `&'a T`, `Box<T>`, `Option<T>`, `fn(T)` -> U in return |
| **Contravariant** | Relationship reversed | `F<Super>` is subtype of `F<Sub>` | `fn(T)` in argument position, `*const T`? (see below) |
| **Invariant** | No relationship | `F<Sub>` is NOT subtype of `F<Super>` | `&mut T`, `Cell<T>`, `UnsafeCell<T>`, `*mut T` |

### Covariance on lifetimes

```rust
// 'a: 'b means 'a outlives 'b (lives at least as long)

// &'a T is COVARIANT over 'a.
// If 'a: 'b, then &'a T is a subtype of &'b T.
// Intuition: you can pass a short-lived reference where a long-lived one is expected
// if the data actually lives at least that long.

// Example: covariance in action
fn takes_static_ref(_x: &'static str) {}

let s: &str = "hello";       // &'static str by default for string literals
takes_static_ref(s);         // ✅ OK: &'static T is subtype of &'static T (same)

let owned = String::from("world");
let ref_owned: &str = &owned;  // This borrow's lifetime is tied to owned's scope
// takes_static_ref(ref_owned);  // Would be ERROR except string literals are 'static
```

### Invariance on `&mut T`

```rust
// &mut T is INVARIANT over T (and over lifetimes).
// You CANNOT substitute a subtype for &mut T.

fn set_value(x: &mut &'static str) {
    *x = "forever";
}

let mut s: &str = "temp";
// set_value(&mut s);  // ERROR: expected &mut &'static str, got &mut &str
// Why? If it compiled, set_value could store a 'static reference into a
// non-'static variable, breaking memory safety.
```

```text
Variance cheat-sheet for common Rust types:

Type                          Variance
─────────────────────────────────────────────────
&T                            covariant in T, covariant in lifetime
&mut T                        invariant in T, invariant in lifetime
Box<T>, Vec<T>, String        covariant in T
Cell<T>, RefCell<T>           invariant in T
UnsafeCell<T>                 invariant in T
*const T                      covariant in T
*mut T                        invariant in T
fn(T) -> U                    contravariant in T, covariant in U
fn(T) where T: 'a            invariant in 'a (T: 'a is a constraint)
PhantomData<&'a T>           inherits variance of &'a T
```

### Why variance matters in APIs

```rust
// Real-world: variance errors appear in:
// 1. Structs with mutable references
struct Bad<'a, T> {
    inner: &'a mut T,  // 'a is invariant → Bad<'a, T> is invariant in 'a
}

// 2. Closure/lifetime inference
fn foo<'a>(f: impl Fn(&'a str)) {}  // f is contravariant in 'a

// 3. Trait objects
trait Trait<'a> {}
// Box<dyn Trait<'static>> is NOT a subtype of Box<dyn Trait<'short>>
```

---

## Subtyping and Outlives

> [!info] Subtyping on lifetimes
> `'a: 'b` means `'a` outlives (is at least as long as) `'b`. This is the **subtype relationship** for lifetimes: if `'a: 'b`, then `'a` is a subtype of `'b`. A longer lifetime can be used where a shorter one is expected.

### `T: 'a` — "T outlives 'a"

```rust
// T: 'a means: any references inside T must live at least as long as 'a.
// If T has no references (e.g., i32), T: 'a is trivially true.

// Example: storing a reference requires the reference to outlive the struct
struct Ref<'a, T: 'a> {
    data: &'a T,
}

// T: 'a is automatically inserted by the borrow checker when needed.
// You rarely write it explicitly, but seeing it in error messages helps.

// Common error: "the parameter type T may not live long enough"
// Fix: add T: 'a bound
struct Container<'a, T: 'a> {
    inner: &'a T,
}
```

### `'a: 'b` — lifetime bounds

```rust
// 'a: 'b means 'a outlives 'b. Used when a function takes two references
// and the output is tied to only one input:

fn first<'a, 'b>(a: &'a str, b: &'b str) -> &'a str
where
    'b: 'a,  // 'b must outlive 'a (a can't outlive b since b is ignored)
{
    a
}

// More common: polymorphic lifetimes where one reference must outlive another's borrow
struct Pair<'a, 'b: 'a> {
    first: &'a str,
    second: &'b str,
}
```

### Lifetime coercion

```rust
// The compiler automatically "shortens" lifetimes when needed (coercion):
// &'a T can be coerced to &'b T when 'a: 'b.

fn takes_short(_: &str) {}  // elided → &'_ str

let long_lived = String::from("hello");
let ref_long: &'static str = "world";

takes_short(&long_lived);  // &long_lived is coerced to a shorter lifetime
takes_short(ref_long);     // &'static coerced to the function's lifetime
```

---

## Non-Lexical Lifetimes (NLL)

> [!info] NLL (RFC 2094, stable since Rust 2018)
> Before NLL, lifetimes were based on **lexical scopes** — a reference lived until the end of the enclosing block. NLL makes lifetimes follow **last use** instead, enabling much more ergonomic borrowing patterns.

### Lexical lifetimes (Rust 2015 — old behavior)

```rust
// Lexical: reference lives until end of scope
let mut data = vec![1, 2, 3];
let x = &data[0];          // borrow starts here
data.push(4);              // ERROR: can't mutate while x exists
println!("{x}");           // x used here
}                          // x's borrow ends here (scope-end)

// With lexical lifetimes, this error happened even if you moved the push
// after the println — because x lived until the end of the scope.
```

### NLL (Rust 2018+)

```rust
// NLL: reference lives until LAST USE
let mut data = vec![1, 2, 3];
let x = &data[0];          // borrow starts here
println!("{x}");           // LAST use of x — borrow ends here
data.push(4);              // ✅ OK: x is no longer borrowed
```

### Two-phase borrows (NLL extension)

```rust
// Two-phase borrows allow reborrowing a mutable reference during
// the "reservation" phase (before the "activation" phase).

// Without two-phase borrows (Rust 2015):
let mut v = vec![1, 2, 3];
v.push(v.len());  // ERROR: mutable borrow and shared borrow conflict

// With two-phase borrows (Rust 2018+):
let mut v = vec![1, 2, 3];
v.push(v.len());  // ✅ OK: the mutable borrow for push() is "reserved"
                  // until v.len() evaluates the shared borrow, then "activated"

// How two-phase borrows work:
// 1. Auto-deref and method call creates a "reservation" (mutable borrow pending)
// 2. Arguments are evaluated (shared borrow for v.len() — OK since the
//    mutable borrow is only reserved, not activated yet)
// 3. After arguments are evaluated, the reservation is "activated"
//    (mutable borrow becomes active, exclusive access)
```

### NLL limitations

```rust
// NLL still rejects this pattern (Polonius would accept it):
fn example() {
    let mut data = vec![1, 2, 3];
    let x = &mut data[0];
    let y = &data;           // ERROR: can't borrow data as shared while
                             // x's mutable borrow is active
    println!("{x} {y:?}");
}
// Polonius (next-gen borrow checker) may accept this because x and y
// borrow disjoint parts of data.
```

---

## Higher-Ranked Trait Bounds (HRTB)

> [!info] HRTB
> Higher-Ranked Trait Bounds (`for<'a>`) express that a trait must hold **for all possible lifetimes** `'a`, not just one concrete lifetime. This is essential for `Fn` trait bounds, iterator patterns, and generic API design.

### The problem HRTB solves

```rust
// Suppose we want a function that accepts a callback working on any reference:
fn call_with_ref(f: impl Fn(&i32)) {
    let x = 42;
    f(&x);  // f must accept any &i32, not just one specific lifetime
}

// Without HRTB, the bound would fix a single lifetime:
fn bad_call_with_ref<'a>(f: impl Fn(&'a i32)) {
    // f now only accepts &'a i32 — we can't pass &x here unless
    // x happens to live exactly 'a
}

// With HRTB (implicit via elision for Fn):
// fn call_with_ref(f: impl Fn(&i32))
// desugars to: fn call_with_ref(f: impl for<'a> Fn(&'a i32))
```

### Where HRTB is required

```rust
// 1. Fn/FnMut/FnOnce bounds (implicit HRTB)
fn with_borrow(f: impl Fn(&str)) {}  // for<'a> Fn(&'a str)

// 2. Trait bound on a reference type
fn process<T: for<'a> MyTrait<'a>>(t: T) {}

// 3. Iterator patterns
fn transform<F>(f: F)
where
    F: for<'a> Fn(&'a str) -> &'a str,  // output lifetime tied to input
{}

// 4. Closure bounds in structs
struct Handler<F>
where
    F: for<'a> Fn(&'a [u8]) -> &'a [u8],
{
    handler: F,
}
```

### When HRTB errors appear

```rust
// Error: "bound must be higher-ranked"
// Usually means you need for<'a>:

// ❌ Without HRTB:
fn map_ref<F>(f: F) where F: Fn(&str) -> &str {}  // This actually works due to
                                                     // implicit HRTB on Fn

// ✅ Explicit HRTB (same as implicit):
fn map_ref<F>(f: F) where F: for<'a> Fn(&'a str) -> &'a str {}

// Where HRTB is REQUIRED (not implicit):
trait LifetimeTrait<'a> {}
fn with_hrtb<T: for<'a> LifetimeTrait<'a>>(t: T) {}  // MUST write for<'a>
```

---

## PhantomData

> [!info] PhantomData
> `PhantomData<T>` is a zero-sized type that tells the compiler you conceptually own or depend on `T` even though no field of type `T` exists in your struct. It's used to: express ownership for drop check, express variance correctly, and mark lifetime/type dependencies for the borrow checker.

### PhantomData use cases

```rust
use std::marker::PhantomData;

// 1. Ownership for drop check (Drop requires the type to be "owned")
struct MyAlloc<T> {
    ptr: *mut T,
    _marker: PhantomData<T>,  // Says: "this struct conceptually owns T"
}

impl<T> Drop for MyAlloc<T> {
    fn drop(&mut self) {
        // Safe to drop T here because PhantomData tells the compiler
        // we might have an instance of T
        unsafe { std::ptr::drop_in_place(self.ptr) }
    }
}

// 2. Variance control
struct Iter<'a, T> {
    ptr: *const T,
    _phantom: PhantomData<&'a T>,  // Makes Iter covariant over 'a and T
}

// 3. Type-level state machine (zero-cost abstractions)
struct State<S> { _state: PhantomData<S> }

struct Idle;
struct Ready;

impl State<Idle> { fn start(self) -> State<Ready> { State { _state: PhantomData } } }
impl State<Ready> { fn process(&self) {} }
```

### PhantomData variance table

```rust
use std::marker::PhantomData;

// Each PhantomData variant tells the compiler a different variance story:

PhantomData<T>              // invariant in T (owns T)
PhantomData<&'a T>          // covariant in 'a and T
PhantomData<&'a mut T>      // invariant in 'a and T
PhantomData<fn(T)>          // contravariant in T
PhantomData<fn() -> T>      // covariant in T
PhantomData<*const T>       // covariant in T
PhantomData<*mut T>         // invariant in T

// Choosing wrong PhantomData can make your code compile when it shouldn't
// or reject safe code. For unsafe types, always pick the correct variant.

// Example: storing a raw pointer for iteration
// We want Iter to be covariant so &Iter subtypes work correctly
struct IterCorrect<'a, T> {
    start: *const T,
    end: *const T,
    _phantom: PhantomData<&'a T>,  // ✅ covariant — same as std::slice::Iter
}
```

---

## Lifetime Bounds on Trait Objects

```rust
// Trait objects have their own lifetime rules:

// 1. Trait object lifetime defaults
trait MyTrait {}
// Box<dyn MyTrait>          — lifetime defaults to 'static
// &dyn MyTrait              — lifetime is the borrow's lifetime
// Box<dyn MyTrait + 'a>     — explicit lifetime

// 2. When you need to store trait objects with references
struct Wrapper<'a> {
    // If the trait object captures references, it needs a lifetime bound:
    inner: Box<dyn MyTrait + 'a>,
    // Without 'a, Box<dyn MyTrait> = Box<dyn MyTrait + 'static>
    // This would reject implementations that borrow data
}

// 3. Lifetime bounds on trait objects in generics
fn process<'a>(items: &[Box<dyn MyTrait + 'a>]) {
    // items references must live at least 'a
}

// 4. Lifetime elision for trait objects
// &dyn Trait              → &'a dyn Trait + 'a
// &'a dyn Trait            → &'a dyn Trait + 'a
// Box<dyn Trait>           → Box<dyn Trait + 'static>
```

---

## Lifetime Capture in Closures

```rust
// Closures can capture references from their environment.
// The closure's type implicitly captures the minimum lifetimes needed.

fn call_fn_once(f: impl FnOnce()) {
    f();
}

fn example() {
    let s = String::from("hello");
    let borrow = &s;  // borrow lives at least as long as call_fn_once's scope

    call_fn_once(|| {
        println!("{borrow}");  // closure captures &s
    });

    // The closure's type is: impl FnOnce() where the borrow is captured
    // The compiler infers: FnOnce() is valid for the scope where borrow is alive
}
```

### The `'_` lifetime in closures (return type captures)

```rust
// Common error: closure returns a reference to a captured value
fn create_matcher<'a>(pattern: &'a str) -> impl Fn(&'a str) -> bool {
    // Captures pattern by reference
    // Returns a closure whose lifetime is tied to pattern's lifetime
    move |text| text.contains(pattern)
}

// Without explicit lifetime:
fn create_matcher_bad(pattern: &str) -> impl Fn(&str) -> bool {
    move |text| text.contains(pattern)
    // ❌ ERROR: lifetime of pattern may not live long enough
    // Fix: add 'a or use '_
}
```

---

## Pitfalls

### Over-annotating lifetimes

Not every function needs explicit lifetimes. Rely on elision rules. Add explicit lifetimes only when elision can't infer, or when clarity requires it.

### Self-referential structs

These are usually impossible without `Pin` + `unsafe`. See `Pin` and `Unpin` deep dive for alternatives.

### Invariance confusion with `&mut` and `Cell`

When you see "lifetime mismatch" errors with `&mut` or `Cell`, it's usually because these types are invariant — the compiler can't shorten the lifetime for you. Restructure the API to avoid mutable references if variance matters.

### Forgetting `PhantomData` in unsafe types

If you store a raw pointer but don't add `PhantomData<T>`, the compiler doesn't know your type conceptually owns `T`. The drop checker may accept code that drops `T` before the struct is done using it. This can create subtle use-after-frees.

### `impl Fn(&str) -> &str` without explicit lifetimes

```rust
// This compiles (HRTB is implicit for Fn):
fn ok(f: impl Fn(&str) -> &str) {}

// But this doesn't:
fn bad<F>(f: F) where F: Fn(&str) -> &str {}
// Actually this does work for Fn — it gets implicit HRTB
// But for custom traits, you MUST write for<'a>:
fn custom<F>(f: F) where F: for<'a> MyTrait<'a> {}  // Required!
```

---

> [!question]- Interview Questions
>
> **Q: What is variance and why does it matter for lifetimes?**
> A: Variance describes how subtyping propagates through generic types. For lifetimes, `&'a T` is covariant over `'a` — you can substitute a shorter lifetime. `&mut T` is invariant — you cannot. This matters because invariance prevents the compiler from shortening a mutable reference's lifetime, which would allow data races.
>
> **Q: What problem did NLL solve?**
> A: Before NLL, references lived until the end of their enclosing scope (lexical). This rejected safe code where the last use of a reference was before a conflicting mutation. NLL makes references live only until their last use, enabling patterns like `data.push(data.len())`.
>
> **Q: When must you write `for<'a>` (HRTB)?**
> A: When you need a trait bound to hold for ALL possible lifetimes, not just one. Implicit for `Fn(&str)` bounds. Required for custom traits: `T: for<'a> MyTrait<'a>`.
>
> **Q: What does PhantomData do?**
> A: It's a zero-sized marker that tells the compiler about ownership/variance relationships that aren't visible in the struct's fields. Used in unsafe types to express ownership for drop check, control variance, and model type-state machines.

---

## Cross-Links

- [[Rust/01_Foundations/01_Ownership_and_Borrowing]] for ownership basics
- [[Rust/04_Playbooks/01_Debug_Borrow_Checker_Errors]] for debugging borrow-checker diagnostics
- [[Rust/03_Advanced/02_Unsafe_Rust_and_FFI_Basics]] for PhantomData in unsafe types
- [[Rust/02_Core/07_Pin_and_Unpin_Deep_Dive]] for self-referential types and how Pin interacts with lifetimes
