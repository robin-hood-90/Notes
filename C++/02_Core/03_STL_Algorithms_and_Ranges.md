---
tags: [cpp, core, stl-algorithms, ranges, sort, transform, find, accumulate, algorithm-complexity]
aliases: ["STL Algorithms", "Ranges Library", "Algorithm Complexity", "Functional Composition"]
status: stable
updated: 2026-05-09
---

# STL Algorithms and Ranges

> [!summary] Goal
> Master STL algorithms — non-modifying, modifying, sorting, and numeric operations with complexity guarantees. Understand the Ranges library (C++20) for composable, readable pipelines.

## Table of Contents

1. [Algorithm Categories](#algorithm-categories)
2. [Non-Modifying Algorithms](#non-modifying-algorithms)
3. [Modifying Algorithms](#modifying-algorithms)
4. [Sorting and Partitioning](#sorting-and-partitioning)
5. [Numeric Algorithms](#numeric-algorithms)
6. [Ranges Library (C++20)](#ranges-library)
7. [Algorithm Complexity Table](#algorithm-complexity-table)
8. [Pitfalls](#pitfalls)

---

## Algorithm Categories

> [!info] STL algorithms
> The STL provides ~100 algorithms categorized by operation. They operate on **iterator ranges** `[first, last)`. Each algorithm has documented complexity guarantees. The Ranges library (C++20) provides a more composable, readable interface.

---

## Non-Modifying Algorithms

```cpp
#include <algorithm>
#include <numeric>

std::vector<int> v = {1, 2, 3, 4, 5, 3};
std::vector<int> v2 = {1, 2, 3};

// Search
auto it = std::find(v.begin(), v.end(), 3);              // First 3 → O(n)
auto it2 = std::find_if(v.begin(), v.end(), [](int x) { return x > 3; });  // First >3

bool all = std::all_of(v.begin(), v.end(), [](int x) { return x > 0; });    // true
bool any = std::any_of(v.begin(), v.end(), [](int x) { return x == 5; });   // true
bool none = std::none_of(v.begin(), v.end(), [](int x) { return x > 10; }); // true

auto range = std::equal(v.begin(), v.end(), v2.begin());  // Compare element-by-element
int count = std::count(v.begin(), v.end(), 3);            // Count 3s → 2

// Search for subsequence
auto sub = std::search(v.begin(), v.end(), v2.begin(), v2.end());  // Find subrange
auto adj = std::adjacent_find(v.begin(), v.end());       // First pair of equal adjacents
```

---

## Modifying Algorithms

```cpp
// Copy
std::vector<int> dest(v.size());
std::copy(v.begin(), v.end(), dest.begin());               // Forward copy
std::copy_if(v.begin(), v.end(), std::back_inserter(dest),
    [](int x) { return x % 2 == 0; });                     // Conditional copy

// Transform (map)
std::transform(v.begin(), v.end(), v.begin(),
    [](int x) { return x * 2; });                          // In-place multiply by 2

// Replace
std::replace(v.begin(), v.end(), 3, 99);                   // Replace 3s with 99
std::replace_if(v.begin(), v.end(), [](int x) { return x > 3; }, 0);  // Replace >3 with 0

// Fill / Generate
std::fill(v.begin(), v.end(), 0);                          // Fill entire range
std::generate(v.begin(), v.end(), [n = 0]() mutable { return n++; }); // 0, 1, 2, ...

// Remove (doesn't erase! — use erase-remove idiom)
auto new_end = std::remove(v.begin(), v.end(), 3);         // Moves non-3s to front
v.erase(new_end, v.end());                                 // Actually removes

// Unique (remove consecutive duplicates)
auto unique_end = std::unique(v.begin(), v.end());         // Moves unique to front
v.erase(unique_end, v.end());

// Reverse
std::reverse(v.begin(), v.end());                          // In-place reverse

// Rotate
std::rotate(v.begin(), v.begin() + 2, v.end());           // {3,4,5,1,2} for {1,2,3,4,5}, n=2

// Shuffle
std::random_device rd;
std::mt19937 g(rd());
std::shuffle(v.begin(), v.end(), g);
```

---

## Sorting and Partitioning

```cpp
// Sort (intro sort: quicksort → heapsort)
std::sort(v.begin(), v.end());                     // O(n log n)
std::sort(v.begin(), v.end(), std::greater<>());   // Descending

// Stable sort (preserves relative order of equal elements)
std::stable_sort(v.begin(), v.end());              // O(n log² n) worst

// Partial sort
std::partial_sort(v.begin(), v.begin() + 3, v.end());  // Top 3 sorted, rest unspecified

// nth_element (find the element that would be at position n if sorted)
std::nth_element(v.begin(), v.begin() + v.size()/2, v.end());  // Median (O(n))

// Partition
auto pivot = std::partition(v.begin(), v.end(),
    [](int x) { return x < 10; });                 // All < 10 before, ≥ 10 after
std::stable_partition(...);                        // Stable partition

// Binary search (on sorted range)
bool found = std::binary_search(v.begin(), v.end(), 42);  // O(log n)
auto [lo, hi] = std::equal_range(v.begin(), v.end(), 42); // Range of elements == 42
auto lo = std::lower_bound(v.begin(), v.end(), 42);       // First ≥ 42
auto hi = std::upper_bound(v.begin(), v.end(), 42);       // First > 42
```

---

## Numeric Algorithms

```cpp
#include <numeric>

std::vector<int> v = {1, 2, 3, 4, 5};

// Accumulate (fold)
int sum = std::accumulate(v.begin(), v.end(), 0);                     // 15
int product = std::accumulate(v.begin(), v.end(), 1,
    std::multiplies<>());                                              // 120

// Inner product (dot product)
std::vector<int> w = {5, 4, 3, 2, 1};
int dot = std::inner_product(v.begin(), v.end(), w.begin(), 0);       // 1*5+2*4+...+5*1

// Partial sum
std::vector<int> partials(v.size());
std::partial_sum(v.begin(), v.end(), partials.begin());               // {1, 3, 6, 10, 15}

// Adjacent difference
std::vector<int> diffs(v.size());
std::adjacent_difference(v.begin(), v.end(), diffs.begin());          // {1, 1, 1, 1, 1}

// Iota (fill with increasing values)
std::iota(v.begin(), v.end(), 0);                                     // {0, 1, 2, 3, 4}
```

---

## Ranges Library (C++20)

> [!info] Ranges
> The Ranges library (C++20) provides a new way to compose algorithms using **range adaptors** (`views::filter`, `views::transform`, `views::take`, etc.). Pipelines read left-to-right (not inside-out like iterator-based algorithms). Ranges are **lazy** — they don't create intermediate containers.

```cpp
#include <ranges>

std::vector<int> v = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Iterator-based (C++98 style — hard to read, right-to-left)
std::vector<int> result;
std::copy_if(v.begin(), v.end(), std::back_inserter(result),
    [](int x) { return x % 2 == 0; });
std::transform(result.begin(), result.end(), result.begin(),
    [](int x) { return x * 2; });

// Ranges (C++20 — clean, left-to-right pipeline)
auto result_ranges = v
    | std::views::filter([](int x) { return x % 2 == 0; })   // {2, 4, 6, 8, 10}
    | std::views::transform([](int x) { return x * 2; })     // {4, 8, 12, 16, 20}
    | std::ranges::to<std::vector>();                        // C++23: to<vector>()

// Lazy evaluation — nothing computed until iteration
auto even_view = v | std::views::filter([](int x) { return x % 2 == 0; });
for (int x : even_view) {           // Computation happens here
    std::cout << x << ' ';          // 2 4 6 8 10
}

// Common range adaptors
auto evens = v | std::views::filter([](int n) { return n % 2 == 0; });
auto first3 = v | std::views::take(3);
auto skip2 = v | std::views::drop(2);
auto reversed = v | std::views::reverse;
auto squares = v | std::views::transform([](int n) { return n * n; });

// Combining adaptors
auto result = v
    | std::views::filter([](int n) { return n > 3; })
    | std::views::transform([](int n) { return n * n; })
    | std::views::take(3);

// Ranges algorithms
std::ranges::sort(v);                               // ranges version of std::sort
auto it = std::ranges::find(v, 5);                  // ranges version of std::find
std::ranges::copy(v, dest.begin());                 // ranges version of std::copy

// Projections — sort by member
struct Person { std::string name; int age; };
std::vector<Person> people = {{"Alice", 30}, {"Bob", 25}};
std::ranges::sort(people, {}, &Person::age);        // Sort by age (no custom comparator!)
```

---

## Algorithm Complexity Table

| Algorithm | Complexity | Notes |
|-----------|:----------:|-------|
| `find`, `find_if` | O(n) | Linear search |
| `count`, `count_if` | O(n) | |
| `equal`, `mismatch` | O(n) | |
| `search` | O(n*m) | Substring search (naive) |
| `copy`, `copy_if` | O(n) | |
| `transform` | O(n) | |
| `replace`, `replace_if` | O(n) | |
| `fill`, `generate` | O(n) | |
| `remove` | O(n) | Remove doesn't erase! |
| `unique` | O(n) | Only consecutive duplicates |
| `reverse` | O(n) | |
| `rotate` | O(n) | |
| `sort` | O(n log n) | Intro sort |
| `stable_sort` | O(n log n) | O(n log² n) worst case |
| `partial_sort` | O(n log k) | k = sorted elements count |
| `nth_element` | O(n) | Average case |
| `lower_bound`, `upper_bound` | O(log n) | On sorted range |
| `binary_search` | O(log n) | On sorted range |
| `merge` | O(n) | Merges two sorted ranges |
| `accumulate` | O(n) | |
| `partial_sum` | O(n) | |

---

## Pitfalls

### Erase-remove idiom

`std::remove` moves elements to the front but DOESN'T erase them. The end of the range is returned, and you must call `erase` to actually remove the elements:

```cpp
// ❌ Doesn't actually remove
std::remove(v.begin(), v.end(), 3);              // v.size() unchanged! Elements at end are "removed" but not erased

// ✅ Correct erase-remove
v.erase(std::remove(v.begin(), v.end(), 3), v.end());  // v.size() decreases
```

### Sort on already-sorted data

Quick sort degrades to O(n²) on sorted/reverse-sorted data. `std::sort` uses introsort (quicksort → heapsort if recursion too deep) so it's O(n log n) worst case. But `stable_sort` can still be slow.

### Ranges: views are not owning

```cpp
std::vector<int> getData();

auto view = getData() | std::views::filter([](int n) { return n > 0; });
// ❌ view now holds dangling iterators — getData() returned a temporary!
// The vector is destroyed, the view references freed memory

// ✅ Fix: store the owning container
auto data = getData();
auto view = data | std::views::filter([](int n) { return n > 0; });
```

### Using `std::accumulate` with strings

`std::accumulate` makes a copy for each element when used with strings — O(n²). Use `std::ostringstream` or fold the strings manually.

---

> [!question]- Interview Questions
>
> **Q: What's the erase-remove idiom?**
> A: `std::remove` doesn't actually erase elements — it moves the elements to keep to the front and returns the new logical end. You must call `v.erase(returned_iterator, v.end())` to actually remove them. Combined: `v.erase(std::remove(v.begin(), v.end(), value), v.end());`
>
> **Q: What's the difference between std::sort and std::stable_sort?**
> A: `std::sort` (introsort) generally faster but doesn't preserve the relative order of equal elements. `std::stable_sort` (merge sort variant) preserves order but may be slower (O(n log² n) worst case). Use `stable_sort` when you have a primary and secondary sort key.
>
> **Q: What are C++20 Ranges and why are they better?**
> A: Ranges provide composable, lazy algorithms. Pipelines read left-to-right (`v | views::filter | views::transform`) instead of nested inside-out (`transform(v, filter(v))`). Range adaptors are lazy — no intermediate containers created. Projections (`sort by member`) simplify custom comparisons.
>
> **Q: What's nth_element used for?**
> A: `nth_element` partially sorts so that the element at position n is the one that WOULD be there if the whole range were sorted. Elements before are ≤, after are ≥. O(n) average. Used for: finding the median, top K elements (without sorting everything), percentile calculations.
>
> **Q: How does std::accumulate work and what's its complexity?**
> A: `accumulate(start, end, init, op = +)` computes a left fold over the range. O(n). For `std::string`, it creates a new string object for each concatenation — O(n²). Prefer `std::ostringstream` or `fmt::format` for string building.

---

## Cross-Links

- [[C++/02_Core/02_STL_Containers_Deep_Dive]] for containers that algorithms operate on
- [[C++/02_Core/04_Iterators_and_Iterator_Categories]] for iterator requirements
- [[C++/01_Foundations/08_Lambdas_and_Functional_Programming]] for lambda expressions used in algorithms
- [[C++/01_Foundations/05_Move_Semantics_and_Value_Categories]] for move with algorithms
- [[C++/03_Advanced/07_Performance_Cache_and_Optimization]] for cache-efficient algorithm usage
