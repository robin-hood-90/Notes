---
tags: [rust, core, collections, linked-list, binary-heap, vecdeque, btreemap]
aliases: ["LinkedList", "BinaryHeap", "VecDeque", "Lesser Collections", "BTreeMap vs HashMap"]
status: stable
updated: 2026-05-03
---

# `LinkedList`, `BinaryHeap`, and Lesser-Used Collections

> [!summary] Goal
> Know when to reach for the less common standard collections — and when not to.

## Table of Contents

1. [Why These Collections Exist](#why-these-collections-exist)
2. [`LinkedList`](#linkedlist)
3. [`BinaryHeap`](#binaryheap)
4. [`VecDeque`](#vecdeque)
5. [`BTreeMap` vs `HashMap`](#btreemap-vs-hashmap)
6. [Pitfalls](#pitfalls)

---

## Why These Collections Exist

These collections serve specific niches. Using the wrong one (e.g., `LinkedList` for most workloads) hurts performance.

---

## `LinkedList`

A doubly-linked list. **Almost never the right choice.**

```rust
use std::collections::LinkedList;

let mut list = LinkedList::new();
list.push_back(1);
list.push_front(0);
list.push_back(2);
```

### When to use

- **Extremely rare**: constant-time element splicing in the middle (split_off, append)
- Mostly relevant for very specific data structure algorithms

### When NOT to use

```rust
// BAD — Vec is faster for almost everything
let mut list = LinkedList::new();
for i in 0..1000 { list.push_back(i); }
// Iteration is slower than Vec due to cache misses
// Random access is O(n) — no indexing
```

> [!tip] In almost every case where you'd reach for a linked list in other languages, `Vec` or `VecDeque` is faster in Rust.

---

## `BinaryHeap`

A priority queue. Always pops the largest (or smallest with reverse) item.

```rust
use std::collections::BinaryHeap;

let mut heap = BinaryHeap::new();
heap.push(3);
heap.push(5);
heap.push(1);

assert_eq!(heap.pop(), Some(5));  // max element
assert_eq!(heap.pop(), Some(3));
assert_eq!(heap.pop(), Some(1));
```

### Min-heap via reverse order

```rust
use std::collections::BinaryHeap;
use std::cmp::Reverse;

let mut min_heap = BinaryHeap::new();
min_heap.push(Reverse(3));
min_heap.push(Reverse(1));
min_heap.push(Reverse(5));

assert_eq!(min_heap.pop(), Some(Reverse(1)));  // min element
```

### When to use

- Task scheduling (process highest priority first)
- Dijkstra's algorithm
- Merging sorted streams
- Finding top K elements (with fixed-size heap)

---

## `VecDeque`

A double-ended queue. O(1) push/pop at both ends.

```rust
use std::collections::VecDeque;

let mut deque: VecDeque<i32> = VecDeque::new();
deque.push_back(2);
deque.push_back(3);
deque.push_front(1);

assert_eq!(deque.pop_front(), Some(1));
assert_eq!(deque.pop_back(), Some(3));
// remaining: [2]
```

### When to use

| Use case | Why `VecDeque`? |
|----------|----------------|
| **Queue (FIFO)** | `push_back` + `pop_front` — O(1) both ends |
| **Stack (LIFO)** | `push_back` + `pop_back` — but `Vec` is simpler |
| **Sliding window** | `push_back` + `pop_front` |
| **Round-robin** | `push_back` + `pop_front` + re-push |

```rust
// FIFO queue pattern
let mut queue: VecDeque<String> = VecDeque::new();
queue.push_back("job1".into());
queue.push_back("job2".into());

while let Some(job) = queue.pop_front() {
    process(job);
}
```

---

## `BTreeMap` vs `HashMap`

| Aspect | `HashMap` | `BTreeMap` |
|--------|-----------|------------|
| Ordering | None (hash-based) | Sorted by key |
| Lookup | O(1) average | O(log n) |
| Insert/delete | O(1) average | O(log n) |
| Memory per entry | Higher (hash overhead) | Lower |
| Iteration order | Unpredictable | Sorted by key |
| Range queries | Not supported | Supported (range, prefix) |
| Requires | `Hash + Eq` | `Ord` |

```rust
use std::collections::{HashMap, BTreeMap};

// HashMap: fast lookups, no ordering
let mut scores: HashMap<&str, i32> = HashMap::new();
scores.insert("Alice", 95);
scores.insert("Bob", 87);

// BTreeMap: ordered, range queries
let mut sorted: BTreeMap<&str, i32> = BTreeMap::new();
sorted.insert("Alice", 95);
sorted.insert("Bob", 87);

// Range query in BTreeMap
for (name, score) in sorted.range("A".."C") {
    println!("{name}: {score}");  // Alice: 95, Bob: 87
}

// First/last entries
assert_eq!(sorted.first_key_value(), Some((&"Alice", &95)));
assert_eq!(sorted.last_key_value(), Some((&"Bob", &87)));
```

---

## Pitfalls

### LinkedList cache behavior

`LinkedList` allocates each element separately — iteration is pointer-chasing with poor cache locality. `Vec` stores elements contiguously (cache-friendly).

### BinaryHeap is not stable

Equal-priority items may be popped in any order. Use a custom struct with insertion order if stability matters.

### VecDeque vs Vec

`VecDeque` has slightly more overhead per operation than `Vec` for push/pop at the back only. Use `Vec` when you only need stack behavior.

### BTreeMap node overhead

`BTreeMap` has lower per-entry overhead than `HashMap` (no hash table slack), but each node (B-tree page) carries some overhead. Best for large, ordered datasets.

---

> [!question]- Interview Questions
>
> **Q: When would you use `LinkedList` in Rust?**
> A: Almost never. `Vec` or `VecDeque` is faster for nearly all workloads due to cache locality. The only niche is constant-time `split_off`/`append` operations.
>
> **Q: What is the difference between `HashMap` and `BTreeMap`?**
> A: `HashMap` uses hashing for O(1) lookups but no ordering. `BTreeMap` maintains sorted order with O(log n) operations and supports range queries, first/last key access.
>
> **Q: How do you implement a min-heap with `BinaryHeap`?**
> A: Wrap values in `Reverse` (e.g., `BinaryHeap<Reverse<i32>>`). The heap then pops the smallest item.

---

## Cross-Links

- [[Rust/01_Foundations/04_Iterators_Collections_and_Slices]] for core collections
- [[Rust/03_Advanced/11_Cargo_Features_and_Conditional_Compilation]] for feature-gating collections

---

## References

- [std::collections](https://doc.rust-lang.org/std/collections/index.html)
- [Rust Collections Guide](https://doc.rust-lang.org/std/collections/#when-should-you-use-which-collection)
