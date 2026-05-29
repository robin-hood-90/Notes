---
tags: [dsa, data-structures, java]
aliases: ["DSA Data Structures"]
status: stable
updated: 2026-05-29
---

# Data Structures - Complete Guide (Beginner to Advanced)

> [!summary] One-Stop Revision
> Use this note for choosing the right structure, invariants, and common patterns. For full Java implementations, jump to `[[JAVA_IMPL/Java_01_Fundamental_DS]]` and `[[JAVA_IMPL/Java_02_Advanced_DS]]` (embedded at the relevant sections below).

> [!tip] Quick Jump
> - Implementations index: [[JAVA_IMPL/Java_00_Index_and_CheatSheet]]
> - Algorithms reference: [[Algorithms]]
> - Practice list: [[Questions]]

---
### AtCoder Library (ACL) Mapping

| ACL Component | This Vault Topic |
|---------------|------------------|
| `dsu` | Union-Find (Disjoint Set) |
| `fenwick_tree` | Binary Indexed Tree (Fenwick) |
| `segtree` / `lazysegtree` | Segment Trees (iterative/lazy) |
| `scc_graph` | Strongly Connected Components |
| `maxflow` | Max Flow (Dinic/Edmonds-Karp) |
| `mincostflow` | Min-Cost Max-Flow |
| `twosat` | 2-SAT (implication graph + SCC) |

Use this table to map AtCoder problems directly to the right DS in these notes and Java templates.

## Table of Contents

