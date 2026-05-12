---
tags: [rust, core, iterators, advanced-iterators, custom-iterators]
aliases: ["Advanced Iterators", "IntoIterator", "Custom Iterator", "Iterator Adapters"]
status: stable
updated: 2026-05-03
---

# Advanced Iterator Patterns

> [!summary] Goal
> Implement custom iterators, understand the `Iterator` trait in full, and build complex lazy pipelines.

## Table of Contents

1. [Why Advanced Iterator Patterns Matter](#why-advanced-iterator-patterns-matter)
2. [Implementing `IntoIterator`](#implementing-intoiterator)
3. [Custom Iterator Types](#custom-iterator-types)
4. [Iterator Adapters](#iterator-adapters)
5. [Pitfalls](#pitfalls)

---

## Why Advanced Iterator Patterns Matter

The `Iterator` trait powers all Rust iteration. Building custom iterators lets you:
- Create lazy sequences from custom data structures
- Control iteration semantics (owned, borrowed, mutable)
- Build composable processing pipelines

---

## Implementing `IntoIterator`

To make your custom type work with `for` loops and iterator adapters:

```rust
struct Range {
    start: i32,
    end: i32,
}

struct RangeIter {
    current: i32,
    end: i32,
}

impl Iterator for RangeIter {
    type Item = i32;

    fn next(&mut self) -> Option<Self::Item> {
        if self.current < self.end {
            let val = self.current;
            self.current += 1;
            Some(val)
        } else {
            None
        }
    }
}

impl IntoIterator for Range {
    type Item = i32;
    type IntoIter = RangeIter;

    fn into_iter(self) -> RangeIter {
        RangeIter { current: self.start, end: self.end }
    }
}

for i in Range { start: 0, end: 5 } {
    println!("{i}");  // 0, 1, 2, 3, 4
}
```

### Three iterator variants for collection types

```rust
struct Items<T>(Vec<T>);

impl<T> Items<T> {
    fn iter(&self) -> impl Iterator<Item = &T> { self.0.iter() }
    fn iter_mut(&mut self) -> impl Iterator<Item = &mut T> { self.0.iter_mut() }
}

impl<T> IntoIterator for Items<T> {
    type Item = T;
    type IntoIter = std::vec::IntoIter<T>;
    fn into_iter(self) -> Self::IntoIter { self.0.into_iter() }
}

impl<'a, T> IntoIterator for &'a Items<T> {
    type Item = &'a T;
    type IntoIter = std::slice::Iter<'a, T>;
    fn into_iter(self) -> Self::IntoIter { self.0.iter() }
}

impl<'a, T> IntoIterator for &'a mut Items<T> {
    type Item = &'a mut T;
    type IntoIter = std::slice::IterMut<'a, T>;
    fn into_iter(self) -> Self::IntoIter { self.0.iter_mut() }
}
```

---

## Custom Iterator Types

### Wrapping an existing iterator

```rust
struct Interleave<I, J> {
    a: I,
    b: J,
    toggle: bool,
}

impl<I, J> Iterator for Interleave<I, J>
where
    I: Iterator,
    J: Iterator<Item = I::Item>,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<Self::Item> {
        self.toggle = !self.toggle;
        if self.toggle {
            self.a.next()
        } else {
            self.b.next()
        }
    }
}
```

### Stateful iterator

```rust
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        let next = self.a.checked_add(self.b)?;  // overflow = stop
        self.a = self.b;
        self.b = next;
        Some(self.a)
    }
}

fn fibonacci() -> Fibonacci {
    Fibonacci { a: 0, b: 1 }
}

assert_eq!(fibonacci().take(5).collect::<Vec<_>>(), vec![1, 1, 2, 3, 5]);
```

---

## Iterator Adapters

### Using `Fuse` for safe iteration after None

```rust
let mut iter = vec![1, 2, 3].into_iter().fuse();
assert_eq!(iter.next(), Some(1));
assert_eq!(iter.next(), Some(2));
assert_eq!(iter.next(), Some(3));
assert_eq!(iter.next(), None);
assert_eq!(iter.next(), None);  // Fuse guarantees continued None
```

### `Peekable` — look ahead

```rust
let mut iter = [1, 2, 3].iter().peekable();
assert_eq!(iter.peek(), Some(&&1));
assert_eq!(iter.next(), Some(&1));
assert_eq!(iter.peek(), Some(&&2));
```

### `Cycle` — infinite repeat

```rust
let mut cycle = [1, 2].iter().cycle();
assert_eq!(cycle.next(), Some(&1));
assert_eq!(cycle.next(), Some(&2));
assert_eq!(cycle.next(), Some(&1));  // wraps around
```

---

## Pitfalls

### Lifetime in custom iterators

```rust
// BAD — returning references requires lifetime annotations
struct RefIter<'a, T> {
    data: &'a [T],
    pos: usize,
}

impl<'a, T> Iterator for RefIter<'a, T> {
    type Item = &'a T;
    fn next(&mut self) -> Option<Self::Item> {
        let item = self.data.get(self.pos)?;
        self.pos += 1;
        Some(item)
    }
}
```

### ExactSizeIterator contract

If you implement `ExactSizeIterator`, `len()` and `size_hint()` must return accurate upper bounds.

### Collection invalidation

Don't create iterators that borrow the collection while mutation is possible elsewhere.

---

> [!question]- Interview Questions
>
> **Q: What are the three iterator variants every collection should implement?**
> A: `.iter()` (borrowed, `&T`), `.iter_mut()` (mutable borrow, `&mut T`), and `.into_iter()` (owned, `T`) via `IntoIterator`.
>
> **Q: What does `Fuse` do?**
> A: It wraps an iterator and ensures that once `next()` returns `None`, it continues returning `None` forever. Prevents undefined behavior from unreliable iterator implementations.

---

## Cross-Links

- [[Rust/01_Foundations/04_Iterators_Collections_and_Slices]] for iterator basics
- [[Rust/01_Foundations/05_Traits_Generics_and_Lifetimes_Intro]] for trait bounds on iterators
- [[Rust/03_Advanced/07_Memory_Layout_and_repr_Attributes]] for memory-efficient iteration

---

## References

- [std::iter::Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html)
- [std::iter::IntoIterator](https://doc.rust-lang.org/std/iter/trait.IntoIterator.html)
- [Iterator adapters (std)](https://doc.rust-lang.org/std/iter/trait.Iterator.html#implementors)
