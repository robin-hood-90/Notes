---
tags: [rust, advanced, const-generics, gats, generic-associated-types]
aliases: ["Const Generics", "Generic Associated Types", "GATs", "Compile-Time Generics"]
status: stable
updated: 2026-05-03
---

# Const Generics and Generic Associated Types

> [!summary] Goal
> Use compile-time values as generic parameters for type-level computations and write associated types that vary by implementing type.

## Table of Contents

1. [Why Const Generics and GATs Matter](#why-const-generics-and-gats-matter)
2. [Const Generics Syntax](#const-generics-syntax)
3. [Use Cases for Const Generics](#use-cases-for-const-generics)
4. [Generic Associated Types: Syntax](#generic-associated-types-syntax)
5. [Use Cases for GATs](#use-cases-for-gats)
6. [Pitfalls](#pitfalls)

---

## Why Const Generics and GATs Matter

```mermaid
flowchart LR
    A[Rust Generics] --> B[Type generics: T]
    A --> C[Const generics: const N: usize]
    A --> D[Lifetime generics: 'a]
    A --> E[GATs: associated types with params]
    B --> F[Most common — Vec\<T\>]
    C --> G[Fixed-size arrays — [T; N]]
    D --> H[Lifetime relationships]
    E --> I["LendingIterator", MatrixRow]
```

> [!tip] Definition
> **Const generics**: generic parameters that are compile-time constant values (like integers), not types. **Generic associated types (GATs)**: associated types that are themselves generic — they can have their own type, lifetime, or const parameters.

---

## Const Generics Syntax

```rust
// Basic syntax
struct Array<T, const N: usize> {
    data: [T; N],
}

// Usage — the const value is part of the type
let small: Array<i32, 3> = Array { data: [1, 2, 3] };
let large: Array<i32, 100> = Array { data: [0; 100] };
```

### Where const generics can appear

```rust
// Type parameters
fn identity<const N: usize>(x: [i32; N]) -> [i32; N] { x }

// In structs
struct Buffer<const SIZE: usize> {
    inner: [u8; SIZE],
    pos: usize,
}

// In enums
enum Response<const MAX: usize> {
    Data([u8; MAX]),
    Timeout,
}

// In traits
trait Capacity {
    const CAP: usize;
}
```

### Limitations on const parameter types

| Supported | Not yet supported (nightly/planned) |
|-----------|-----------------------------------|
| `bool` | `&str`, `String` |
| `char` | Floating point |
| Integer types (`i8`, `u8`, `i16`, `u16`, `i32`, `u32`, `i64`, `u64`, `i128`, `u128`, `isize`, `usize`) | Custom types |

---

## Use Cases for Const Generics

### Fixed-size buffers

```rust
struct RingBuffer<const N: usize> {
    data: [u8; N],
    head: usize,
    tail: usize,
}

impl<const N: usize> RingBuffer<N> {
    const fn new() -> Self {
        Self { data: [0; N], head: 0, tail: 0 }
    }
}

let buf: RingBuffer<1024> = RingBuffer::new();
```

### Matrix types

```rust
struct Matrix<const R: usize, const C: usize> {
    data: [[f64; C]; R],
}

impl<const R: usize, const C: usize> Matrix<R, C> {
    fn zeros() -> Self {
        Self { data: [[0.0; C]; R] }
    }
}
```

### Compile-time dimension checking

```rust
fn dot<const N: usize>(a: [f64; N], b: [f64; N]) -> f64 {
    let mut sum = 0.0;
    for i in 0..N { sum += a[i] * b[i]; }
    sum
}
```

---

## Generic Associated Types: Syntax

```rust
trait LendingIterator {
    type Item<'a> where Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

struct Once<T>(Option<T>);

impl<T: Clone> LendingIterator for Once<T> {
    type Item<'a> = &'a T;  // GAT — the lifetime is bound to the borrow

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
        self.0.take().map(|x| {
            // Can't return T because Iterator would need owned
            // But with GAT, we return &T tied to the borrow
            &x  // This won't compile — simplified for illustration
        })
    }
}
```

### A working GAT example

```rust
trait Container {
    type Elem<T>: std::ops::Deref<Target = T>;

    fn get<T>(&self, key: &str) -> Option<Self::Elem<T>>;
}

struct MyVec<T>(Vec<T>);

impl<T> Container for MyVec<T> {
    type Elem<U> = &'static U;  // simplified

    fn get<U>(&self, key: &str) -> Option<Self::Elem<U>> {
        None
    }
}
```

---

## Use Cases for GATs

### Lending iterator (streaming with references)

The standard `Iterator` yields owned values. A lending iterator can yield references tied to the borrow:

```rust
trait LendingIterator {
    type Item<'a> where Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

// Allows patterns that normal Iterators can't express
struct Lines<'a> {
    inner: &'a str,
}

impl<'a> LendingIterator for Lines<'a> {
    type Item<'b> = &'b str where Self: 'b;

    fn next<'b>(&'b mut self) -> Option<Self::Item<'b>> {
        // return a reference into self.inner
        todo!()
    }
}
```

### Pooled connections

```rust
trait ConnectionPool {
    type Conn<'a>: std::ops::Deref<Target = Connection> where Self: 'a;

    fn get<'a>(&'a self) -> Self::Conn<'a>;
}
```

### Functor pattern

```rust
trait Functor {
    type Mapped<T, F>: Functor where F: FnOnce(Self::Unmapped) -> T;
    type Unmapped;

    fn map<F, T>(self, f: F) -> Self::Mapped<T, F>
    where F: FnOnce(Self::Unmapped) -> T;
}
```

---

## Pitfalls

### Type inference with const generics

```rust
fn foo<const N: usize>() -> [i32; N] { [0; N] }

let x = foo();  // ERROR: cannot infer the value of const parameter N
```

**Fix**: specify the const: `let x = foo::<5>();`

### Const generics and trait bounds

```rust
trait IsOdd {
    const IS_ODD: bool;
}

// Can't implement IsOdd for all const generics
// impl<const N: usize> IsOdd for [i32; N] { ... }
```

**Workaround**: use const generic expressions.

### GATs and lifetime bounds

GATs with lifetime parameters require careful bound handling:

```rust
trait BadGat {
    type Item<'a>;
    // Using Self::Item<'a> may need bounds
    fn get<'a>(&'a self) -> Self::Item<'a>;
}
```

**Fix**: add explicit where clauses on the GAT.

### Complexity

Const generics and GATs increase the learning curve significantly. Use them sparingly — a simpler design with concrete types or a macro is often better.

---

> [!question]- Interview Questions
>
> **Q: What are const generics?**
> A: Generic parameters that accept compile-time constant values (like `const N: usize`), enabling types and functions parameterized by integers (e.g., `[T; N]`).
>
> **Q: What are generic associated types (GATs)?**
> A: Associated types that are themselves generic — they can have their own type, lifetime, or const parameters. They enable traits like `LendingIterator` where the item type depends on the borrow lifetime.
>
> **Q: When should you use const generics vs runtime values?**
> A: Const generics for compile-time known sizes (stack arrays, buffer sizes, matrix dimensions). Runtime values for dynamic sizes (heap-allocated collections like `Vec`).

---

## Cross-Links

- [[Rust/01_Foundations/05_Traits_Generics_and_Lifetimes_Intro]] for generics and associated types
- [[Rust/03_Advanced/07_Memory_Layout_and_repr_Attributes]] for fixed-size array layout
- [[Rust/03_Advanced/10_no_std_and_Embedded_Rust]] for const generics in embedded buffers

---

## References

- [Const Generics RFC 2000](https://rust-lang.github.io/rfcs/2000-const-generics.html)
- [Const Generics (Rust Reference)](https://doc.rust-lang.org/reference/items/generics.html#const-generics)
- [GATs RFC 1598](https://rust-lang.github.io/rfcs/1598-generic_associated_types.html)
- [GATs Initiative](https://blog.rust-lang.org/2022/10/28/gats-stabilization.html)