1. [Arrays](#1-arrays)
2. [Strings](#2-strings)
3. [Linked Lists](#3-linked-lists)
4. [Stacks](#4-stacks)
5. [Queues](#5-queues)
6. [Hash Tables](#6-hash-tables)
7. [Trees](#7-trees)
8. [Heaps / Priority Queues](#8-heaps-priority-queues)
9. [Graphs](#9-graphs)
10. [Tries (Prefix Trees)](#10-tries)
11. [Disjoint Set Union (Union-Find)](#11-disjoint-set-union)
12. [Segment Trees](#12-segment-trees)
13. [Binary Indexed Trees (Fenwick Trees)](#13-binary-indexed-trees)
14. [Suffix Arrays and Suffix Trees](#14-suffix-arrays-and-suffix-trees)
15. [Bloom Filters](#15-bloom-filters)
16. [Skip Lists](#16-skip-lists)
17. [LRU / LFU Caches](#17-lru-lfu-caches)

---

## 1. Arrays

> [!summary] Recall
> - Strength: O(1) random access, cache-friendly.
> - Weakness: inserts/deletes in the middle are O(n).
> - Typical tools: prefix sum, two pointers, sliding window, difference arrays.

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.1 Static Array]]
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.2 Dynamic Array]]

```mermaid
flowchart LR
    subgraph Array["Contiguous Memory Block"]
        A0["Index 0<br/>A"] --- A1["Index 1<br/>B"] --- A2["Index 2<br/>C"] --- A3["Index 3<br/>D"] --- A4["Index 4<br/>E"]
    end
    subgraph Dynamic["Dynamic Array (ArrayList) Doubling"]
        I1["Size=4<br/>[A,B,C,D]"] -->|"push(E)"| I2["Size=4 full<br/>allocate new[8]"]
        I2 --> I3["Copy: [A,B,C,D,_,_,_,_]"]
        I3 --> I4["push(E): [A,B,C,D,E,_,_,_]"]
    end
    subgraph Prefix["Prefix Sum"]
        P1["A=[3,1,4,1,5]"] --> P2["P[1]=3<br/>P[2]=4<br/>P[3]=8<br/>P[4]=9<br/>P[5]=14"]
        P2 --> P3["RangeSum(2,4) = P[4]-P[1] = 9-3 = 6<br/><= A[2]+A[3]+A[4] = 1+4+1 = 6"]
    end
```

### Overview

An array is a contiguous block of memory storing elements of the same type, accessed by index.

### Types

| Type | Description |
|------|-------------|
| **Static Array** | Fixed size, allocated at compile time |
| **Dynamic Array** | Resizable (e.g., `ArrayList` in Java, `vector` in C++, `list` in Python) |
| **2D / Multi-dimensional Array** | Matrix representation, grids |
| **Sparse Array** | Most elements are zero/default; stored efficiently |

### Time Complexity

| Operation | Static Array | Dynamic Array |
|-----------|:---:|:---:|
| Access by index | O(1) | O(1) |
| Search (unsorted) | O(n) | O(n) |
| Search (sorted) | O(log n) | O(log n) |
| Insert at end | N/A | Amortized O(1) |
| Insert at index | O(n) | O(n) |
| Delete at index | O(n) | O(n) |

### Space Complexity

- O(n)

### Key Concepts

- **Contiguous memory** — cache-friendly, excellent locality of reference
- **Amortized doubling** — dynamic arrays double capacity when full; insertion is amortized O(1)
- **Prefix Sum Array** — precompute cumulative sums for O(1) range sum queries
- **Difference Array** — efficient range update in O(1), reconstruct with prefix sum
- **Kadane's Algorithm** — max subarray sum in O(n)
- **Two Pointer Technique** — used on sorted arrays for pair/triplet problems
- **Sliding Window** — fixed or variable window for subarray/substring problems
- **Dutch National Flag** — 3-way partitioning (0s, 1s, 2s)

### Common Patterns

- Reverse an array in-place
- Rotate array by k positions
- Merge two sorted arrays
- Find duplicates (using hash set or sorting)
- Subarray with given sum (prefix sum + hash map)
- Trapping rain water (two pointer / stack)
- Next permutation

### Pseudocode

#### Array Traversal
```
Traverse(A[1 .. n]):
    for i ← 1 to n:
        process A[i]
```

#### Insert at Index
```
Insert(A[1 .. n], index, value):
    for i ← n downto index + 1:
        A[i + 1] ← A[i]
    A[index] ← value
    n ← n + 1
```

#### Delete at Index
```
Delete(A[1 .. n], index):
    for i ← index to n - 1:
        A[i] ← A[i + 1]
    n ← n - 1
```

#### Kadane's Algorithm (Maximum Subarray Sum)
```
Kadane(A[1 .. n]):
    maxSoFar ← -∞
    maxEndingHere ← 0
    for i ← 1 to n:
        maxEndingHere ← max(A[i], maxEndingHere + A[i])
        maxSoFar ← max(maxSoFar, maxEndingHere)
    return maxSoFar
```

#### Dutch National Flag (3-way Partition)
```
DutchFlagPartition(A[1 .. n], pivot):
    low ← 1, mid ← 1, high ← n
    while mid ≤ high:
        if A[mid] < pivot:
            swap A[low] and A[mid]
            low ← low + 1
            mid ← mid + 1
        else if A[mid] = pivot:
            mid ← mid + 1
        else:
            swap A[mid] and A[high]
            high ← high - 1
```

#### Prefix Sum Array (Build)
```
BuildPrefixSum(A[1 .. n]):
    P[1 .. n]  // prefix sum array
    P[1] ← A[1]
    for i ← 2 to n:
        P[i] ← P[i - 1] + A[i]
    return P

RangeSum(P[1 .. n], L, R):
    if L = 1:
        return P[R]
    else:
        return P[R] - P[L - 1]
```

> [!warning] Pitfalls
> - **Off-by-one in 0-indexed vs 1-indexed** — LeetCode uses 0-indexing; many pseudocode references use 1-indexing. When prefix sums are defined as `P[0]=0, P[i]=P[i-1]+A[i-1]`, sum(L,R) = P[R+1] - P[L] (0-indexed) vs P[R] - P[L-1] (1-indexed). Trace an example.
> - **Insert/Delete at front is O(n)** — arrays require shifting all elements. Use a LinkedList or Deque for O(1) front operations.
> - **Multi-dimensional array indexing** — `A[i][j]` in row-major order is at `A + (i * cols + j) * sizeof(T)`. Column-first access destroys cache locality (cache misses on every access). Always iterate rows first, then columns.
> - **Resizing amortized cost** — dynamic arrays (ArrayList, Vector) double capacity, giving O(1) amortized push. But the worst-case single push is O(n). Don't use dynamic arrays in hard real-time systems without preallocation.
> - **Passing slices as copies** — in Java, `Arrays.copyOfRange()` creates a new array (O(n)). In Python, `arr[i:j]` also copies. For read-only views, use the original array with bounds.

> [!question]- Q: Why are arrays O(1) for random access?
> **Answer:** Arrays are stored in contiguous memory. The address of element i is `base_address + i * element_size`. The CPU can compute this address and load the data in a single instruction. No traversal, no pointer chasing — pure arithmetic.

> [!question]- Q: When should I use an array vs a linked list?
> **Answer:** Use an **array** for random access (indexing), cache-friendly iteration, and fixed-size data. Use a **linked list** for frequent insertions/deletions at arbitrary positions (especially front/middle) when you already have a reference to the node. Arrays dominate for most practical purposes due to cache locality.

> [!question]- Q: What is the difference between a static array and a dynamic array?
> **Answer:** Static arrays have fixed size allocated at declaration. Dynamic arrays (ArrayList, Vector) grow automatically by allocating a larger array and copying elements when capacity is exceeded. Amortized insertion is O(1), but resize operations are O(n).

> [!question]- Q: How does Kadane's algorithm find the maximum subarray in O(n)?
> **Answer:** Maintain `currentMax = max(A[i], currentMax + A[i])` and `globalMax = max(globalMax, currentMax)`. At each position, decide whether to extend the previous subarray or start fresh. The intuition: a negative prefix sum can never improve a subarray starting after it.

### Resources

- [Array Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/array-data-structure/)
- [Arrays - mycodeschool (YouTube)](https://www.youtube.com/watch?v=7EdaoE46BTI)
- *Introduction to Algorithms (CLRS)* — Chapter 1-2

---

## 2. Strings

```mermaid
flowchart LR
    subgraph Str["String in memory"]
        S0["H"] --- S1["e"] --- S2["l"] --- S3["l"] --- S4["o"] --- S5["\\0"]
    end
    subgraph Substring["Substring s[1:4]"]
        T0["e"] --- T1["l"] --- T2["l"]
    end
    subgraph StringBuilder["StringBuilder (mutable)"]
        B1["Buffer: [H,e,l,l,o,_,W,o,r,l,d,_,!]"] --> B2["append(): append to end"]
        B2 --> B3["toString(): [H,e,l,l,o, ,W,o,r,l,d, !]"]
    end
```


> [!summary] Recall
> - In Java, `String` is immutable; repeated concatenation can be O(n^2). Use `StringBuilder`.

### Overview

A string is a sequence of characters. Internally represented as a character array (C/C++) or immutable object (Java, Python).

### Key Concepts

- **Immutability** — in Java/Python strings are immutable; modifications create new objects
- **Character encoding** — ASCII (7-bit), Extended ASCII (8-bit), UTF-8, UTF-16, UTF-32
- **StringBuilder / StringBuffer** — mutable string classes for efficient concatenation in Java

### Important Techniques

| Technique | Purpose | Complexity |
|-----------|---------|:---:|
| Two pointers | Palindrome check, reverse | O(n) |
| Sliding window | Longest substring without repeating chars | O(n) |
| Hashing (Rabin-Karp) | Pattern matching | O(n+m) avg |
| KMP Algorithm | Pattern matching | O(n+m) |
| Z-Algorithm | Pattern matching | O(n+m) |
| Manacher's Algorithm | Longest palindromic substring | O(n) |
| Trie | Prefix-based search, autocomplete | O(L) per query |
| Suffix Array | All occurrences, LCP | O(n log n) build |

### Common Operations & Complexity

| Operation | Complexity |
|-----------|:---:|
| Access char at index | O(1) |
| Concatenation | O(n+m) |
| Substring | O(k) where k = length of substring |
| Comparison | O(min(n,m)) |
| Search (brute force) | O(n*m) |

### Common Patterns

- Anagram detection (frequency count)
- Longest common prefix
- String to integer (atoi)
- Valid parentheses
- Palindrome partitioning
- Edit distance (DP)
- Regular expression matching (DP)

### Pseudocode

#### Palindrome Check (Two Pointer)
```
IsPalindrome(S[1 .. n]):
    left ← 1
    right ← n
    while left < right:
        if S[left] ≠ S[right]:
            return false
        left ← left + 1
        right ← right - 1
    return true
```

> [!warning] Pitfalls
> - **Using adjacency matrix for sparse graphs** — if V = 10^5 and E = 10^5, an adjacency matrix uses O(V²) = 10^10 memory (impossible). Always use adjacency list for sparse graphs.
> - **Undirected edges stored only in one direction** — for undirected graphs, adding edge (u, v) must update both `adj[u]` and `adj[v]`. Forgetting one direction breaks traversal.
> - **DFS on deep/recursive graphs** — a chain of 10^5 vertices causes StackOverflowError. Use an explicit Stack or BFS for deep graphs.
> - **Not tracking visited in undirected graphs** — without a visited set, BFS/DFS cycles infinitely between two nodes. In DFS, always pass a `parent` parameter to avoid revisiting the immediate predecessor.
> - **In-degree vs out-degree confusion** — in directed graphs, in-degree counts incoming edges, out-degree counts outgoing. Mixing them up breaks topological sort (uses in-degree), SCC algorithms, and degree-based heuristics.
> - **Graph disconnectedness** — many algorithms (BFS, DFS) only visit the component containing the start vertex. For full coverage, loop over all vertices and run BFS/DFS from each unvisited vertex.

> [!question]- Q: When should I use an adjacency list vs adjacency matrix?
> **Answer:** **Adjacency list**: O(V+E) space, best for sparse graphs (E << V²). Fast edge iteration. **Adjacency matrix**: O(V²) space, best for dense graphs (E ≈ V²). O(1) edge existence check. Use list as default; matrix only when E is large or constant-time edge queries matter.

> [!question]- Q: How do I represent a weighted graph?
> **Answer:** In an adjacency list, store pairs: `adj[u] = [(v1, w1), (v2, w2)]`. In an adjacency matrix, store the weight at `matrix[u][v]` (use 0 or ∞ for no edge). For Dijkstra/Bellman-Ford/Kruskal's, the weight is the edge cost to minimize.

> [!question]- Q: What's the difference between a tree and a graph?
> **Answer:** A tree is a connected, acyclic, undirected graph with exactly V-1 edges. Adding any edge creates a cycle; removing any edge disconnects it. Every tree is a graph; not every graph is a tree.

> [!question]- Q: How do you detect if a graph has a cycle?
> **Answer:** **Undirected**: DFS with parent tracking — if you visit an already-visited neighbor that is not the parent, there's a cycle. **Directed**: three-color DFS (white/gray/black) — a back edge (gray → gray) indicates a cycle. Or use Kahn's topological sort — if not all nodes are dequeued, there's a cycle.

> [!warning] Pitfalls
> - **String immutability + repeated concatenation** — `s += "a"` in a loop creates a new string each time (O(n²) total). Use `StringBuilder` (Java) or `''.join()` (Python) for building strings in loops.
> - **Using `==` instead of `.equals()` in Java** — `str1 == str2` compares references, not content. Two identical strings from different sources (e.g., substring vs literal) will have different references.
> - **Substring memory leak (Java 6 and earlier)** — `substring()` shared the original string's char array, keeping the large original from being GC'd. Fixed in Java 7+. Still worth knowing for legacy systems.
> - **Case sensitivity by default** — `"Apple".equals("apple")` is false. Normalize with `.toLowerCase()` or `.equalsIgnoreCase()` unless case matters.
> - **Regex vs indexOf for single char/string search** — `str.indexOf(ch)` is O(n) and ~10x faster than `str.matches(".*ch.*")` which compiles a regex. Use regex only for pattern matching, never for simple substring checks.

> [!question]- Q: What is the difference between `String`, `StringBuilder`, and `StringBuffer`?
> **Answer:** **String**: immutable — safe for sharing, keys in maps, thread-safe. **StringBuilder**: mutable, not thread-safe — fastest for single-threaded string building. **StringBuffer**: mutable, thread-safe (synchronized) — slower than StringBuilder; use only when multi-threaded mutation is needed.

> [!question]- Q: How is a string stored in memory?
> **Answer:** In Java: char array (UTF-16). Java 9+ uses compact strings: `byte[]` with LATIN1 (1 byte/char) or UTF16 (2 bytes/char) encoding based on content, saving ~50% memory for ASCII-heavy strings. Python: flexible string representation, immutable, with interning for small strings.

> [!question]- Q: How do you reverse a string?
> **Answer:** Java: `new StringBuilder(s).reverse().toString()` (O(n)). In-place: convert to char array, swap from both ends. For words: split, reverse each word and the word list. Constant extra space: reverse the whole string, then reverse each word individually.

> [!question]- Q: What is string interning?
> **Answer:** Java maintains a pool of unique string literals. `String s = "hello"` uses the interned copy; `new String("hello")` creates a new object. Call `s.intern()` to get the canonical copy. Interning saves memory for repeated strings but adds lookup overhead.

### Resources

- [String Algorithms - CP-Algorithms](https://cp-algorithms.com/string/)
- [KMP Algorithm - Abdul Bari (YouTube)](https://www.youtube.com/watch?v=V5-7GzOfADQ)

---

## 3. Linked Lists

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.3 Singly Linked List]]
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.4 Doubly Linked List]]

### Overview

A linked list is a linear data structure where each element (node) contains data and a pointer to the next node.

```mermaid
flowchart LR
    subgraph Node["Node Structure"]
        N["| data | next |"] --> N2["|  5   |  ————→"]
    end
    subgraph InsertHead["Insertion at Head"]
        A1["Head → | 3 | → | 7 | → | 1 | null"] --> A2["newnode = | 9 | → Head"]
        A2 --> A3["Head → | 9 | → | 3 | → | 7 | → | 1 | null"]
    end
    subgraph Reverse["Reverse Iterative"]
        B1["null ← prev<br/>curr → | A | → | B | → | C | → null"] --> B2["Step: curr.next = prev<br/>null ← | A | &nbsp;&nbsp;| B | → | C |"]
        B2 --> B3["After loop<br/>prev → | C | → | B | → | A | → null"]
    end
```

### Types

| Type | Description |
|------|-------------|
| **Singly Linked List** | Each node points to the next node |
| **Doubly Linked List** | Each node points to both next and previous |
| **Circular Linked List** | Last node points back to the first |
| **Circular Doubly Linked List** | Doubly linked + circular |
| **Skip List** | Multi-level linked list for O(log n) search |
| **XOR Linked List** | Memory-efficient doubly linked list using XOR of addresses |

### Time Complexity

| Operation | Singly | Doubly |
|-----------|:---:|:---:|
| Access by index | O(n) | O(n) |
| Search | O(n) | O(n) |
| Insert at head | O(1) | O(1) |
| Insert at tail | O(n) or O(1) with tail pointer | O(1) |
| Insert after node | O(1) | O(1) |
| Delete head | O(1) | O(1) |
| Delete given node | O(n) | O(1) |

### Space Complexity

- O(n)

### Key Concepts

- **Sentinel / Dummy Node** — simplifies edge cases (empty list, head deletion)
- **Fast and Slow Pointers (Floyd's)** — cycle detection, finding middle node
- **Runner Technique** — two pointers at different speeds

### Common Patterns

- Reverse a linked list (iterative & recursive)
- Detect cycle and find cycle start (Floyd's algorithm)
- Find middle element
- Merge two sorted lists
- Remove Nth node from end (two pointers with gap)
- Intersection point of two lists
- Flatten a multilevel linked list
- LRU Cache implementation (doubly linked list + hash map)
- Clone a linked list with random pointers

### Pseudocode

#### Node Structure
```
class Node:
    data
    next  → Node        # singly
    prev  → Node        # doubly (additional)
```

#### Insert at Head
```
InsertAtHead(head, value):
    newNode ← new Node with data ← value
    newNode.next ← head
    if head ≠ NIL:
        head.prev ← newNode        // if doubly linked
    head ← newNode
```

#### Insert After Node
```
InsertAfter(node, value):
    newNode ← new Node with data ← value
    newNode.next ← node.next
    newNode.prev ← node
    if node.next ≠ NIL:
        node.next.prev ← newNode
    node.next ← newNode
```

#### Delete Given Node
```
DeleteNode(head, node):
    if node.prev ≠ NIL:
        node.prev.next ← node.next
    else:
        head ← node.next            // deleting head
    if node.next ≠ NIL:
        node.next.prev ← node.prev
```

#### Reverse (Iterative)
```
Reverse(head):
    prev ← NIL
    curr ← head
    while curr ≠ NIL:
        next ← curr.next             // save next
        curr.next ← prev             // reverse link
        prev ← curr
        curr ← next
    return prev                      // new head
```

#### Floyd's Cycle Detection
```
DetectCycle(head):
    slow ← head
    fast ← head
    while fast ≠ NIL and fast.next ≠ NIL:
        slow ← slow.next
        fast ← fast.next.next
        if slow = fast:
            return true              // cycle exists
    return false
```

#### Merge Two Sorted Lists
```
MergeTwoSorted(L1, L2):
    dummy ← new Node
    tail ← dummy
    while L1 ≠ NIL and L2 ≠ NIL:
        if L1.data ≤ L2.data:
            tail.next ← L1
            L1 ← L1.next
        else:
            tail.next ← L2
            L2 ← L2.next
        tail ← tail.next
    if L1 ≠ NIL: tail.next ← L1
    if L2 ≠ NIL: tail.next ← L2
    return dummy.next
```

#### Remove Nth from End
```
RemoveNthFromEnd(head, n):
    dummy ← new Node with next ← head
    fast ← dummy
    slow ← dummy
    for i ← 1 to n + 1:
        fast ← fast.next
    while fast ≠ NIL:
        slow ← slow.next
        fast ← fast.next
    slow.next ← slow.next.next       // delete node
    return dummy.next
```

> [!warning] Pitfalls
> - **NullPointerException from uninitialized next** — newly created nodes have `next = null` by default, but forgetting to set it explicitly when linking causes NPEs downstream. Always structure insertion as: `newNode.next = prev.next; prev.next = newNode;`.
> - **Head deletion without a dummy node** — deleting the first node requires updating the head reference. Using a `dummy` node pointing to head eliminates this special case. Same for insertion at position 0.
> - **Cycle detection with Floyd's algorithm** — the fast pointer moves `fast = fast.next.next`. If `fast.next` is null before the second dereference, you get NPE. Always check `fast != null && fast.next != null` in the loop condition.
> - **Forgetting to update both ends in doubly linked lists** — inserting between A and B requires: `newNode.prev = A; newNode.next = B; A.next = newNode; B.prev = newNode;` — 4 pointer updates. Missing any one corrupts the list.
> - **Using linked lists for cache-heavy workloads** — each node lives in a separate heap allocation (poor locality). Iterating a linked list is ~5-10x slower than iterating an array of the same size due to cache misses. Use arrays unless frequent O(1) mid-list insertions are required.

> [!question]- Q: How do you reverse a linked list in-place?
> **Answer:** Use three pointers: `prev=null, curr=head`. In a loop: `nextTemp = curr.next; curr.next = prev; prev = curr; curr = nextTemp`. Return `prev` as the new head. O(n) time, O(1) space. This is the most-asked linked list interview question.

> [!question]- Q: What's the difference between singly and doubly linked lists?
> **Answer:** **Singly**: each node has `next` pointer only. Simpler, less memory. Can only traverse forward. **Doubly**: each node has `next` and `prev` pointers. Supports O(1) deletion given a node reference (not just the predecessor). Used in LRU cache, Deque implementations.

> [!question]- Q: How does Floyd's cycle detection algorithm work?
> **Answer:** Use fast (2 steps) and slow (1 step) pointers. If they meet, a cycle exists. To find the cycle start: reset slow to head, move both at 1 step until they meet — that's the cycle entry. O(n) time, O(1) space. No hash set needed.

> [!question]- Q: Why use a dummy/sentinel node?
> **Answer:** It eliminates edge cases for operations at the head of the list. With a dummy node, head insertion, head deletion, and empty-list handling become identical to mid-list operations. Code becomes shorter and less error-prone.

### Resources

- [Linked List - GeeksforGeeks](https://www.geeksforgeeks.org/data-structures/linked-list/)
- [Linked Lists - mycodeschool (YouTube)](https://www.youtube.com/playlist?list=PL2_aWCzGMAwI3W_JlcBbtYTwiQSsOTa6P)

---

## 4. Stacks

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.6 Stack (Array Implementation)]]
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.7 Stack (Linked Implementation)]]

### Overview

A stack is a Last-In-First-Out (LIFO) data structure. Think of it as a stack of plates.

```mermaid
flowchart LR
    subgraph Stack["Stack operations"]
        S0["[]"] --> S1["push(A)\n[A]"]
        S1 --> S2["push(B)\n[A,B]"]
        S2 --> S3["pop() → B\n[A]"]
        S3 --> S4["push(C)\n[A,C]"]
        S4 --> S5["peek() → C\n[A,C]"]
    end
```

### Operations & Complexity

| Operation | Complexity |
|-----------|:---:|
| Push | O(1) |
| Pop | O(1) |
| Peek / Top | O(1) |
| isEmpty | O(1) |
| Search | O(n) |

### Implementation

- **Array-based** — simple, fixed or dynamic size
- **Linked-list-based** — push/pop at head

### Key Concepts

- **Monotonic Stack** — stack where elements are in increasing or decreasing order; used for next greater/smaller element problems
- **Min Stack** — stack that supports getMin() in O(1)
- **Two Stacks in One Array** — space optimization
- **Stack using Queues** — and vice versa

### Common Patterns

- Valid parentheses / balanced brackets
- Next Greater Element (monotonic stack)
- Next Smaller Element
- Largest Rectangle in Histogram
- Evaluate Reverse Polish Notation
- Implement calculator (infix to postfix)
- Daily temperatures
- Trapping rain water (stack approach)
- Decode string (nested encoding)
- Asteroid collision

### Call Stack & Recursion

- Every recursive function uses the call stack implicitly
- Stack overflow occurs when recursion depth exceeds stack size
- Tail call optimization eliminates stack growth for tail-recursive functions

### Pseudocode

#### Stack (Array Implementation)
```
Stack:
    A[1 .. MAX]   // backing array
    top ← 0

Push(x):
    top ← top + 1
    A[top] ← x

Pop():
    if top = 0:
        error "underflow"
    x ← A[top]
    top ← top - 1
    return x

Peek():
    if top = 0:
        error "underflow"
    return A[top]

IsEmpty():
    return top = 0
```

#### Monotonic Stack — Next Greater Element
```
NextGreaterElement(A[1 .. n]):
    result[1 .. n] ← -1
    stack ← empty
    for i ← 1 to n:
        while stack is not empty and A[stack.top()] < A[i]:
            j ← stack.pop()
            result[j] ← A[i]
        stack.push(i)
    return result
```

#### Evaluate Reverse Polish Notation
```
EvalRPN(tokens[1 .. n]):
    stack ← empty
    for each token in tokens:
        if token is a number:
            stack.push(token)
        else:
            b ← stack.pop()
            a ← stack.pop()
            result ← apply operator(token, a, b)
            stack.push(result)
    return stack.top()
```

#### Infix to Postfix (Shunting-Yard)
```
InfixToPostfix(infix[1 .. n]):
    output ← []
    opStack ← empty
    for each token in infix:
        if token is operand:
            output.append(token)
        else if token = '(':
            opStack.push(token)
        else if token = ')':
            while opStack.top() ≠ '(':
                output.append(opStack.pop())
            opStack.pop()             // discard '('
        else if token is operator:
            while opStack is not empty and Precedence(opStack.top()) ≥ Precedence(token):
                output.append(opStack.pop())
            opStack.push(token)
    while opStack is not empty:
        output.append(opStack.pop())
    return output
```

> [!warning] Pitfalls
> - **Popping from an empty stack** — always check `isEmpty()` before pop/peek. Java's `Stack.pop()` throws `EmptyStackException`; Deque's `pop()` throws `NoSuchElementException`.
> - **Using Stack (legacy) vs Deque** — `java.util.Stack` extends `Vector` and is synchronized (slow). Use `ArrayDeque` or `LinkedList` as a Deque for stack operations: `push()`, `pop()`, `peek()`.
> - **Recursive stack overflow for large problems** — deep recursion (e.g., DFS on a 10^5-node chain, unbounded tree traversal) exceeds the call stack. Convert to an explicit Stack for iterative DFS tail recursion.
> - **Forgetting Stack for monotonic stack patterns** — problems like "next greater element," "largest rectangle in histogram," and "daily temperatures" all use a monotonic stack. Recognizing the monotonic pattern is the key to solving them.

> [!question]- Q: What are the key LIFO applications of a stack?
> **Answer:** (1) Undo/Redo in editors. (2) Back/Forward in browsers. (3) Expression evaluation (infix → postfix, calculator). (4) Parenthesis matching. (5) Function call stack. (6) DFS graph traversal. (7) Monotonic stack (next greater/smaller element).

> [!question]- Q: How does a monotonic stack work?
> **Answer:** Maintain elements in strictly increasing or decreasing order. When a new element violates the monotonic property, pop elements from the stack until the property is restored. Popped elements are processed ("next greater element found"). Each element is pushed and popped at most once → O(n).

> [!question]- Q: What's the relationship between recursion and stacks?
> **Answer:** Every recursive function implicitly uses the call stack — each call pushes a stack frame with local variables and return address. Tail recursion can be optimized to avoid stack growth. Explicit stacks convert recursive algorithms (DFS, backtracking) to iterative ones.

> [!question]- Q: How do you implement a stack using queues (or vice versa)?
> **Answer:** Stack using 2 queues: push → enqueue to q1. pop → dequeue q1 into q2 until last element, dequeue that element, swap q1 and q2. O(n) pop, O(1) push. Can be made O(1) amortized with a single queue where push rotates the queue.

### Resources

- [Stack Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/stack-data-structure/)
- [Stacks - William Fiset (YouTube)](https://www.youtube.com/watch?v=RBSGKlAvoiM)

---

## 5. Queues

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.8 Queue (Array Implementation)]]
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.9 Queue (Linked Implementation)]]
> ![[JAVA_IMPL/Java_01_Fundamental_DS#A.11 Deque]]

### Overview

A queue is a First-In-First-Out (FIFO) data structure.

```mermaid
flowchart LR
    subgraph Queue["Queue (front → back)"]
        Q0["[]"] --> Q1["enqueue(A)\n[A]"]
        Q1 --> Q2["enqueue(B)\n[A,B]"]
        Q2 --> Q3["dequeue() → A\n[B]"]
        Q3 --> Q4["enqueue(C)\n[B,C]"]
    end
    subgraph Circular["Circular Buffer (size=4)"]
        C0["head=0 tail=2\n[A,B,_,_]"] --> C1["enqueue(C)\nhead=0 tail=3\n[A,B,C,_]"]
        C1 --> C2["dequeue()\nhead=1 tail=3\n[_,B,C,_]"]
    end
```

### Types

| Type | Description |
|------|-------------|
| **Simple Queue** | FIFO order |
| **Circular Queue** | Wraps around; efficient use of array space |
| **Double-Ended Queue (Deque)** | Insert/delete from both ends |
| **Priority Queue** | Elements dequeued by priority (see Heaps) |
| **Monotonic Queue (Deque)** | Maintains monotonic order for sliding window problems |

### Operations & Complexity

| Operation | Queue | Deque |
|-----------|:---:|:---:|
| Enqueue / Push | O(1) | O(1) |
| Dequeue / Pop | O(1) | O(1) |
| Peek front | O(1) | O(1) |
| Peek back | N/A | O(1) |

### Common Patterns

- BFS traversal (graphs, trees)
- Sliding window maximum (monotonic deque)
- Generate binary numbers 1 to N
- First non-repeating character in stream
- Implement stack using queues
- Task scheduling (Round Robin)
- Rotten oranges (multi-source BFS)

### Pseudocode

#### Queue (Circular Array)
```
Queue:
    A[1 .. MAX]
    front ← 1, rear ← 1, size ← 0

Enqueue(x):
    if size = MAX:
        error "overflow"
    A[rear] ← x
    rear ← (rear mod MAX) + 1
    size ← size + 1

Dequeue():
    if size = 0:
        error "underflow"
    x ← A[front]
    front ← (front mod MAX) + 1
    size ← size - 1
    return x

Peek():
    if size = 0:
        error "underflow"
    return A[front]

IsEmpty():
    return size = 0
```

#### Deque (Doubly Ended Queue)
```
Deque:
    A[1 .. MAX]
    front ← 1, rear ← 1, size ← 0

PushFront(x):
    front ← front - 1; if front < 1: front ← MAX
    A[front] ← x
    size ← size + 1

PushBack(x):
    A[rear] ← x
    rear ← (rear mod MAX) + 1
    size ← size + 1

PopFront():
    x ← A[front]
    front ← (front mod MAX) + 1
    size ← size - 1
    return x

PopBack():
    rear ← rear - 1; if rear < 1: rear ← MAX
    size ← size - 1
    return A[rear]
```

#### Sliding Window Maximum (Monotonic Deque)
```
SlidingWindowMax(A[1 .. n], k):
    result ← []
    dq ← empty Deque    // stores indices
    for i ← 1 to n:
        // remove indices outside current window
        while dq is not empty and dq.front() < i - k + 1:
            dq.popFront()
        // maintain decreasing order
        while dq is not empty and A[dq.back()] ≤ A[i]:
            dq.popBack()
        dq.pushBack(i)
        if i ≥ k:
            result.append(A[dq.front()])
    return result
```

#### Stack Using Two Queues
```
StackUsingQueues:
    Push(x):
        q2.enqueue(x)
        while q1 is not empty:
            q2.enqueue(q1.dequeue())
        swap q1 and q2

    Pop():
        return q1.dequeue()

    Top():
        return q1.peek()
```

> [!warning] Pitfalls
> - **Confusing Queue (FIFO) with Stack (LIFO)** — Queue: first in, first out (like a line). Stack: last in, first out (like a stack of plates). Mismatching them causes completely wrong algorithm behavior.
> - **Using LinkedList as Queue** — `LinkedList` implements `Queue` but `add()`/`remove()` throw exceptions on failure, while `offer()`/`poll()` return false/null. Use the latter for non-exceptional control flow.
> - **BFS with wrong data structure** — BFS requires a queue (FIFO) for level-order traversal. Using a stack (DFS) changes semantics and produces depth-first order.
> - **Circular queue index wrapping** — `rear = (rear + 1) % capacity`. Forgetting the modulo causes index out of bounds. Also, tracking `size` separately avoids ambiguity between full and empty states (when front == rear).
> - **Deque operations on the wrong end** — `addFirst()` vs `addLast()`, `pollFirst()` vs `pollLast()`. Using the wrong end effectively reverses queue behavior. Read the method name carefully.

> [!question]- Q: What's the difference between Queue, Deque, and PriorityQueue?
> **Answer:** **Queue** = FIFO (first in, first out). **Deque** = double-ended (can add/remove from both ends) — can act as both stack and queue. **PriorityQueue** = elements ordered by priority (min or max) regardless of insertion order. Each serves a different use case.

> [!question]- Q: When is a circular queue needed?
> **Answer:** When you have a fixed-size buffer and want to reuse slots. Examples: keyboard buffer, network packet buffer, audio processing, message queues. Circular queues avoid shifting elements (which O(n) arrays require) by wrapping the write pointer around.

> [!question]- Q: How do you implement a queue using two stacks?
> **Answer:** Push stack (for enqueue) + Pop stack (for dequeue). Enqueue: push to Push stack. Dequeue: if Pop stack is empty, pop all from Push stack and push to Pop stack (reversing order), then pop from Pop stack. Amortized O(1) per operation.

> [!question]- Q: What are practical applications of Deques?
> **Answer:** Sliding window maximum (monotonic deque), palindrome checking (compare from both ends), undo/redo with history limits, work-stealing in parallel computing (deque per thread), and LRU cache (remove oldest from one end, promote to other).

### Resources

- [Queue Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/queue-data-structure/)
- [Queues - William Fiset (YouTube)](https://www.youtube.com/watch?v=KxzhEQ-zpDc)

---

## 6. Hash Tables

### Overview

> [!tip] Intuition
> Imagine a library where every book has a unique call number. To find a book, you don't scan every shelf — you compute the call number's position and go directly there. A hash table does the same: feed a key into a hash function, get back an array index, and retrieve the value in O(1). The challenge (and the art) is handling **collisions** — when two keys hash to the same slot.

```mermaid
flowchart TD
    subgraph HashOps["Hash Table Operations"]
        H1["Insert: key='cat', hash(cat)=5 → store at index 5"]
        H2["Lookup: key='cat', hash(cat)=5 → found at index 5"]
        H3["Delete: key='cat', hash(cat)=5 → mark as deleted/tombstone"]
    end
    subgraph Collision["Collision: Separate Chaining"]
        C1["Index 2: 'dog' → 'cat' (same hash) → 'bird'"] --> C2["Each bucket is a linked list"]
        C2 --> C3["Insert: append to list. Lookup: traverse list."]
    end
```

A hash table maps keys to values using a hash function. Provides average O(1) lookup, insertion, and deletion.

### Components

1. **Hash Function** — maps key to an index
   - Properties: deterministic, uniform distribution, fast computation
   - Examples: division method, multiplication method, universal hashing, MurmurHash, SHA-256
2. **Collision Resolution**
   - **Chaining** — each bucket holds a linked list / balanced BST
   - **Open Addressing** — probe for next empty slot
     - Linear Probing: `h(k, i) = (h(k) + i) mod m`
     - Quadratic Probing: `h(k, i) = (h(k) + c1*i + c2*i^2) mod m`
     - Double Hashing: `h(k, i) = (h1(k) + i*h2(k)) mod m`

### Time Complexity

| Operation | Average | Worst |
|-----------|:---:|:---:|
| Insert | O(1) | O(n) |
| Delete | O(1) | O(n) |
| Search | O(1) | O(n) |

### Space Complexity

- O(n)

### Key Concepts

- **Load Factor** — `α = n / m` (number of elements / number of buckets)
- **Rehashing** — resize and rehash when load factor exceeds threshold (~0.75)
- **Perfect Hashing** — O(1) worst-case for static sets
- **Consistent Hashing** — used in distributed systems
- **Rolling Hash** — used in Rabin-Karp string matching

### Language Implementations

| Language | Hash Map | Hash Set |
|----------|----------|----------|
| Java | `HashMap`, `LinkedHashMap`, `ConcurrentHashMap` | `HashSet` |
| Python | `dict` | `set` |
| C++ | `unordered_map` | `unordered_set` |
| JavaScript | `Map`, `Object` | `Set` |

### Common Patterns

- Two Sum (hash map for complement lookup)
- Group anagrams
- Longest consecutive sequence
- Subarray sum equals K (prefix sum + hash map)
- First unique character
- Isomorphic strings
- Design HashMap from scratch
- Count frequency of elements

### Pseudocode

#### Direct-Address Table
```
DirectAddressSearch(T, k):
    return T[k]

DirectAddressInsert(T, x):
    T[x.key] ← x

DirectAddressDelete(T, x):
    T[x.key] ← NIL
```

#### Chaining — Insert and Search
```
ChainedHashInsert(T, x):
    hash ← Hash(x.key)
    insert x at head of list T[hash]

ChainedHashSearch(T, k):
    hash ← Hash(k)
    for each node in list T[hash]:
        if node.key = k:
            return node
    return NIL

ChainedHashDelete(T, x):
    hash ← Hash(x.key)
    remove x from list T[hash]
```

#### Open Addressing — Linear Probing
```
HashInsert(T, x):
    i ← 0
    repeat:
        j ← Hash(x.key, i)       // h(k, i) = (h'(k) + i) mod m
        if T[j] = NIL or T[j] = DELETED:
            T[j] ← x
            return j
        i ← i + 1
    until i = m
    error "hash table overflow"

HashSearch(T, k):
    i ← 0
    repeat:
        j ← Hash(k, i)
        if T[j] = NIL:
            return NIL            // not found
        if T[j].key = k:
            return T[j]
        i ← i + 1
    until i = m
    return NIL
```

#### Rolling Hash (Polynomial Rolling)
```
// h(S) = (c1 * a^(n-1) + c2 * a^(n-2) + ... + cn) mod m
ComputeRollingHash(S[1 .. n], a, m):
    hash ← 0
    for i ← 1 to n:
        hash ← (hash * a + S[i]) mod m
    return hash

SlideHash(oldHash, leftChar, rightChar, a, aPow_n, m):
    // remove left char, add right char in O(1)
    newHash ← (oldHash - leftChar * aPow_n) mod m
    if newHash < 0: newHash ← newHash + m
    newHash ← (newHash * a + rightChar) mod m
    return newHash
```

> [!warning] Pitfalls
> - **Using mutable objects as keys** — if a key's hash changes after insertion, the value becomes unfindable (it's in the wrong bucket). Always use immutable objects (String, Integer) as keys.
> - **Poor hash function causing clustering** — a hash function that maps everything to the same bucket degrades O(1) to O(n). Use a well-distributed hash (e.g., `Objects.hash()` in Java, or multiply by a large prime).
> - **Load factor too high** — when the load factor exceeds ~0.75, collision chains grow and performance degrades. Rehash (resize to ~2x capacity) before it gets bad.
> - **Modifying a collection while iterating** — removing entries via `map.keySet().remove()` during iteration may cause `ConcurrentModificationException`. Use `Iterator.remove()` or collect keys first, then remove.
> - **Integer overflow in rolling hash** — when computing hash codes modulo m, intermediate products like `hash * 31 + c` can overflow 32-bit int. Java's `String.hashCode()` intentionally allows overflow (wrap-around); if you need collision control, use a large prime modulo.
> - **Assuming HashMap iteration order** — `HashMap` does not guarantee insertion order. Use `LinkedHashMap` (insertion order) or `TreeMap` (sorted order) when order matters.

> [!question]- Q: How does a hash function work?
> **Answer:** It maps a key to an integer array index. A good hash function: (1) is deterministic (same key → same index), (2) distributes uniformly, (3) is fast to compute. Common approach: `hash(key) % array_size`, where `hash(key)` is the key's hashCode blended with bit shifts and prime multiplication.

> [!question]- Q: What's the difference between separate chaining and open addressing?
> **Answer:** **Separate chaining**: each bucket holds a linked list (or BST) of collided entries. Simpler, handles high load factors well. **Open addressing**: when a slot is taken, probe for the next empty slot (linear probing, quadratic probing, double hashing). Better cache locality but degrades badly at high load factors.

> [!question]- Q: Why is load factor 0.75 the default in Java's HashMap?
> **Answer:** It balances time and space. Below 0.75: sparse array, good performance but wastes memory. Above 0.75: collision probability increases rapidly. At 0.75, expected probes for open addressing ≈ 2.5; for separate chaining, average chain length ≈ 0.75. The default hits a sweet spot.

> [!question]- Q: How does rehashing work?
> **Answer:** When the load factor exceeds the threshold, create a new array (typically 2x size), then re-insert every entry: compute `hash(key) % new_size` for each key-value pair. Rehashing is O(n) but amortized over all insertions, it's O(1) per insert.

### Resources

- [Hashing - GeeksforGeeks](https://www.geeksforgeeks.org/hashing-data-structure/)
- [Hash Tables - CS50 (YouTube)](https://www.youtube.com/watch?v=nvzVHwrrub0)
- *CLRS* — Chapter 11

---

## 7. Trees

![[assets/binary-tree.png|650]]

```mermaid
flowchart TD
  A[Tree Problem] --> B{Need ordered operations?}
  B -->|Yes| BST[BST / Balanced BST]
  B -->|No| BT[Binary Tree]
  BST --> AVL[AVL (more strict balance)]
  BST --> RB[Red-Black (fewer rotations)]
```

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_01_Fundamental_DS#C.1 Binary Tree]]
> ![[JAVA_IMPL/Java_01_Fundamental_DS#C.2 Binary Search Tree]]
> ![[JAVA_IMPL/Java_01_Fundamental_DS#C.3 AVL Tree]]
> ![[JAVA_IMPL/Java_02_Advanced_DS#E.1 Red-Black Tree]]

### Overview

A tree is a hierarchical data structure consisting of nodes connected by edges, with one root node and zero or more subtrees.

### Terminology

| Term | Definition |
|------|------------|
| **Root** | Top node with no parent |
| **Leaf** | Node with no children |
| **Depth** | Number of edges from root to node |
| **Height** | Number of edges from node to deepest leaf |
| **Degree** | Number of children of a node |
| **Subtree** | Tree formed by a node and all its descendants |
| **Level** | Depth + 1 (root is level 1) |
| **Ancestor / Descendant** | Parent chain / child chain |

---

### 7.1 Binary Tree

A tree where each node has at most 2 children (left, right).

**Types of Binary Trees:**

| Type | Property |
|------|----------|
| **Full (Strict)** | Every node has 0 or 2 children |
| **Complete** | All levels filled except possibly last (filled left to right) |
| **Perfect** | All internal nodes have 2 children; all leaves at same level |
| **Balanced** | Height difference between left and right subtrees ≤ 1 |
| **Degenerate (Skewed)** | Each node has only one child (essentially a linked list) |

**Traversals:**

| Traversal | Order | Use Case |
|-----------|-------|----------|
| **Preorder** | Root → Left → Right | Copy tree, serialize |
| **Inorder** | Left → Root → Right | BST sorted order |
| **Postorder** | Left → Right → Root | Delete tree, evaluate expression |
| **Level Order (BFS)** | Level by level | Breadth-first problems |
| **Morris Traversal** | Inorder without stack/recursion | O(1) space traversal |

**Properties:**
- Max nodes at level `l` = `2^l`
- Max nodes in tree of height `h` = `2^(h+1) - 1`
- Min height of n nodes = `floor(log2(n))`
- Number of leaf nodes = number of internal nodes with 2 children + 1

#### Pseudocode — Binary Tree Traversals

##### Recursive Traversals
```
Preorder(root):
    if root = NIL: return
    Visit(root)
    Preorder(root.left)
    Preorder(root.right)

Inorder(root):
    if root = NIL: return
    Inorder(root.left)
    Visit(root)
    Inorder(root.right)

Postorder(root):
    if root = NIL: return
    Postorder(root.left)
    Postorder(root.right)
    Visit(root)
```

##### Iterative Traversals (Using Stack)
```
InorderIterative(root):
    stack ← empty
    curr ← root
    while curr ≠ NIL or stack is not empty:
        while curr ≠ NIL:
            stack.push(curr)
            curr ← curr.left
        curr ← stack.pop()
        Visit(curr)
        curr ← curr.right

PreorderIterative(root):
    if root = NIL: return
    stack ← empty
    stack.push(root)
    while stack is not empty:
        node ← stack.pop()
        Visit(node)
        if node.right ≠ NIL: stack.push(node.right)
        if node.left ≠ NIL:  stack.push(node.left)

PostorderIterative(root):
    stack1 ← empty, stack2 ← empty
    stack1.push(root)
    while stack1 is not empty:
        node ← stack1.pop()
        stack2.push(node)
        if node.left ≠ NIL:  stack1.push(node.left)
        if node.right ≠ NIL: stack1.push(node.right)
    while stack2 is not empty:
        Visit(stack2.pop())
```

##### Level Order (BFS)
```
LevelOrder(root):
    if root = NIL: return
    queue ← empty
    queue.enqueue(root)
    while queue is not empty:
        node ← queue.dequeue()
        Visit(node)
        if node.left ≠ NIL:  queue.enqueue(node.left)
        if node.right ≠ NIL: queue.enqueue(node.right)
```

##### Morris Inorder Traversal (O(1) space)
```
MorrisInorder(root):
    curr ← root
    while curr ≠ NIL:
        if curr.left = NIL:
            Visit(curr)
            curr ← curr.right
        else:
            pred ← curr.left
            while pred.right ≠ NIL and pred.right ≠ curr:
                pred ← pred.right
            if pred.right = NIL:
                pred.right ← curr       // create thread
                curr ← curr.left
            else:
                pred.right ← NIL        // remove thread
                Visit(curr)
                curr ← curr.right
```

---

### 7.2 Binary Search Tree (BST)

- Left child < Parent < Right child (for all nodes)
- Inorder traversal gives sorted sequence

**Operations:**

| Operation | Average | Worst (skewed) |
|-----------|:---:|:---:|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Min / Max | O(log n) | O(n) |

**Deletion Cases:**
1. Leaf node — simply remove
2. One child — replace with child
3. Two children — replace with inorder successor (or predecessor)

#### Pseudocode — BST Operations

```mermaid
flowchart TD
    subgraph Del1["BST Delete Case 1: Leaf Node (delete 1)"]
        A1["Before:    10<br/>&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;\&nbsp;&nbsp;<br/>&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;15<br/>&nbsp;/&nbsp;\<br/>1&nbsp;&nbsp;7"] --> A2["Remove 1<br/>    10<br/>&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;\&nbsp;&nbsp;<br/>&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;15<br/>&nbsp;/&nbsp;\<br/>nil&nbsp;7"]
    end
    subgraph Del2["Case 2: One Child (delete 5)"]
        B1["    10<br/>&nbsp;&nbsp;/&nbsp;&nbsp;\<br/>&nbsp;5&nbsp;&nbsp;15<br/>&nbsp;/&nbsp;\<br/>1&nbsp;nil"] --> B2["Replace 5 with 1<br/>    10<br/>&nbsp;&nbsp;/&nbsp;&nbsp;\<br/>&nbsp;1&nbsp;&nbsp;15"]
    end
    subgraph Del3["Case 3: Two Children (delete 10)"]
        C1["    10<br/>&nbsp;&nbsp;/&nbsp;&nbsp;\<br/>&nbsp;5&nbsp;&nbsp;15<br/>&nbsp;/&nbsp;\&nbsp;&nbsp;&nbsp;/&nbsp;\<br/>1&nbsp;7&nbsp;12&nbsp;20"] --> C2["Find inorder successor: 12"]
        C2 --> C3["Replace 10 with 12<br/>    12<br/>&nbsp;&nbsp;/&nbsp;&nbsp;\<br/>&nbsp;5&nbsp;&nbsp;15<br/>&nbsp;/&nbsp;\&nbsp;&nbsp;&nbsp;/&nbsp;\<br/>1&nbsp;7&nbsp;nil&nbsp;20"]
    end
```

##### Search
```
BSTSearch(root, key):
    if root = NIL or root.key = key:
        return root
    if key < root.key:
        return BSTSearch(root.left, key)
    else:
        return BSTSearch(root.right, key)
```

##### Insert
```
BSTInsert(root, key):
    if root = NIL:
        return new Node with key
    if key < root.key:
        root.left ← BSTInsert(root.left, key)
    else if key > root.key:
        root.right ← BSTInsert(root.right, key)
    return root
```

##### Delete
```
BSTDelete(root, key):
    if root = NIL:
        return NIL
    if key < root.key:
        root.left ← BSTDelete(root.left, key)
    else if key > root.key:
        root.right ← BSTDelete(root.right, key)
    else:
        // Case 1 & 2: 0 or 1 child
        if root.left = NIL:
            return root.right
        if root.right = NIL:
            return root.left
        // Case 3: 2 children
        succ ← FindMin(root.right)
        root.key ← succ.key
        root.right ← BSTDelete(root.right, succ.key)
    return root

FindMin(root):
    while root.left ≠ NIL:
        root ← root.left
    return root
```

##### Validate BST
```
IsValidBST(root, min ← -∞, max ← +∞):
    if root = NIL: return true
    if root.key ≤ min or root.key ≥ max:
        return false
    return IsValidBST(root.left, min, root.key)
       and IsValidBST(root.right, root.key, max)
```

##### Kth Smallest in BST
```
KthSmallest(root, k):
    // Returns (node, k-left) pair or found value
    stack ← empty
    curr ← root
    while curr ≠ NIL or stack is not empty:
        while curr ≠ NIL:
            stack.push(curr)
            curr ← curr.left
        curr ← stack.pop()
        k ← k - 1
        if k = 0: return curr.key
        curr ← curr.right
    return NIL
```

---

### 7.3 Self-Balancing BSTs

> [!tip]
> Performance guaranteed: O(log n) for all operations.

```mermaid
flowchart TD
    subgraph LL["LL Imbalance → Right Rotate"]
        LA1["Before:<br/>&nbsp;&nbsp;10<br/>&nbsp;/&nbsp;&nbsp;\<br/>5&nbsp;&nbsp;T2<br/>/<br/>2"] --> LA2["After rotate right at 10:<br/>&nbsp;&nbsp;5<br/>&nbsp;/&nbsp;&nbsp;\<br/>2&nbsp;&nbsp;10<br/>&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;\<br/>&nbsp;&nbsp;T1&nbsp;T2"]
    end
    subgraph RR["RR Imbalance → Left Rotate"]
        RA1["Before:<br/>10<br/>&nbsp;\<br/>&nbsp;&nbsp;15<br/>&nbsp;&nbsp;&nbsp;\<br/>&nbsp;&nbsp;&nbsp;&nbsp;20"] --> RA2["After rotate left at 10:<br/>&nbsp;15<br/>&nbsp;/&nbsp;\<br/>10&nbsp;20"]
    end
    subgraph LR["LR Imbalance → Left Rotate Child → Right Rotate Parent"]
        LR1["Before:<br/>&nbsp;10<br/>&nbsp;/&nbsp;&nbsp;\<br/>5&nbsp;&nbsp;T3<br/>&nbsp;\<br/>&nbsp;&nbsp;7"] --> LR2["Step1: left rotate at 5<br/>&nbsp;10<br/>&nbsp;/&nbsp;\<br/>7&nbsp;T3<br/>/<br/>5"]
        LR2 --> LR3["Step2: right rotate at 10<br/>&nbsp;&nbsp;7<br/>&nbsp;/&nbsp;\<br/>5&nbsp;10"]
    end
    subgraph RL["RL Imbalance → Right Rotate Child → Left Rotate Parent"]
        RL1["Before:<br/>10<br/>&nbsp;\<br/>&nbsp;15<br/>&nbsp;/<br/>12"] --> RL2["Step1: right rotate at 15<br/>10<br/>&nbsp;\<br/>12<br/>&nbsp;\<br/>&nbsp;15"]
        RL2 --> RL3["Step2: left rotate at 10<br/>&nbsp;12<br/>&nbsp;/&nbsp;\<br/>10&nbsp;15"]
    end
```


#### AVL Tree
- Balance factor = height(left) - height(right) ∈ {-1, 0, 1}
- Rotations: Left, Right, Left-Right, Right-Left
- Strictly balanced — faster lookups than Red-Black Tree
- All operations O(log n)

##### AVL Rotations (Pseudocode)
```
Height(node):
    if node = NIL: return 0
    return node.height

BalanceFactor(node):
    if node = NIL: return 0
    return Height(node.left) - Height(node.right)

UpdateHeight(node):
    node.height ← 1 + max(Height(node.left), Height(node.right))

RotateRight(y):
    x ← y.left
    T2 ← x.right
    x.right ← y
    y.left ← T2
    UpdateHeight(y)
    UpdateHeight(x)
    return x                  // new root of subtree

RotateLeft(x):
    y ← x.right
    T2 ← y.left
    y.left ← x
    x.right ← T2
    UpdateHeight(x)
    UpdateHeight(y)
    return y                  // new root of subtree

AVLInsert(root, key):
    // Standard BST insert first
    if root = NIL:
        return new Node with key and height ← 1
    if key < root.key:
        root.left ← AVLInsert(root.left, key)
    else if key > root.key:
        root.right ← AVLInsert(root.right, key)
    else:
        return root            // duplicates not allowed

    UpdateHeight(root)
    balance ← BalanceFactor(root)

    // Left Heavy
    if balance > 1:
        if key < root.left.key:
            return RotateRight(root)           // Left-Left case
        else:
            root.left ← RotateLeft(root.left)  // Left-Right case
            return RotateRight(root)

    // Right Heavy
    if balance < -1:
        if key > root.right.key:
            return RotateLeft(root)            // Right-Right case
        else:
            root.right ← RotateRight(root.right) // Right-Left case
            return RotateLeft(root)

    return root
```

#### Red-Black Tree
- Each node is red or black
- Root and leaves (NIL) are black
- Red node's children must be black
- Every path from root to leaf has the same number of black nodes
- Less strictly balanced than AVL — fewer rotations on insert/delete
- Used in: Java `TreeMap`, C++ `std::map`, Linux kernel

#### Splay Tree
- Self-adjusting; recently accessed elements move to root
- Amortized O(log n) operations
- Good for caches with temporal locality

#### B-Tree / B+ Tree
- Generalized BST; each node can have multiple keys and children
- Used in databases and file systems
- B+ Tree: all data in leaves, leaves linked for range queries
- Minimizes disk I/O

---

### 7.4 N-ary Tree

- Each node can have up to N children
- Traversals similar to binary tree but iterate over all children

---

### 7.5 Lowest Common Ancestor (LCA)

| Method | Preprocessing | Query |
|--------|:---:|:---:|
| Naive (path comparison) | O(1) | O(n) |
| Binary Lifting | O(n log n) | O(log n) |
| Euler Tour + Sparse Table | O(n log n) | O(1) |
| Tarjan's Offline LCA | O(n + q) | O(1) amortized |

#### Pseudocode — LCA

##### Binary Lifting (Preprocessing + Query)
```
// Preprocessing
BinaryLifting(root):
    n ← number of nodes
    LOG ← floor(log2(n)) + 1
    up[1 .. n][0 .. LOG] ← NIL
    depth[1 .. n] ← 0
    DFS-LCA(root, NIL)

DFS-LCA(node, parent):
    up[node][0] ← parent
    for j ← 1 to LOG:
        if up[node][j - 1] ≠ NIL:
            up[node][j] ← up[ up[node][j - 1] ][j - 1]
    for each child of node:
        if child ≠ parent:
            depth[child] ← depth[node] + 1
            DFS-LCA(child, node)

// Query
LCA(u, v):
    if depth[u] < depth[v]: swap u, v
    // lift u to same depth as v
    diff ← depth[u] - depth[v]
    for j ← 0 to LOG:
        if diff has bit j set:
            u ← up[u][j]
    if u = v: return u
    // lift both together
    for j ← LOG downto 0:
        if up[u][j] ≠ up[v][j]:
            u ← up[u][j]
            v ← up[v][j]
    return up[u][0]
```

#### Practical usage patterns (CP)

- Subtree queries: Euler tour flattening → `[tin[v], tout[v]]` interval → Fenwick/Segment Tree
- Path queries (u↔v): HLD → split path into O(log n) chains → segment tree over base array
- Kth ancestor: binary lifting powers of two

> [!tip] Bridges
> - `[[#12. Segment Trees]]`, `[[#13. Binary Indexed Trees (Fenwick Trees)]]` for range structures

#### Pseudocode — Common Tree Operations

##### Diameter of Binary Tree
```
Diameter(root):
    if root = NIL: return 0
    leftHeight ← Height(root.left)
    rightHeight ← Height(root.right)
    leftDiam ← Diameter(root.left)
    rightDiam ← Diameter(root.right)
    return max(leftHeight + rightHeight, max(leftDiam, rightDiam))

// Optimised: compute height and diameter together
DiameterOptimised(root):
    // returns (diameter, height)
    if root = NIL: return (0, 0)
    (leftD, leftH) ← DiameterOptimised(root.left)
    (rightD, rightH) ← DiameterOptimised(root.right)
    h ← 1 + max(leftH, rightH)
    d ← max(leftH + rightH, max(leftD, rightD))
    return (d, h)
```

##### Serialize and Deserialize
```
Serialize(root):
    if root = NIL: return "NIL,"
    return str(root.key) + "," + Serialize(root.left) + Serialize(root.right)

Deserialize(data):
    // Use a queue of tokens split by comma
    return DeserializeHelper(tokenQueue)

DeserializeHelper(queue):
    token ← queue.dequeue()
    if token = "NIL": return NIL
    node ← new Node with key ← token
    node.left ← DeserializeHelper(queue)
    node.right ← DeserializeHelper(queue)
    return node
```

##### Construct Tree from Inorder + Preorder
```
BuildTree(preorder, inorder):
    // preorder[1 .. n], inorder[1 .. n]
    // Preorder[1] is always root
    // HashMap maps inorder values to indices for O(1) lookup
    inorderMap ← map each value → index
    return BuildHelper(preorder, 1, n, inorder, 1, n, inorderMap)

BuildHelper(pre, preStart, preEnd, in, inStart, inEnd, map):
    if preStart > preEnd: return NIL
    rootVal ← pre[preStart]
    root ← new Node with key ← rootVal
    rootIndex ← map[rootVal]
    leftSize ← rootIndex - inStart
    root.left ← BuildHelper(pre, preStart + 1, preStart + leftSize,
                             in, inStart, rootIndex - 1, map)
    root.right ← BuildHelper(pre, preStart + leftSize + 1, preEnd,
                              in, rootIndex + 1, inEnd, map)
    return root
```

### 7.6 Euler Tour (Tree Flattening)

- Goal: map each subtree of v to a contiguous range [tin[v], tout[v]] in an array.
- Use DFS to assign entry time `tin[v]` and exit time `tout[v]` while writing v into an order array at `tin[v]`.

```
timer ← 0
DFS(v, p):
    tin[v] ← timer; order[timer] ← v; timer ← timer + 1
    for u in g[v]:
        if u ≠ p: DFS(u, v)
    tout[v] ← timer - 1
```

- Subtree sum/update → range query/update on `[tin[v], tout[v]]` using Fenwick/Segment Tree.

> [!tip] Bridges
> - Use `[[#13. Binary Indexed Trees (Fenwick Trees)]]` or `[[#12. Segment Trees]]` over the Euler-order base array.
> - Java templates: ![[JAVA_IMPL/Java_05_Utilities_Templates#Fast I/O (Competitive Programming)]]

> [!warning] Pitfalls
> - Off-by-one in `tout[v]` definition; decide inclusive vs exclusive and be consistent.
> - Mixing 0/1-based indices between DS and Euler arrays.

---

### 7.7 Heavy-Light Decomposition (HLD)

- Decomposes a tree into O(log n) chains so any path u↔v splits into O(log n) segments on chains.
- Maintain arrays: `parent[]`, `depth[]`, `heavy[]` (child with largest subtree), `head[]` (chain head), `pos[]` (index in base array).
- Build a segment tree over the base array indexed by `pos[v]`.

```
// 1) DFS sizes to choose heavy child
dfs(v, p):
    parent[v] ← p; size ← 1; best ← 0
    for u in g[v], u ≠ p:
        depth[u] ← depth[v] + 1
        usz ← dfs(u, v)
        if usz > best: best ← usz; heavy[v] ← u
        size ← size + usz
    return size

// 2) Decompose into chains
decompose(v, h):
    head[v] ← h; pos[v] ← cur++
    if heavy[v] ≠ -1:
        decompose(heavy[v], h)
        for u in g[v], u ≠ parent[v] and u ≠ heavy[v]:
            decompose(u, u)

// 3) Path query
queryPath(u, v):
    res ← NEUTRAL
    while head[u] ≠ head[v]:
        if depth[ head[u] ] < depth[ head[v] ]: swap u, v
        res ← combine(res, seg.query(pos[ head[u] ], pos[u]))
        u ← parent[ head[u] ]
    // now same head
    if depth[u] > depth[v]: swap u, v
    res ← combine(res, seg.query(pos[u] + EDGE_OR_NODE_OFFSET, pos[v]))
    return res
```

```mermaid
flowchart TD
  subgraph Tree
    A((A)) --heavy--> B((B)) --heavy--> E((E))
    B --light--> C((C))
    C --heavy--> F((F))
  end
  subgraph Chains
    H1[Chain 1: A→B→E]
    H2[Chain 2: C→F]
  end
  A -.maps to.-> H1
  B -.maps to.-> H1
  E -.maps to.-> H1
  C -.maps to.-> H2
  F -.maps to.-> H2
```

> [!tip] Java templates
> - ![[JAVA_IMPL/Java_05_Utilities_Templates#HLD Skeleton]]
> - ![[JAVA_IMPL/Java_05_Utilities_Templates#LCA (Binary Lifting) Template]]

> [!warning] Pitfalls
> - Edge vs node values: adjust inclusive ranges with an offset (store edge value at child’s position).
> - Forgetting to handle the final same-chain segment in `queryPath`.
> - Not resetting `heavy[] = -1` before DFS when reusing arrays.

### Common Tree Patterns

- Maximum depth / minimum depth
- Diameter of binary tree
- Check if balanced
- Symmetric tree / mirror tree
- Path sum problems
- Serialize and deserialize binary tree
- Construct tree from traversals (inorder + preorder/postorder)
- Validate BST
- Kth smallest element in BST
- Flatten binary tree to linked list
- Binary tree right side view
- Vertical order traversal
- Boundary traversal

> [!warning] Pitfalls
> - **BST validation without tracking min/max range** — checking only `left.val < root.val < right.val` is insufficient. A node deep in the right subtree could violate the global BST property (e.g., 10 → right→5 → left→15). Pass `min` and `max` bounds down the recursion.
> - **Forgetting to handle null in recursive tree functions** — most tree operations start with `if (root == null) return`. Without this, every recursive call eventually NullPointerExceptions.
> - **Tree height vs depth confusion** — depth = distance from root (root has depth 0). Height = longest path to a leaf (leaf has height 0 or 1 depending on convention). Mixing them up breaks balanced-tree checks.
> - **Recursive tree serialization stack overflow** — deep skewed trees (10^5 nodes) overflow the call stack. Use iterative traversal (stack-based) for serialization and deserialization.
> - **In-place tree modification without proper parent tracking** — BST deletion requires tracking or updating the parent pointer. Without it, you can't unlink the deleted node. Using a dummy or returning the new root from recursion solves this.

> [!question]- Q: When is a tree balanced and why does it matter?
> **Answer:** A balanced tree has height O(log n). Unbalanced (skewed) trees degenerate to linked lists (height = n). BST operations (search, insert, delete) are O(height), so balanced = O(log n) vs unbalanced = O(n). Self-balancing trees (AVL, Red-Black) enforce balance automatically.

> [!question]- Q: What is the difference between BFS and DFS in trees?
> **Answer:** **BFS** (level-order): processes level by level, uses a queue. Good for shortest path in unweighted trees, level-order printing, connected components. **DFS** (pre/in/post-order): goes deep first, uses recursion or stack. Good for serialization, expression trees, topological ordering on DAGs.

> [!question]- Q: How does LCA (Lowest Common Ancestor) work?
> **Answer:** For a binary tree: recursively search left and right. If both return non-null, current node is LCA. If only one returns non-null, that's the LCA (both nodes in that subtree). O(n). For BST: exploit BST property — if both nodes are less than root, go left; both greater, go right; otherwise root is LCA. O(log n).

> [!question]- Q: What's the difference between AVL and Red-Black trees?
> **Answer:** **AVL**: stricter balance (height difference ≤ 1). Faster lookups (more balanced), but more rotations on insert/delete. **Red-Black**: looser balance (longest path ≤ 2× shortest). Fewer rotations, faster insert/delete. Java's TreeMap uses Red-Black; databases often prefer AVL or B-Trees.

### Resources

- [Tree Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/binary-tree-data-structure/)
- [Binary Trees - mycodeschool (YouTube)](https://www.youtube.com/playlist?list=PL2_aWCzGMAwI3W_JlcBbtYTwiQSsOTa6P)
- [Self-balancing BSTs - Abdul Bari (YouTube)](https://www.youtube.com/watch?v=jDM6_TnYIqE)
- *CLRS* — Chapters 12-14, 18

---

## 8. Heaps / Priority Queues

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_01_Fundamental_DS#Section D: Heaps]]

### Overview

```mermaid
flowchart TD
    subgraph MinHeap["Min-Heap (tree + array)"]
        H1["1"] --> H2["3"] & H3["5"]
        H2 --> H4["7"] & H5["9"]
        H3 --> H6["10"] & H7["12"]
    end
    subgraph Push["push(2)"]
        P1["Add at end → [1,3,5,7,9,10,12,2]"] --> P2["bubble-up:2<7→swap\n[1,3,5,2,9,10,12,7]"]
        P2 --> P3["bubble-up:2<3→swap\n[1,2,5,3,9,10,12,7]→ stop"]
    end
    subgraph Pop["pop() → remove min"]
        D1["Replace root with last\n[12,3,5,7,9,10]"] --> D2["bubble-down:12>3→swap\n[3,12,5,7,9,10]"]
        D2 --> D3["bubble-down:12>7→swap\n[3,7,5,12,9,10]→stop"]
    end
```

A heap is a complete binary tree satisfying the heap property:
- **Max-Heap**: parent ≥ children
- **Min-Heap**: parent ≤ children

Typically implemented as an array.

### Array Representation

For node at index `i` (0-indexed):
- Parent: `(i - 1) / 2`
- Left child: `2i + 1`
- Right child: `2i + 2`

### Operations

| Operation | Complexity |
|-----------|:---:|
| Insert (push) | O(log n) |
| Extract min/max (pop) | O(log n) |
| Peek (get min/max) | O(1) |
| Build heap from array | O(n) |
| Heapify (sift down) | O(log n) |
| Delete arbitrary | O(log n) |
| Update key | O(log n) |

### Types

| Type | Description |
|------|-------------|
| **Binary Heap** | Standard heap; complete binary tree |
| **d-ary Heap** | Each node has d children; shallower tree |
| **Fibonacci Heap** | Amortized O(1) insert, decrease-key; used in Dijkstra's |
| **Binomial Heap** | Collection of binomial trees; efficient merge |
| **Pairing Heap** | Simpler alternative to Fibonacci heap |
| **Min-Max Heap** | Alternating min and max levels |
| **Indexed Priority Queue** | Supports update/delete by key |

### Language Implementations

| Language | Min-Heap | Max-Heap |
|----------|----------|----------|
| Java | `PriorityQueue<>` | `PriorityQueue<>(Collections.reverseOrder())` |
| Python | `heapq` (min-heap) | Negate values for max |
| C++ | `priority_queue<>` (max by default) | `priority_queue<int, vector<int>, greater<int>>` for min |

### Common Patterns

- Kth largest/smallest element
- Merge K sorted lists/arrays
- Top K frequent elements
- Find median from data stream (two heaps)
- Task scheduler
- Reorganize string
- Sliding window median
- Heap sort
- Dijkstra's shortest path (min-heap)
- Prim's MST (min-heap)
- Huffman coding

### Pseudocode

#### Min-Heap Insert (Sift Up)
```
MinHeapInsert(A[1 .. n], x):
    n ← n + 1
    A[n] ← x
    i ← n
    while i > 1 and A[Parent(i)] > A[i]:
        swap A[i] and A[Parent(i)]
        i ← Parent(i)

Parent(i): return ⌊i / 2⌋
```

#### Min-Heap Extract-Min (Sift Down)
```
MinHeapExtractMin(A[1 .. n]):
    if n < 1: error "underflow"
    min ← A[1]
    A[1] ← A[n]
    n ← n - 1
    MinHeapify(A, 1)
    return min

MinHeapify(A[1 .. n], i):
    smallest ← i
    left ← Left(i)
    right ← Right(i)
    if left ≤ n and A[left] < A[smallest]:
        smallest ← left
    if right ≤ n and A[right] < A[smallest]:
        smallest ← right
    if smallest ≠ i:
        swap A[i] and A[smallest]
        MinHeapify(A, smallest)

Left(i):  return 2i
Right(i): return 2i + 1
```

#### Build Heap in O(n)
```
BuildMinHeap(A[1 .. n]):
    for i ← ⌊n / 2⌋ downto 1:
        MinHeapify(A, i)
```

#### Heap Sort
```
HeapSort(A[1 .. n]):
    // Build max-heap
    for i ← ⌊n / 2⌋ downto 1:
        MaxHeapify(A, n, i)
    // Extract elements
    for i ← n downto 2:
        swap A[1] and A[i]
        MaxHeapify(A, i - 1, 1)
```

#### Find Median from Data Stream (Two Heaps)
```
MedianFinder:
    maxHeap ← Max-Heap for lower half       // smaller half
    minHeap ← Min-Heap for upper half       // larger half

AddNum(x):
    if maxHeap is empty or x ≤ maxHeap.top():
        maxHeap.push(x)
    else:
        minHeap.push(x)
    // Balance: maxHeap may be ≤ 1 larger than minHeap
    if maxHeap.size > minHeap.size + 1:
        minHeap.push(maxHeap.pop())
    else if minHeap.size > maxHeap.size:
        maxHeap.push(minHeap.pop())

FindMedian():
    if maxHeap.size > minHeap.size:
        return maxHeap.top()
    return (maxHeap.top() + minHeap.top()) / 2
```

> [!warning] Pitfalls
> - **Using max-heap where min-heap is needed** — Java's `PriorityQueue` is a min-heap by default (smallest element at top). Use `new PriorityQueue<>(Collections.reverseOrder())` for max-heap. Python's `heapq` is always min-heap; negate values for max-heap.
> - **Heapify in O(n) vs building by repeated insert** — inserting n elements one-by-one is O(n log n). Heapify (bottom-up siftDown starting from n/2) is O(n). Use heapify when you have all elements upfront.
> - **0-indexed vs 1-indexed array representation** — in 0-indexed, children of i are at `2i+1` and `2i+2`, parent is `(i-1)/2`. In 1-indexed, children at `2i` and `2i+1`, parent at `i/2`. Off-by-one errors are common.
> - **Heap sort instability** — heap sort is not stable (equal elements may be reordered). For stable sorting, use merge sort or TimSort.
> - **Find median with two heaps** — the invariant: maxHeap size = minHeap size OR maxHeap size = minHeap size + 1. After every insertion, rebalance. Forgetting to rebalance gives incorrect medians.

> [!question]- Q: How do you find the Kth largest element using a heap?
> **Answer:** **Min-heap of size K**: iterate through the array, add each element to a min-heap. If heap size > K, pop the smallest. After processing, the top of the min-heap is the Kth largest. O(n log k) time, O(k) space. Alternatively, QuickSelect in O(n) average.

> [!question]- Q: What is heapify and why is it O(n)?
> **Answer:** Heapify builds a heap from an unsorted array by calling siftDown on all non-leaf nodes (indices n/2 down to 1). The cost at each level: O(1) for leaves (height 0), O(h) for height h. Summing: Σ(h * n/2^{h+1}) = O(n). Intuition: most nodes are near the bottom and cost very little.

> [!question]- Q: How do you merge K sorted lists using a heap?
> **Answer:** Push the head of each list into a min-heap with (value, listIndex, elementIndex). Repeatedly pop the minimum, add it to the result, and push the next element from the same list. O(N log K) where N = total elements, K = number of lists.

> [!question]- Q: What's the difference between a heap and a sorted array?
> **Answer:** A heap guarantees the root is the min/max, but the rest is not sorted — it's a partial order. Finding the minimum is O(1); finding the kth smallest (without popping) is not supported. A sorted array supports both min and kth smallest in O(1), but insertion is O(n) vs O(log n) for heap.

### Resources

- [Heap Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/heap-data-structure/)
- [Heaps - Abdul Bari (YouTube)](https://www.youtube.com/watch?v=HqPJF2L5h9U)
- *CLRS* — Chapter 6

---

## 9. Graphs

> [!summary] Pick a representation
> - Sparse graph: adjacency list.
> - Dense graph: adjacency matrix.
> - Weighted: store `(to, weight)` pairs.

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_02_Advanced_DS#Section G: Graph Representations]]

> [!tip] Intuition
> A graph represents **relationships**: cities connected by roads, people connected by friendships, web pages linked by hyperlinks. The choice of representation — adjacency list vs matrix — depends on whether the graph is sparse (few edges) or dense (many edges). Think of an adjacency list as a "who knows whom" directory for each vertex; an adjacency matrix is a "yes/no" table for every possible pair.

```mermaid
flowchart TD
    subgraph AL["Adjacency List (Sparse)"]
        A1["0 → [1, 2]"] --- A2["1 → [0, 3]"]
        A2 --- A3["2 → [0, 3]"] --- A4["3 → [1, 2]"]
    end
    subgraph AM["Adjacency Matrix (Dense)"]
        M1["   0 1 2 3<br/>0: 0 1 1 0<br/>1: 1 0 0 1<br/>2: 1 0 0 1<br/>3: 0 1 1 0"]
    end
    subgraph Terms["Key Terms"]
        T1["Degree = # of edges from a vertex"]
        T2["Path = sequence of edges"]
        T3["Cycle = path starting and ending at same vertex"]
        T4["Connected = path exists between every pair"]
        T5["DAG = Directed Acyclic Graph (no directed cycles)"]
    end
```

### Overview

A graph G = (V, E) consists of vertices (nodes) and edges (connections between nodes).

### Types

| Type | Description |
|------|-------------|
| **Undirected** | Edges have no direction |
| **Directed (Digraph)** | Edges have direction |
| **Weighted** | Edges have associated weights/costs |
| **Unweighted** | All edges have equal weight |
| **Cyclic** | Contains at least one cycle |
| **Acyclic** | No cycles |
| **DAG** | Directed Acyclic Graph |
| **Connected** | Path exists between every pair of vertices |
| **Bipartite** | Vertices can be divided into two disjoint sets |
| **Complete** | Edge between every pair of vertices |
| **Sparse** | |E| << |V|^2 |
| **Dense** | |E| ≈ |V|^2 |

### Representations

| Representation | Space | Check Edge | Iterate Neighbors | Best For |
|----------------|:---:|:---:|:---:|----------|
| **Adjacency Matrix** | O(V^2) | O(1) | O(V) | Dense graphs |
| **Adjacency List** | O(V + E) | O(degree) | O(degree) | Sparse graphs |
| **Edge List** | O(E) | O(E) | O(E) | Kruskal's, simple storage |
| **Incidence Matrix** | O(V * E) | O(E) | O(E) | Rare, theoretical |

### Key Concepts

- **Degree** — number of edges incident to a vertex
  - In-degree / Out-degree (directed graphs)
- **Connected Components** — maximal connected subgraphs
- **Strongly Connected Components (SCC)** — every vertex reachable from every other (directed)
  - Algorithms: Kosaraju's, Tarjan's
- **Topological Sort** — linear ordering of vertices in a DAG
  - Kahn's algorithm (BFS-based), DFS-based
- **Bipartite Check** — BFS/DFS 2-coloring
- **Euler Path / Circuit** — traverse every edge exactly once
- **Hamiltonian Path / Cycle** — visit every vertex exactly once (NP-complete)

### Common Patterns

- BFS / DFS traversal
- Number of islands (connected components)
- Clone graph
- Course schedule (topological sort + cycle detection)
- Word ladder (BFS)
- Shortest path (BFS for unweighted, Dijkstra for weighted)
- Detect cycle (DFS with coloring, Union-Find)
- Network delay time
- Cheapest flights within K stops
- Critical connections (bridges — Tarjan's)
- Alien dictionary (topological sort)
- Graph coloring

### Pseudocode

#### Graph Representation (Adjacency List)
```
// Build adjacency list from edge list E[1 .. m]:
Adj[1 .. V] ← array of empty lists
for each edge (u, v) in E:
    Adj[u].append(v)
    if undirected: Adj[v].append(u)
```

#### BFS
```
BFS(G[1 .. V], source):
    for v ← 1 to V:
        color[v] ← WHITE, dist[v] ← ∞, parent[v] ← NIL
    color[source] ← GRAY, dist[source] ← 0
    queue ← empty, queue.enqueue(source)
    while queue is not empty:
        u ← queue.dequeue()
        for each v in Adj[u]:
            if color[v] = WHITE:
                color[v] ← GRAY
                dist[v] ← dist[u] + 1
                parent[v] ← u
                queue.enqueue(v)
        color[u] ← BLACK
```

#### DFS
```
DFS(G[1 .. V]):
    for v ← 1 to V:
        color[v] ← WHITE, parent[v] ← NIL
    time ← 0
    for v ← 1 to V:
        if color[v] = WHITE:
            DFS-Visit(v)

DFS-Visit(u):
    time ← time + 1
    disc[u] ← time
    color[u] ← GRAY
    for each v in Adj[u]:
        if color[v] = WHITE:
            parent[v] ← u
            DFS-Visit(v)
        else if color[v] = GRAY:
            // Back edge → cycle detected (directed graph)
    color[u] ← BLACK
    time ← time + 1
    fin[u] ← time
```

#### Cycle Detection — Directed (3-Color DFS)
```
HasCycleDirected(G):
    for v ← 1 to V: color[v] ← WHITE
    for v ← 1 to V:
        if color[v] = WHITE and CycleDFS(v):
            return true
    return false

CycleDFS(u):
    color[u] ← GRAY
    for each v in Adj[u]:
        if color[v] = GRAY: return true    // back edge
        if color[v] = WHITE and CycleDFS(v): return true
    color[u] ← BLACK
    return false
```

#### Cycle Detection — Undirected (Union-Find)
```
HasCycleUndirected(edges):
    for each vertex v: MakeSet(v)
    for each edge (u, v):
        if Find(u) = Find(v):
            return true                    // cycle found
        Union(u, v)
    return false
```

#### Topological Sort — Kahn's Algorithm (BFS)
```
TopologicalSort(G):
    inDegree[1 .. V] ← {0}
    for u ← 1 to V:
        for each v in Adj[u]:
            inDegree[v] ← inDegree[v] + 1
    queue ← empty
    for v ← 1 to V:
        if inDegree[v] = 0: queue.enqueue(v)
    result ← []
    while queue is not empty:
        u ← queue.dequeue()
        result.append(u)
        for each v in Adj[u]:
            inDegree[v] ← inDegree[v] - 1
            if inDegree[v] = 0:
                queue.enqueue(v)
    if |result| ≠ V: return "cycle exists"
    return result
```

#### Kosaraju's SCC
```
KosarajuSCC(G):
    // First DFS: compute finish order
    stack ← empty
    for v ← 1 to V: visited[v] ← false
    for v ← 1 to V:
        if not visited[v]:
            DFSPostorder(G, v, visited, stack)
    // Reverse graph
    GT ← ReverseEdges(G)
    // Second DFS: process in reverse finish order
    for v ← 1 to V: visited[v] ← false
    sccList ← []
    while stack is not empty:
        v ← stack.pop()
        if not visited[v]:
            component ← []
            DFSCollect(GT, v, visited, component)
            sccList.append(component)
    return sccList
```

#### Tarjan's Bridges (Critical Connections)
```
FindBridges(G):
    time ← 0
    disc[1 .. V] ← -1, low[1 .. V] ← -1
    bridges ← []
    for v ← 1 to V:
        if disc[v] = -1: BridgeDFS(v, NIL, G, disc, low, bridges, time)
    return bridges

BridgeDFS(u, parent, G, disc, low, bridges, time):
    time ← time + 1
    disc[u] ← time, low[u] ← time
    for each v in Adj[u]:
        if v = parent: continue
        if disc[v] ≠ -1:
            low[u] ← min(low[u], disc[v])    // back edge
        else:
            BridgeDFS(v, u, G, disc, low, bridges, time)
            low[u] ← min(low[u], low[v])
            if low[v] > disc[u]:
                bridges.append((u, v))        // bridge found
```

#### Bipartite Check (BFS 2-Coloring)
```
IsBipartite(G):
    color[1 .. V] ← -1  // uncolored
    for v ← 1 to V:
        if color[v] = -1:
            queue ← empty, queue.enqueue(v)
            color[v] ← 0
            while queue is not empty:
                u ← queue.dequeue()
                for each w in Adj[u]:
                    if color[w] = -1:
                        color[w] ← 1 - color[u]
                        queue.enqueue(w)
                    else if color[w] = color[u]:
                        return false         // not bipartite
    return true
```

### Resources

- [Graph Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/)
- [Graph Theory - William Fiset (YouTube Playlist)](https://www.youtube.com/playlist?list=PLDV1Zeh2NRsDGO4--qE8yH72HFL1Km93)
- *CLRS* — Chapters 22-26

---

## 10. Tries (Prefix Trees)

### Overview

> [!tip] Intuition
> When you type "app" in your phone's search bar and it suggests "apple," "application," and "appetizer," a trie is behind the scenes. Each node stores one character, and words are paths from root to a marked "end-of-word" node. Finding all words with a given prefix is O(prefix length) — you just walk down that path and collect all descendants. No hash table can match this prefix-search speed.

```mermaid
flowchart TD
    subgraph Trie["Trie containing 'app', 'apple', 'api', 'bat'"]
        T0["root"] --> T1["'a'"]
        T0 --> T2["'b'"]
        T1 --> T3["'p'"]
        T3 --> T4["'p' ★ (end: app)"]
        T4 --> T5["'l'"]
        T5 --> T6["'e' ★ (end: apple)"]
        T3 --> T7["'i' ★ (end: api)"]
        T2 --> T8["'a'"]
        T8 --> T9["'t' ★ (end: bat)"]
    end
    style T4 fill:#f9a,stroke:#a05
    style T6 fill:#f9a,stroke:#a05
    style T7 fill:#f9a,stroke:#a05
    style T9 fill:#f9a,stroke:#a05
```

A trie is a tree-like data structure used to store strings, where each node represents a character. Useful for prefix-based operations.

### Types

| Type | Description |
|------|-------------|
| **Standard Trie** | One child per character |
| **Compressed Trie (Radix Tree / Patricia Trie)** | Merge chains of single-child nodes |
| **Ternary Search Trie** | Three children: less, equal, greater |
| **Suffix Trie** | Trie of all suffixes of a string |

### Operations

| Operation | Complexity |
|-----------|:---:|
| Insert | O(L) where L = word length |
| Search | O(L) |
| Delete | O(L) |
| Prefix search | O(P + K) where P = prefix length, K = results |
| Autocomplete | O(P + K) |

### Space Complexity

- O(ALPHABET_SIZE * L * N) worst case (N words of length L)
- Compressed trie significantly reduces space

### Node Structure

```
class TrieNode:
    children: Map<char, TrieNode>   # or array of size 26 for lowercase
    isEndOfWord: boolean
    count: int                       # optional: word frequency
    prefixCount: int                 # optional: words with this prefix
```

### Common Patterns

- Implement Trie (insert, search, startsWith)
- Word Search II (Trie + DFS on board)
- Longest common prefix
- Autocomplete system
- Replace words (dictionary + trie)
- Maximum XOR of two numbers (bitwise trie)
- Palindrome pairs
- Word squares
- Stream of characters (suffix-based trie)

### Pseudocode

#### Trie — Insert, Search, StartsWith
```
TrieNode:
    children: map of char → TrieNode  (or array of size 26)
    isEnd: boolean

TrieInsert(root, word):
    node ← root
    for each ch in word:
        if node.children does not contain ch:
            node.children[ch] ← new TrieNode()
        node ← node.children[ch]
    node.isEnd ← true

TrieSearch(root, word):
    node ← root
    for each ch in word:
        if node.children does not contain ch:
            return false
        node ← node.children[ch]
    return node.isEnd

TrieStartsWith(root, prefix):
    node ← root
    for each ch in prefix:
        if node.children does not contain ch:
            return NIL
        node ← node.children[ch]
    return node                        // subtree for autocomplete
```

#### Trie — Delete
```
TrieDelete(root, word, depth ← 0):
    if root = NIL: return NIL
    if depth = |word|:
        root.isEnd ← false
        if root.children is empty:
            return NIL                  // delete node
        return root
    ch ← word[depth]
    root.children[ch] ← TrieDelete(root.children[ch], word, depth + 1)
    if root.children is empty and not root.isEnd:
        return NIL
    return root
```

#### Maximum XOR (Bitwise Trie)
```
MaxXOR(nums[1 .. n]):
    // Build bitwise trie (31 bits for 32-bit integers)
    root ← new TrieNode()
    for each num in nums:
        InsertBits(root, num)
    maxXor ← 0
    for each num in nums:
        xor ← FindMaxXorPart(root, num)
        maxXor ← max(maxXor, xor)
    return maxXor

InsertBits(root, x):
    node ← root
    for bit 31 downto 0:
        b ← (x >> bit) & 1
        if node.children[b] = NIL:
            node.children[b] ← new TrieNode()
        node ← node.children[b]

FindMaxXorPart(root, x):
    node ← root
    result ← 0
    for bit 31 downto 0:
        b ← (x >> bit) & 1
        toggle ← 1 - b
        if node.children[toggle] ≠ NIL:
            result ← result | (1 << bit)
            node ← node.children[toggle]
        else:
            node ← node.children[b]
    return result
```

> [!warning] Pitfalls
> - **Memory blowup with full alphabet arrays** — a naive trie with `children[26]` per node for the full lowercase alphabet wastes ~26 * 8 * N bytes for an N-node trie. Use `HashMap<Character, Node>` or compressed trie (Radix tree) for sparse alphabets.
> - **Forgetting to mark end-of-word** — without an `isEnd` flag, `search("app")` returns true for "apple" if "app" is a prefix but not a stored word. Always check `isEnd` in `search()`, not just in `startsWith()`.
> - **Case sensitivity** — a trie storing "Apple" won't match "apple" unless you normalize (e.g., lowercase all strings before insertion and search).
> - **Deleted nodes in compressed tries** — in a Radix/Patricia trie, deleting a word may require merging nodes or handling shared prefixes carefully. Standard tries just unset `isEnd`.
> - **Stack overflow in recursive trie operations** — deeply nested tries (e.g., storing URLs or long strings) can exceed recursion limits. Use iterative traversal for production implementations.

> [!question]- Q: What's the difference between a Trie and a Hash Set for storing strings?
> **Answer:** A Hash Set gives O(1) lookup for exact matches; a Trie gives O(L) lookup but also supports **prefix queries** (startsWith, autocomplete), longest prefix match, and lexicographic ordering of stored strings — none of which a Hash Set can do efficiently.

> [!question]- Q: How is a Trie used for autocomplete?
> **Answer:** After navigating to the node corresponding to the typed prefix, perform DFS/BFS from that node to collect all descendant nodes marked `isEnd`. Return those words. With frequency counts at nodes, you can also return the top-K most frequent completions.

> [!question]- Q: What's a compressed trie (Radix Tree)?
> **Answer:** Nodes with only one child are merged with their parent, storing substrings instead of single characters. For example, the path "app" → "le" becomes one node labeled "apple" if no branching occurs. This drastically reduces node count for sparse keys.

> [!question]- Q: How is a Trie used for Maximum XOR problems?
> **Answer:** Build a binary trie (each node has children 0 and 1). For each number, to find the maximum XOR with any previously inserted number, traverse the trie taking the opposite bit (1 if current bit is 0) at each level. O(32) per query.

### Resources

- [Trie Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/trie-insert-and-search/)
- [Tries - Tushar Roy (YouTube)](https://www.youtube.com/watch?v=AXjmTQ8LEoI)

---

## 11. Disjoint Set Union (Union-Find)

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_02_Advanced_DS#H.1 Union-Find (DSU)]]

### Overview

> [!tip] Intuition
> Imagine a social network where each person points to a "group leader." When two people become friends, their groups merge — the smaller group's leader now points to the larger group's leader. To find who leads a person, you follow the chain upward, compressing the path along the way so future lookups are instant. That's Union-Find: **disjoint sets, near-constant operations, no tree rotations, no rebalancing — just parent pointers and clever path compression.**

```mermaid
flowchart LR
    subgraph DSU_Init["Initial: each element is its own parent"]
        P1["0→0&nbsp;&nbsp;1→1&nbsp;&nbsp;2→2&nbsp;&nbsp;3→3&nbsp;&nbsp;4→4&nbsp;&nbsp;5→5&nbsp;&nbsp;6→6"]
    end
    subgraph DSU_Union["Union(1,2), Union(3,4), Union(5,6)"]
        U1["0→0&nbsp;&nbsp;1→1&nbsp;&nbsp;2→1&nbsp;&nbsp;3→3&nbsp;&nbsp;4→3&nbsp;&nbsp;5→5&nbsp;&nbsp;6→5"]
        U2["0→0&nbsp;&nbsp;1→1&nbsp;&nbsp;2→1&nbsp;&nbsp;3→3&nbsp;&nbsp;4→3&nbsp;&nbsp;5→5&nbsp;&nbsp;6→5<br/>Sets: {0}, {1,2}, {3,4}, {5,6}"]
    end
    subgraph DSU_Union2["Union(1,3) — union of two sets"]
        U3["Height of {1,2}=1, Height of {3,4}=1<br/>Attach 3's root to 1's root (arbitrary)"]
        U4["Result: 0→0&nbsp;&nbsp;3→1&nbsp;&nbsp;1→1&nbsp;&nbsp;2→1&nbsp;&nbsp;4→3<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5→5&nbsp;&nbsp;6→5"]
    end
    subgraph FindPC["Find(4) with Path Compression"]
        F1["Find(4): 4→3→1→1 → root=1"] --> F2["After: set 4→1 directly<br>parent: 4→1 (skip 3)"]
    end
// Initialisation
for i ← 1 to n:
    parent[i] ← i
    rank[i] ← 0

MakeSet(x):
    parent[x] ← x
    rank[x] ← 0

Find(x):
    if parent[x] ≠ x:
        parent[x] ← Find(parent[x])       // path compression
    return parent[x]

Union(x, y):
    rootX ← Find(x)
    rootY ← Find(y)
    if rootX = rootY: return
    if rank[rootX] < rank[rootY]:
        swap rootX and rootY
    parent[rootY] ← rootX
    if rank[rootX] = rank[rootY]:
        rank[rootX] ← rank[rootX] + 1

// Union by Size (alternative)
UnionBySize(x, y):
    rootX ← Find(x)
    rootY ← Find(y)
    if rootX = rootY: return
    if size[rootX] < size[rootY]:
        parent[rootX] ← rootY
        size[rootY] ← size[rootY] + size[rootX]
    else:
        parent[rootY] ← rootX
        size[rootX] ← size[rootX] + size[rootY]
```

### Common Patterns

- Number of connected components
- Detect cycle in undirected graph
- Kruskal's MST
- Redundant connection
- Accounts merge
- Longest consecutive sequence
- Number of islands (union-find approach)
- Satisfiability of equality equations
- Smallest string with swaps

> [!warning] Pitfalls
> - **Forgetting path compression** — without `parent[x] = Find(parent[x])`, the tree degenerates to a linked list, making Find O(n). Always compress in Find.
> - **Union without rank/size** — naive union (always attach rootY to rootX) can create deep trees. Always use union by rank or union by size to keep depth O(α(n)).
> - **Using Union-Find for directed graphs** — DSU only models undirected connectivity. For directed graphs, use DFS or Tarjan's SCC algorithm.
> - **Rank vs size confusion** — union by rank tracks tree depth; union by size tracks number of elements. Both give O(α(n)), but size is more intuitive for problems like "size of connected component."
> - **Not resetting DSU for multiple test cases** — in competitive programming, reinitialize parent and rank arrays for each test case. Reusing stale parents produces wrong results.

> [!question]- Q: Why is Union-Find effectively O(1) despite being O(α(n))?
> **Answer:** The inverse Ackermann function α(n) grows so slowly that α(n) ≤ 5 for any practical input size (n < 2^65536). In practice, Union-Find with path compression + union by rank is effectively constant time per operation.

> [!question]- Q: When should I use Union-Find vs DFS for connected components?
> **Answer:** Use **Union-Find** when you need to process edges dynamically (online queries, edges added over time). Use **DFS/BFS** for static graphs (all edges known upfront). Union-Find is also better when you only need connectivity queries (no traversal info).

> [!question]- Q: How does Kruskal's MST use Union-Find?
> **Answer:** Kruskal's processes edges by weight. For each edge (u, v), if Find(u) ≠ Find(v), they're in different components — add the edge and Union(u, v). If Find(u) = Find(v), adding this edge would create a cycle — skip it. Union-Find is the cycle-detection engine of Kruskal's.

> [!question]- Q: What's path compression and why does it matter?
> **Answer:** During Find(x), every node on the path from x to the root has its parent pointer reset directly to the root. This flattens the tree over time. Without it, the tree can become deep (O(n)). With both path compression and union by rank, amortized time is O(α(n)).

### Resources

- [Union-Find - GeeksforGeeks](https://www.geeksforgeeks.org/union-find/)
- [Union-Find - William Fiset (YouTube)](https://www.youtube.com/watch?v=ibjEGG7ylHk)
- *CLRS* — Chapter 21

---

## 12. Segment Trees

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_02_Advanced_DS#E.4 Segment Tree]]

### Overview

```mermaid
flowchart TD
    subgraph Build["Build from array [3,1,4,1,5]"]
        ROOT["[0-4]:14"] --> L1["[0-2]:8"] & R1["[3-4]:6"]
        L1 --> L2["[0-1]:4"] & L2R["[2]:4"]
        R1 --> R2["[3]:1"] & R2R["[4]:5"]
        L2 --> L3["[0]:3"] & L3R["[1]:1"]
    end
    subgraph Query["Range query [1-3]"]
        Q1["[0-4]:14 → partial"] --> Q2["[0-2]:8 → partial"]
        Q1 --> Q3["[3-4]:6 → partial"]
        Q2 --> Q4["[0-1]:4 → inside? NO→continue"]
        Q2 --> Q5["[2]:4 → inside ✓ → return 4"]
        Q3 --> Q6["[3]:1 → inside ✓ → return 1"]
        Q3 --> Q7["[4]:5 → outside → skip"]
        Q8["Result: 4 + 1 + 5 = 10 (sum of A[1]+A[2]+A[3])"]
    end

A segment tree is a binary tree used for storing intervals/segments. It allows querying and updating ranges in O(log n).

### Operations

| Operation | Complexity |
|-----------|:---:|
| Build | O(n) |
| Point update | O(log n) |
| Range query (sum, min, max, GCD, etc.) | O(log n) |
| Range update (lazy propagation) | O(log n) |

### Space Complexity

- O(4n) ≈ O(n) (array-based implementation uses ~4x the input size)

### Key Concepts

- **Lazy Propagation** — defer range updates; propagate only when needed; enables O(log n) range updates
- **Persistent Segment Tree** — maintain previous versions; immutable nodes; O(log n) per version
- **2D Segment Tree** — for 2D range queries
- **Merge Sort Tree** — segment tree where each node stores a sorted list

### Pseudocode

```
// 1-indexed: for node i, left ← 2i, right ← 2i + 1
// tree[1 .. 4n] stores segment values

Build(A[1 .. n], node, start, end):
    if start = end:
        tree[node] ← A[start]
    else:
        mid ← (start + end) / 2
        Build(A, 2*node, start, mid)
        Build(A, 2*node + 1, mid+1, end)
        tree[node] ← tree[2*node] + tree[2*node + 1]  // sum example
```

#### Point Update
```
PointUpdate(A, node, start, end, idx, val):
    if start = end:
        tree[node] ← val
    else:
        mid ← (start + end) / 2
        if idx ≤ mid:
            PointUpdate(A, 2*node, start, mid, idx, val)
        else:
            PointUpdate(A, 2*node + 1, mid+1, end, idx, val)
        tree[node] ← tree[2*node] + tree[2*node + 1]
```

#### Range Query (Sum)
```
RangeQuery(node, start, end, L, R):
    if R < start or end < L:       // no overlap
        return 0
    if L ≤ start and end ≤ R:      // complete overlap
        return tree[node]
    mid ← (start + end) / 2
    leftSum ← RangeQuery(2*node, start, mid, L, R)
    rightSum ← RangeQuery(2*node + 1, mid+1, end, L, R)
    return leftSum + rightSum
```

#### Range Update with Lazy Propagation
```
Lazy[1 .. 4n] ← {0}

RangeUpdate(node, start, end, L, R, val):
    if Lazy[node] ≠ 0:               // pending update
        tree[node] ← tree[node] + (end - start + 1) * Lazy[node]
        if start ≠ end:
            Lazy[2*node] ← Lazy[2*node] + Lazy[node]
            Lazy[2*node + 1] ← Lazy[2*node + 1] + Lazy[node]
        Lazy[node] ← 0

    if R < start or end < L:         // no overlap
        return
    if L ≤ start and end ≤ R:        // complete overlap
        tree[node] ← tree[node] + (end - start + 1) * val
        if start ≠ end:
            Lazy[2*node] ← Lazy[2*node] + val
            Lazy[2*node + 1] ← Lazy[2*node + 1] + val
        return

    mid ← (start + end) / 2
    RangeUpdate(2*node, start, mid, L, R, val)
    RangeUpdate(2*node + 1, mid+1, end, L, R, val)
    tree[node] ← tree[2*node] + tree[2*node + 1]
```

### Common Patterns

- Range sum query
- Range minimum/maximum query
- Count of elements in range
- Range update with lazy propagation
- Number of inversions
- Distinct values queries
- Interval scheduling

> [!warning] Pitfalls
> - **0-indexed vs 1-indexed children** — in 1-indexed segment tree, children of node i are at 2i and 2i+1. In 0-indexed, they're at 2i+1 and 2i+2. Consistent indexing is critical; the entire tree breaks with an off-by-one.
> - **Array size for segment tree** — worst-case size is 4*n (not 2*n). For power-of-2 n, 2*n is enough, but for arbitrary n, allocate 4*n to be safe. Using 2*n may cause index out of bounds.
> - **Lazy propagation without clearing** — after applying a lazy update, you must push the lazy value to children AND reset the parent's lazy to 0/identity. Forgetting the reset double-counts updates.
> - **Range update without propagation during query** — when querying a range, you must propagate lazy values downwards before accessing child nodes. Skipping propagation returns stale values.
> - **Merge function not associative** — segment tree operations (sum, min, max) must be associative. For non-associative operations (e.g., matrix multiplication on segments), verify that the order of combination is correct.

> [!question]- Q: When should I use a Segment Tree vs a Fenwick Tree?
> **Answer:** **Segment Tree**: supports any associative operation (sum, min, max, GCD, matrix mult), range updates with lazy propagation. More flexible, more code. **Fenwick Tree (BIT)**: supports only invertible operations (sum, XOR), simpler code, lower constant, less memory. For range sum with point updates, BIT is preferred.

> [!question]- Q: How does lazy propagation work?
> **Answer:** Instead of updating every leaf in a range update, store pending updates at internal nodes (lazy array). When a node is accessed later (by query or update), "push" the lazy value to its children and clear its own lazy. This defers work until it's actually needed, giving O(log n) range updates.

> [!question]- Q: Why does a segment tree need 4*n space?
> **Answer:** In the worst case, a segment tree built for an arbitrary n may need nodes at index 2^(ceil(log₂ n) + 1) - 1. For n not a power of 2, the last level can be sparse, requiring up to 4*n - 1 indices. Using 4*n guarantees no index overflow.

> [!question]- Q: What operations can a segment tree support?
> **Answer:** Any associative operation: sum, minimum, maximum, GCD, LCM, bitwise AND/OR/XOR, matrix multiplication, convolution. With lazy propagation: range addition, range assignment. Persistence variants support historical queries.

### Resources

- [Segment Tree - CP-Algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment Trees - Algorithms Live (YouTube)](https://www.youtube.com/watch?v=Tr-xEGoByFQ)

---

## 13. Binary Indexed Trees (Fenwick Trees)

> [!tip] Java implementation reference
> ![[JAVA_IMPL/Java_02_Advanced_DS#E.5 Fenwick Tree (BIT)]]

---

## Assets and Attribution

- `assets/binary-tree.png`: PNG preview of Wikimedia Commons file “Binary tree.svg” by Derrick Coetzee, released into the public domain. Source: https://commons.wikimedia.org/wiki/File:Binary_tree.svg

### Overview

```mermaid
flowchart LR
    subgraph BIT["Fenwick Tree for [2,1,1,3]"]
        B1["BIT[1] = A[1] = 2\n(1=1 in binary → covers index 1)"]
        B2["BIT[2] = A[1]+A[2] = 3\n(2=10→covers indices 1-2)"]
        B3["BIT[3] = A[3] = 1\n(3=11→covers index 3)"]
        B4["BIT[4] = A[1]+A[2]+A[3]+A[4] = 7\n(4=100→covers indices 1-4)"]
    end
    subgraph Query_BIT["Prefix sum query(3)"]
        QB1["sum=0, idx=3"] --> QB2["add BIT[3]=1, sum=1, idx=2 (3-1)"]
        QB2 --> QB3["add BIT[2]=3, sum=4, idx=0 (2-2)"]
        QB3 --> QB4["idx=0 → stop, sum=4 = A[1]+A[2]+A[3]"]
    end
    subgraph Update["Update(2, +5)"]
        UB1["idx=2 → BIT[2]+=5, idx=4 (2+2)"] --> UB2["idx=4 > N → stop"]
    end

A Fenwick Tree (BIT) is a data structure that efficiently supports prefix sum queries and point updates. Simpler and more cache-friendly than segment trees for these operations.

### Operations

| Operation | Complexity |
|-----------|:---:|
| Build | O(n) or O(n log n) |
| Point update | O(log n) |
| Prefix sum query | O(log n) |
| Range sum query | O(log n) |

### Space Complexity

- O(n)

### Pseudocode

#### Point Update and Prefix Query
```
// BIT[1 .. n] is 1-indexed
// LSO(x) = x & (-x)   returns the lowest set bit

PointUpdate(i, delta):
    while i ≤ n:
        BIT[i] ← BIT[i] + delta
        i ← i + LSO(i)

PrefixQuery(i):   // sum of A[1 .. i]
    sum ← 0
    while i > 0:
        sum ← sum + BIT[i]
        i ← i - LSO(i)
    return sum

RangeQuery(L, R):
    return PrefixQuery(R) - PrefixQuery(L - 1)
```

#### Build BIT in O(n)
```
BuildBIT(A[1 .. n]):
    for i ← 1 to n:
        BIT[i] ← BIT[i] + A[i]
        next ← i + LSO(i)
        if next ≤ n:
            BIT[next] ← BIT[next] + BIT[i]
```

#### Range Update + Point Query (Using Difference Array)
```
// Apply difference array via BIT
RangeUpdate(L, R, val):
    PointUpdate(L, val)
    PointUpdate(R + 1, -val)

GetValue(i):
    return PrefixQuery(i)
```

### Common Patterns

- **2D BIT** — for 2D prefix sums and updates
- **Range Update + Point Query** — using difference array technique with BIT
- **Range Update + Range Query** — using two BITs
- Count inversions
- Range sum queries with updates
- Count of smaller numbers after self
- Coordinate compression + BIT

> [!warning] Pitfalls
> - **1-indexed requirement** — BIT's internal array uses 1-based indexing (i += i & -i). Feeding it a 0-based index breaks the update loop. Always add 1 when converting from 0-based input indices.
> - **BIT vs Segment Tree for non-invertible operations** — BIT works for sum, XOR (invertible) but NOT for min/max/GCD (non-invertible). You can't "remove" an element's contribution from a min. For those, use a Segment Tree.
> - **Update function direction** — `update(i, delta)`: `while (i <= n) { tree[i] += delta; i += i & -i; }`. `query(i)`: `while (i > 0) { sum += tree[i]; i -= i & -i; }`. Getting these loops backwards (i-- instead of i-=lsb) corrupts results.
> - **Coordinate compression for large values** — BIT requires indices in [1, n]. If values range from -10^9 to 10^9, compress them to ranks 1..n first using sorting + binary search.
> - **Range update with BIT** — for range add + point query, use a difference array BIT: `update(L, val); update(R+1, -val)`. For range add + range query, use two BITs. The formulas are non-obvious; double-check the math.

> [!question]- Q: How does `i & -i` isolate the lowest set bit?
> **Answer:** In two's complement, -i flips all bits and adds 1: `i & -i = i & (~i + 1)`. For i=12 (1100₂), ~i+1=0100₂. 1100 & 0100 = 0100 = 4 (the lowest set bit). This LSB determines how many elements the BIT node covers.

> [!question]- Q: How does BIT achieve O(log n) for prefix sum queries?
> **Answer:** Each node i stores the sum of the range `[i - LSB(i) + 1, i]`. A prefix query sums at most log n nodes: repeatedly strip the LSB (i -= i & -i) until reaching 0. Each step skips a power-of-2-sized segment.

> [!question]- Q: What is coordinate compression and why is it needed with BIT?
> **Answer:** BIT requires array indices in [1, max_val]. If values are sparse (e.g., {1000, 5000, 9999}), a BIT of size 10000 wastes space. Compress: sort unique values, assign rank 1..n. Each original value is replaced by its rank. BIT size becomes O(n).

> [!question]- Q: How do you count inversions with a BIT?
> **Answer:** Process the array from right to left. For each element, query the BIT for the count of elements smaller than it (already seen from the right). Then update the BIT at that value's position. Total inversions = sum of queries. O(n log n) with coordinate compression.

### Resources

- [Fenwick Tree - CP-Algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick Trees - William Fiset (YouTube)](https://www.youtube.com/watch?v=RgITNht_f4Q)

---

## 14. Suffix Arrays and Suffix Trees

### Overview

> [!tip] Intuition
> Every suffix of "banana" is one of "banana," "anana," "nana," ..., "a." A **Suffix Array** sorts these alphabetically and stores their starting indices: [5(a), 3(ana), 1(anana), 0(banana), 4(na), 2(nana)]. Once sorted, you can **binary search** for any substring in O(m log n). A **Suffix Tree** compresses all suffixes into a compact trie — same power, more memory.

```mermaid
flowchart TD
    subgraph SA["Suffix Array for 'banana'"]
        SA0["Suffixes:<br/>0: banana<br/>1: anana<br/>2: nana<br/>3: ana<br/>4: na<br/>5: a"]
        SA0 --> SA1["Sorted alphabetically:<br/>5: a<br/>3: ana<br/>1: anana<br/>0: banana<br/>4: na<br/>2: nana"]
        SA1 --> SA2["Suffix Array SA = [5, 3, 1, 0, 4, 2]"]
    end
    subgraph ST["Suffix Tree for 'banana$'"]
        ST1["root → 'a' → '$' (suffix 5), 'na' → '$' (3), 'na$' (1)"]
        ST2["root → 'banana$' (0)"]
        ST3["root → 'na' → '$' (4), 'na$' (2)"]
    end
```

**Suffix Array**: A sorted array of all suffixes of a string, represented by their starting indices.

**Suffix Tree**: A compressed trie of all suffixes of a string.

### Complexity

| Structure | Build | Space | Pattern Search |
|-----------|:---:|:---:|:---:|
| Suffix Array | O(n log n) or O(n) | O(n) | O(m log n) |
| Suffix Array + LCP | O(n log n) | O(n) | O(m + log n) |
| Suffix Tree (Ukkonen's) | O(n) | O(n) but large constant | O(m) |

### Key Concepts

- **LCP Array** — Longest Common Prefix between consecutive suffixes in sorted order
- **Kasai's Algorithm** — build LCP array from suffix array in O(n)
- **SA-IS Algorithm** — build suffix array in O(n)

### Applications

- Pattern matching in text
- Longest repeated substring
- Longest common substring of two strings
- Number of distinct substrings
- Burrows-Wheeler Transform (used in bzip2)

### Pseudocode

#### Suffix Array — Prefix Doubling Build (O(n log n))
```
BuildSuffixArray(S[1 .. n]):
    // rank[i] = rank of i-th suffix, tmpRank[1 .. n] = temporary ranks
    sa[1 .. n] ← [1, 2, ..., n]
    // Initial sort by first character
    Sort sa by S[sa[i]]
    for i ← 1 to n:
        rank[sa[i]] ← rank[sa[i - 1]] + (S[sa[i]] ≠ S[sa[i - 1]])

    k ← 1
    while k < n:
        // Sort by (rank[i], rank[i + k])
        Sort sa using comparator:
            if rank[i] ≠ rank[j]: return rank[i] < rank[j]
            ri ← rank[i + k] if i + k ≤ n else -1
            rj ← rank[j + k] if j + k ≤ n else -1
            return ri < rj
        tmpRank[sa[1]] ← 1
        for i ← 2 to n:
            prev ← sa[i - 1], curr ← sa[i]
            tmpRank[curr] ← tmpRank[prev] + (rank[curr] ≠ rank[prev]
                         or rank[curr + k] ≠ rank[prev + k])
        copy tmpRank to rank
        k ← k * 2
    return sa
```

#### Kasai's LCP Array (O(n))
```
BuildLCP(S[1 .. n], sa[1 .. n]):
    // rank[i] = position of suffix i in sa
    rank[1 .. n] ← 0
    for i ← 1 to n: rank[sa[i]] ← i
    lcp[1 .. n] ← 0
    h ← 0
    for i ← 1 to n:
        if rank[i] > 1:
            j ← sa[rank[i] - 1]
            while S[i + h] = S[j + h]:
                h ← h + 1
            lcp[rank[i]] ← h
            if h > 0: h ← h - 1
    return lcp
```

#### Pattern Search using Suffix Array
```
FindPattern(S, sa[1 .. n], P[1 .. m]):
    // Lower bound: first start position where SA suffix ≥ P
    lo ← 1, hi ← n
    while lo < hi:
        mid ← (lo + hi) / 2
        if S[sa[mid] .. n] ≥ P: hi ← mid
        else: lo ← mid + 1
    // Upper bound: first start position where SA suffix > P
    if S[sa[lo] .. n] < P: return []   // not found
    left ← lo
    hi ← n
    while lo < hi:
        mid ← (lo + hi + 1) / 2
        if S[sa[mid] .. n] > P: hi ← mid - 1
        else: lo ← mid
    right ← lo
    return sa[left .. right]
```

> [!warning] Pitfalls
> - **Suffix Array vs Suffix Automaton confusion** — Suffix Array handles pattern matching in O(m log n). Suffix Automaton handles it in O(m). For persistent queries where construction cost is amortized, Suffix Automaton may be faster. Know which you're implementing.
> - **Building LCP without sentinel** — Kasai's algorithm for LCP array requires a special sentinel character (e.g., '$') smaller than all alphabet characters. Without it, LCP values may be incorrect.
> - **O(n log n) vs O(n) construction** — the prefix-doubling SA construction is O(n log n) and sufficient for most problems (n ≤ 2·10^5). SA-IS / DC3 are O(n) but have heavy constants and implementation complexity. Use the simpler method unless n > 10^6.
> - **LCP for binary search** — when binary searching for a pattern in the suffix array, compare character by character from the suffix start. Without LCP, each comparison takes O(m). With LCP, you can skip already-matched characters for O(m + log n) total.
> - **Suffix Tree memory** — a suffix tree node count is O(n), but each node stores edge labels (start/end indices), children pointers, and suffix links → easily 40+ bytes per node. For n=10^6, this is 40MB+. Suffix Arrays use 4-8 bytes per index.

> [!question]- Q: What can a Suffix Array do that a Trie cannot?
> **Answer:** A Suffix Array enables **substring search** (not just prefix search) in O(m log n), **longest repeated substring**, **longest common substring** of two strings, and **distinct substring count** — all in O(n log n) preprocessing. A Trie only handles prefixes.

> [!question]- Q: How do you find the longest repeated substring using a Suffix Array?
> **Answer:** Build the Suffix Array and LCP array. The maximum value in the LCP array corresponds to the length of the longest repeated substring. Its position identifies the starting indices of the two occurrences.

> [!question]- Q: What's the difference between Suffix Array + LCP and Suffix Tree?
> **Answer:** Suffix Tree supports all Suffix Array operations in linear time but uses much more memory (heavy pointer structures). Suffix Array + LCP array supports the same queries in O(log n) or O(m + log n) with far less memory. Competitive programming favors Suffix Array; bioinformatics sometimes uses Suffix Trees.

> [!question]- Q: How do you find the longest common substring of two strings A and B?
> **Answer:** Concatenate `A + '#' + B + '$'`, build the SA and LCP arrays. Scan the LCP array for the maximum LCP value where the two suffixes belong to different strings (one from A, one from B). The maximum such LCP is the answer.

### Resources

- [Suffix Array - CP-Algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix Trees - Tushar Roy (YouTube)](https://www.youtube.com/watch?v=hPBPaF4pNUM)

---

## 15. Bloom Filters

### Overview

```mermaid
flowchart LR
    subgraph Bloom["Bloom Filter with 3 hash functions"]
        B0["BitArray[0]=0"] --- B1["BitArray[1]=1"] --- B2["BitArray[2]=1"]
        B2 --- B3["BitArray[3]=0"] --- B4["BitArray[4]=1"] --- B5["BitArray[5]=0"]
    end
    subgraph Insert_BF["Insert 'cat'"]
        I1["h1('cat')=1 → set bit 1"] --> I2["h2('cat')=4 → set bit 4"]
        I2 --> I3["h3('cat')=2 → set bit 2"]
    end
    subgraph Check["Check 'dog'"]
        C1["h1('dog')=1 → 1 ✓"] --> C2["h2('dog')=4 → 1 ✓"]
        C2 --> C3["h3('dog')=2 → 1 ✓ → maybe present (could be false positive)"]
    end

A space-efficient probabilistic data structure for set membership testing. May return false positives but never false negatives.

### Properties

- **Space**: O(m) bits where m is the filter size
- **Insert**: O(k) where k = number of hash functions
- **Query**: O(k)
- **False positive rate**: `(1 - e^(-kn/m))^k` where n = number of elements

### Use Cases

- Spell checkers
- Database query optimization (avoid disk lookups)
- Web crawlers (avoid revisiting URLs)
- Network routers (packet filtering)
- Cache filtering

### Pseudocode

#### Bloom Filter — Insert and Query
```
BloomFilter(m, k):           // m bits, k hash functions
    bitArray[1 .. m] ← {0}

Insert(element):
    for j ← 1 to k:
        idx ← Hashj(element) mod m + 1
        bitArray[idx] ← 1

Query(element):
    for j ← 1 to k:
        idx ← Hashj(element) mod m + 1
        if bitArray[idx] = 0:
            return false         // definitely not present
    return true                  // possibly present
```

> [!warning] Pitfalls
> - **False positive rate grows with load** — as more elements are inserted, the fraction of set bits increases. Beyond ~70% fill, FPR skyrockets. Size your filter appropriately upfront.
> - **No deletion support** — standard Bloom filters cannot remove elements (clearing a bit might affect other elements). Use Counting Bloom Filters if deletion is needed.
> - **Optimal k depends on m and n** — k = (m/n) * ln(2) ≈ 0.693 * (m/n). Too few hash functions → too many collisions. Too many → fills the array too fast, increasing FPR.
> - **Hash independence assumption** — theoretical FPR assumes hash functions are independent. In practice, using double hashing with two base hashes (`h1 + i*h2`) is sufficient and simpler than k independent hash functions.
> - **Not for small datasets** — for n < 10,000, a HashSet or boolean array is simpler, exact, and uses comparable memory. Bloom filters shine at scale (millions+ of items).

> [!question]- Q: Why "never false negatives, only false positives"?
> **Answer:** If an element was inserted, all k hash positions are set to 1 — querying it will always return true. But another element may have set those same k bits by coincidence, causing a false positive. The bits can never "unset" themselves to produce a false negative.

> [!question]- Q: How do you choose the size m and number of hash functions k?
> **Answer:** Given expected elements n and desired FPR ε: m = -n * ln(ε) / (ln 2)² bits, k = (m/n) * ln(2) ≈ 0.693 * (m/n). Example: n=1M, ε=1% → m≈9.6M bits (~1.2 MB), k≈7 hash functions.

> [!question]- Q: What's a Counting Bloom Filter?
> **Answer:** Instead of single bits, use small counters (e.g., 4 bits) at each position. Insert increments k counters; delete decrements them. Query returns true if all k counters > 0. The trade-off is more memory (counters instead of bits) and a tiny risk of counter overflow.

> [!question]- Q: When is a Bloom filter better than a hash set?
> **Answer:** When memory is constrained and a small false positive rate is acceptable. Example: Chromium's Safe Browsing uses Bloom filters to check URLs against a blocklist without storing the full blocklist locally. A hash set would require orders of magnitude more memory.

### Resources

- [Bloom Filters - GeeksforGeeks](https://www.geeksforgeeks.org/bloom-filters-introduction-and-python-implementation/)

---

## 16. Skip Lists

### Overview

```mermaid
flowchart TD
    subgraph Skip["Skip List levels"]
        L3["Level 3: -∞ → 20 → null"]
        L2["Level 2: -∞ → 10 → 20 → 30 → null"]
        L1["Level 1: -∞ → 5 → 10 → 15 → 20 → 25 → 30 → 35 → null"]
    end
    subgraph Search_SL["Search for 25"]
        S1["Start at top-left (-∞)"] --> S2["Move right to 20 → 25>20 → go down"]
        S2 --> S3["Move down to level 2 → move right to 30 → 25<30 → go down"]
        S3 --> S4["Move down to level 1 → move right to 25 ✓ found"]
    end

A skip list is a layered linked list that allows O(log n) search, insertion, and deletion on average. A probabilistic alternative to balanced BSTs.

### Complexity

| Operation | Average | Worst |
|-----------|:---:|:---:|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |

### Space: O(n log n) expected

### Key Concepts

- Multiple layers of linked lists
- Each element is "promoted" to the next level with probability p (usually 1/2)
- Search starts at the top level and drops down
- Used in Redis sorted sets, LevelDB

### Pseudocode

#### Skip List — Search and Insert
```
SkipListNode:
    key
    next[0 .. maxLevel]     // array of forward pointers

SkipListSearch(list, key):
    curr ← list.header
    for level ← list.maxLevel downto 0:
        while curr.next[level] ≠ NIL and curr.next[level].key < key:
            curr ← curr.next[level]
    curr ← curr.next[0]
    if curr ≠ NIL and curr.key = key:
        return curr
    return NIL

SkipListInsert(list, key):
    update[0 .. maxLevel]  // nodes to update at each level
    curr ← list.header
    for level ← list.maxLevel downto 0:
        while curr.next[level] ≠ NIL and curr.next[level].key < key:
            curr ← curr.next[level]
        update[level] ← curr
    curr ← curr.next[0]
    if curr ≠ NIL and curr.key = key:
        return              // duplicate; update value if needed
    newLevel ← RandomLevel()
    if newLevel > list.maxLevel:
        for level ← list.maxLevel + 1 to newLevel:
            update[level] ← list.header
        list.maxLevel ← newLevel
    newNode ← new SkipListNode with key and next array of size newLevel + 1
    for level ← 0 to newLevel:
        newNode.next[level] ← update[level].next[level]
        update[level].next[level] ← newNode

RandomLevel():
    level ← 0
    while random() < 0.5:     // p = 0.5
        level ← level + 1
    return min(level, MAX_LEVEL)
```

> [!warning] Pitfalls
> - **Random level generation bias** — using a global seed or predictable PRNG can cause adversarial performance. Use thread-local random or cryptographic randomness for fairness.
> - **Forgetting to update forward pointers at all levels** — during insertion, you must update `update[i].forward[i]` for every level i ≤ newLevel. Missing a level corrupts the skip list.
> - **Over-reliance on skip lists in production** — while O(log n) expected, skip lists have larger constant factors than B-Trees and AVL trees due to pointer chasing. For in-memory use, balanced BSTs are typically faster.
> - **Max level too low** — with p = 0.5, MAX_LEVEL = 16 handles ~2^16 = 65K elements at expected O(log n). For millions of elements, use MAX_LEVEL = 32 or 64.
> - **Not handling duplicates** — some skip list implementations allow duplicates and maintain insertion order (useful for multi-sets). Clarify whether your implementation supports duplicates.

> [!question]- Q: Why use a Skip List over a balanced BST?
> **Answer:** Skip lists are simpler to implement (no rotations, no rebalancing). They provide O(log n) expected time with probabilistic guarantees. Used in Redis sorted sets for range queries and ranking. The trade-off: they use more memory (multiple forward pointers per node).

> [!question]- Q: How does the search for element 25 work in a 3-level skip list?
> **Answer:** Start at the highest level of the head node. Move forward until the next element > 25, then drop one level. Repeat until level 0. At level 0, either the next element is 25 (found) or > 25 (not present). The expected number of steps is O(log n).

> [!question]- Q: What determines the expected height of a skip list?
> **Answer:** Each node's level is generated with geometric distribution: P(level ≥ k) = p^k. With p = 0.5, ~50% of nodes are at level 1, ~25% at level 2, ~12.5% at level 3, etc. Expected number of levels = log_{1/p}(n). The list is expected to be well-balanced.

> [!question]- Q: What's the relationship between skip lists and probability p?
> **Answer:** p controls the trade-off between time and space. p=0.5 gives ~2 forward pointers per node on average (expected levels = 2) and O(log n) search. p=0.25 uses less memory (~1.33 pointers) but slower search. p=0.5 is the standard choice.

### Resources

- [Skip Lists - MIT OCW](https://ocw.mit.edu/courses/6-046j-introduction-to-algorithms-sma-5503-fall-2005/resources/lecture-12-skip-lists/)

---

## 17. LRU / LFU Caches

```mermaid
flowchart TD
    subgraph LRU_State["LRU Cache (capacity=3)"]
        M1["Map: {A→nodeA, B→nodeB, C→nodeC}"]
        LL["List: Head ↔ A ↔ B ↔ C ↔ Tail"]
    end
    subgraph Get_B["get(B)"]
        G1["Find B in map O(1)"] --> G2["Move B to head"]
        G2 --> G3["List: Head ↔ B ↔ A ↔ C ↔ Tail"]
    end
    subgraph Put_D["put(D) — cache full"]
        P1["Create node for D"] --> P2["Remove Tail (C)"]
        P2 --> P3["Map remove C, List delete C"]
        P3 --> P4["Insert D at Head"]
        P4 --> P5["Map add D, List: Head ↔ D ↔ B ↔ A ↔ Tail"]
    end

### Overview

Cache eviction data structures used in operating systems, databases, and web servers.

### LRU (Least Recently Used)

- Evicts the least recently accessed item
- Implementation: **Doubly Linked List + Hash Map**
- All operations O(1)

#### LRU Cache Pseudocode
```
LRUCache(capacity):
    dll ← DoublyLinkedList()      // head = MRU, tail = LRU
    map ← HashMap(key → Node)

Get(key):
    if key not in map: return -1
    node ← map[key]
    dll.Remove(node)
    dll.AddToHead(node)           // mark as most recently used
    return node.value

Put(key, value):
    if key in map:
        node ← map[key]
        node.value ← value
        dll.Remove(node)
        dll.AddToHead(node)
    else:
        if map.size = capacity:
            lru ← dll.tail
            dll.Remove(lru)
            map.Delete(lru.key)
        newNode ← new Node(key, value)
        dll.AddToHead(newNode)
        map.Insert(key, newNode)
```

### LFU (Least Frequently Used)

- Evicts the least frequently accessed item (ties broken by LRU)
- Implementation: **Two Hash Maps + Doubly Linked Lists per frequency**
- All operations O(1)

#### LFU Cache Pseudocode
```
LFUCache(capacity):
    minFreq ← 0
    keyMap ← HashMap(key → Node)              // O(1) key lookup
    freqMap ← HashMap(freq → DLL)              // freq → doubly linked list

Node:
    key, value, freq, prev, next

Get(key):
    if key not in keyMap: return -1
    node ← keyMap[key]
    UpdateFrequency(node)
    return node.value

Put(key, value):
    if capacity = 0: return
    if key in keyMap:
        node ← keyMap[key]
        node.value ← value
        UpdateFrequency(node)
    else:
        if keyMap.size = capacity:
            evictList ← freqMap[minFreq]
            nodeToEvict ← evictList.tail
            evictList.Remove(nodeToEvict)
            keyMap.Delete(nodeToEvict.key)
        newNode ← new Node(key, value, freq ← 1)
        keyMap.Insert(key, newNode)
        freqMap[1].AddToHead(newNode)
        minFreq ← 1

UpdateFrequency(node):
    oldFreq ← node.freq
    freqMap[oldFreq].Remove(node)
    if freqMap[oldFreq].isEmpty and oldFreq = minFreq:
        minFreq ← minFreq + 1
    node.freq ← node.freq + 1
    freqMap[node.freq].AddToHead(node)
```

### Common Patterns

- LRU Cache (LeetCode 146)
- LFU Cache (LeetCode 460)
- Design patterns for caching systems

> [!warning] Pitfalls
> - **LRU with O(1) get and put** — requires a HashMap + DoublyLinkedList. The HashMap gives O(1) node lookup; the doubly linked list gives O(1) insertion at head and removal from any position. Using an array or singly linked list cannot achieve O(1) for both operations.
> - **LFU eviction tie-breaking** — when multiple keys have the same frequency, LFU must evict the least recently used among them. Often implemented as LFU + LRU hybrid: each frequency bucket is an LRU list.
> - **Not updating LFU counter on get** — in LFU, `get(key)` increases that key's access frequency and may move it to a different frequency bucket. Forgetting this means the key stays at an old (lower) frequency.
> - **Cache stampede** — when a popular cached item expires, many requests simultaneously hit the database to recompute it. Use probabilistic early expiration or request coalescing (only one thread recomputes).
> - **Thread safety of cache implementations** — the standard LRU/LFU implementations (HashMap + LinkedList) are not thread-safe. For concurrent access, use `ConcurrentHashMap` + `ConcurrentLinkedDeque` or a read-write lock.

> [!question]- Q: How does an LRU Cache achieve O(1) get and put?
> **Answer:** **HashMap** maps key → node reference for O(1) lookup. **Doubly Linked List** keeps nodes in access order (head = most recent, tail = least recent). On get/put, move the accessed node to head. On eviction, remove tail. Both move and remove are O(1) because we have the node reference from the HashMap.

> [!question]- Q: What's the difference between LRU and LFU?
> **Answer:** **LRU** (Least Recently Used): evicts the item not accessed for the longest time. Favors recency. **LFU** (Least Frequently Used): evicts the item with the lowest access count. Favors frequency. LFU handles "frequently accessed cold items" better; LRU is simpler and works well for temporal locality.

> [!question]- Q: When does LFU beat LRU?
> **Answer:** LFU beats LRU when access patterns are frequency-based rather than recency-based. Example: a news site where top articles get hit constantly while newer articles get sporadic bursts. LRU might evict a frequently-accessed item that hasn't been accessed in the last minute; LFU preserves it due to high cumulative count.

> [!question]- Q: How do you avoid cache stampede?
> **Answer:** Techniques: (1) **Probabilistic early expiration** — expire items at t * (1 + random(0, delta)) instead of exactly at t. (2) **Request coalescing** — the first request that finds a missing key initiates the recomputation; other concurrent requests wait on a promise/future for the result.

### Resources

- [LRU Cache - GeeksforGeeks](https://www.geeksforgeeks.org/lru-cache-implementation/)

---


## Visualization Resources

> [!tip]- Interactive visualizations
> - [VisuAlgo](https://visualgo.net/en) — Sorting, linked list, BST, AVL, heap, graph, TSP, suffix tree
> - [USFCA Visualization Tool](https://www.cs.usfca.edu/~galles/visualization/Algorithms.html) — All DS + sorting, searching, DP, geometry
> - [Algorithm Visualizer](https://algorithm-visualizer.org/) — Dynamic step-through with code
> - [BST Visualization](https://www.cs.usfca.edu/~galles/visualization/BST.html) | [AVL Tree](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html) | [RBT](https://www.cs.usfca.edu/~galles/visualization/RedBlack.html)
> - [Heap](https://visualgo.net/en/heap) | [Hash Table](https://visualgo.net/en/hashtable) | [Graph traversal](https://visualgo.net/en/dfsbfs)
> - [Sorting](https://visualgo.net/en/sorting) | [Binary Search](https://visualgo.net/en/search) | [KMP](https://www.cs.usfca.edu/~galles/visualization/KMP.html)
> - [Radix Sort](https://www.cs.usfca.edu/~galles/visualization/RadixSort.html) | [Counting Sort](https://www.cs.usfca.edu/~galles/visualization/CountingSort.html)
> - [Dijkstra's Algorithm](https://visualgo.net/en/sssp) | [Prim's MST](https://www.cs.usfca.edu/~galles/visualization/Prim.html) | [Kruskal's MST](https://www.cs.usfca.edu/~galles/visualization/Kruskal.html)

## Comparison Summary

| Data Structure | Access | Search | Insert | Delete | Space |
|----------------|:---:|:---:|:---:|:---:|:---:|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Linked List | O(n) | O(n) | O(1)* | O(1)* | O(n) |
| Stack | O(n) | O(n) | O(1) | O(1) | O(n) |
| Queue | O(n) | O(n) | O(1) | O(1) | O(n) |
| Hash Table | N/A | O(1) avg | O(1) avg | O(1) avg | O(n) |
| BST | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Balanced BST | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | O(1)** | O(n) | O(log n) | O(log n) | O(n) |
| Trie | O(L) | O(L) | O(L) | O(L) | O(ALPHABET * L * N) |
| Segment Tree | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Fenwick Tree | O(log n) | O(log n) | O(log n) | N/A | O(n) |

\* At known position | \*\* Min/Max only

---

## Recommended Study Order

### Phase 1: Foundations (Weeks 1-3)
1. Arrays & Strings
2. Linked Lists
3. Stacks & Queues
4. Hash Tables

### Phase 2: Intermediate (Weeks 4-7)
5. Binary Trees & BST
6. Heaps / Priority Queues
7. Graphs (basics: BFS, DFS, adjacency list)

### Phase 3: Advanced (Weeks 8-12)
8. Tries
9. Union-Find
10. Graphs (advanced: SCC, bridges, topological sort)
11. Segment Trees & Fenwick Trees

### Phase 4: Expert (Weeks 13+)
12. Balanced BSTs (AVL, Red-Black)
13. Suffix Arrays & Trees
14. Bloom Filters, Skip Lists
15. Persistent & Advanced data structures

---

## Recommended Resources

### Books
- *Introduction to Algorithms* (CLRS) — the gold standard
- *Algorithms* by Robert Sedgewick — excellent Java-based
- *The Algorithm Design Manual* by Steven Skiena — practical focus
- *Competitive Programming 3* by Steven Halim — for contest prep

### Online Courses
- [MIT 6.006 Introduction to Algorithms](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/)
- [MIT 6.046 Design and Analysis of Algorithms](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/)
- [Stanford Algorithms Specialization (Coursera)](https://www.coursera.org/specializations/algorithms)
- [Abdul Bari's Algorithms (YouTube)](https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O)
- [William Fiset's Data Structures (YouTube)](https://www.youtube.com/playlist?list=PLDV1Zeh2NRsB6SWUrDFW2RmDotAfPbeHu)

### Practice Platforms
- [LeetCode](https://leetcode.com/) — interview-focused
- [Codeforces](https://codeforces.com/) — competitive programming
- [AtCoder](https://atcoder.jp/) — clean problems, editorial solutions
- [HackerRank](https://www.hackerrank.com/) — structured tracks
- [NeetCode](https://neetcode.io/) — curated 150 problems with video solutions

### Visualization Tools
- [VisuAlgo](https://visualgo.net/) — animated data structure operations
- [Data Structure Visualizations (USF)](https://www.cs.usfca.edu/~galles/visualization/Algorithms.html)
- [Algorithm Visualizer](https://algorithm-visualizer.org/)
