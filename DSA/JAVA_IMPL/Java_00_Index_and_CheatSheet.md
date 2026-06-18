---
tags: [dsa, java, implementations]
aliases: ["Java DSA Index", "Java DSA Cheatsheet"]
status: stable
updated: 2026-04-26
---

# Java DSA Implementation Index

Complete Java 17+ implementations of all data structures and algorithms from [[DataStructures]] and [[Algorithms]].

> [!summary] Start Here
> 1. Revise concepts: [[DataStructures]] and [[Algorithms]]
> 2. Jump into Java code: pick the relevant `JAVA_IMPL` file below
> 3. Practice: [[Questions]]

> [!tip] Revision Path
> - Phase 1: [[DataStructures#1. Arrays]] , [[Algorithms#2. Sorting Algorithms]] , [[Algorithms#3. Searching Algorithms]]
> - Phase 2: [[DataStructures#3. Linked Lists]] , [[DataStructures#4. Stacks]] , [[DataStructures#5. Queues]] , [[Algorithms#12. Two Pointers & Sliding Window]]
> - Phase 3: [[DataStructures#7. Trees]] , [[DataStructures#9. Graphs]] , [[Algorithms#8. Graph Algorithms]]
> - Phase 4: [[Algorithms#7. Dynamic Programming]] , [[DataStructures#12. Segment Trees]]

---

## 📚 Quick Navigation

| File | Contents | Implementations |
|------|----------|-----------------|
| [[Java_01_Fundamental_DS]] | Linear DS, Hash, Basic Trees | 23 |
| [[Java_02_Advanced_DS]] | Advanced Trees, Graphs, Caches | 20 |
| [[Java_03_Algorithms_Part1]] | Sorting, Searching, Greedy, Backtracking | 53 |
| [[Java_04_Algorithms_Part2]] | DP, Graph Algos, Strings, Math | 64 |
| [[Java_05_Utilities_Templates]] | Helpers, Patterns, Common Utils | ~15 |
| [[Java_06_Advanced_Algorithms_CP]] | Flow, FFT/NTT, Geometry, Mo's, NP/Approx | CP |

---

## 📊 Complete Complexity Cheat Sheet

### Data Structures

| Structure | Access | Search | Insert | Delete | Space |
|-----------|:------:|:------:|:------:|:------:|:-----:|
| **Static Array** | O(1) | O(n) | O(n) | O(n) | O(n) |
| **Dynamic Array** | O(1) | O(n) | O(1)* | O(n) | O(n) |
| **Singly Linked List** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Doubly Linked List** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Circular Linked List** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Stack (Array)** | O(1) | O(n) | O(1) | O(1) | O(n) |
| **Stack (Linked)** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Queue (Array)** | O(1) | O(n) | O(1) | O(1) | O(n) |
| **Queue (Linked)** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Circular Queue** | O(1) | O(n) | O(1) | O(1) | O(n) |
| **Deque** | O(1) | O(n) | O(1) | O(1) | O(n) |
| **Monotonic Stack** | O(1) | O(1) | O(1) | O(1) | O(n) |
| **Monotonic Queue** | O(1) | O(1) | O(1) | O(1) | O(n) |
| **Hash Table** | N/A | O(1) | O(1) | O(1) | O(n) |
| **HashSet** | N/A | O(1) | O(1) | O(1) | O(n) |
| **Binary Tree** | O(n) | O(n) | O(n) | O(n) | O(n) |
| **BST** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **AVL Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **Red-Black Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **Splay Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **B-Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **N-ary Tree** | O(n) | O(n) | O(n) | O(n) | O(n) |
| **Min/Max Heap** | O(1)** | O(n) | O(log n) | O(log n) | O(n) |
| **Trie** | O(L) | O(L) | O(L) | O(L) | O(AL × N) |
| **Suffix Array** | O(1) | O(m log n) | O(n log n) | O(n log n) | O(n) |
| **Graph (Adj List)** | O(1) | O(V+E) | O(1) | O(V+E) | O(V+E) |
| **Graph (Adj Matrix)** | O(1) | O(V²) | O(1) | O(1) | O(V²) |
| **Union-Find** | O(α(n)) | O(α(n)) | O(α(n)) | O(α(n)) | O(n) |
| **Segment Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **Fenwick Tree** | O(log n) | O(log n) | O(log n) | - | O(n) |
| **Bloom Filter** | - | O(k) | O(k) | - | O(m) |
| **Skip List** | O(log n) | O(log n) | O(log n) | O(log n) | O(n log n) |
| **LRU Cache** | O(1) | O(1) | O(1) | O(1) | O(n) |
| **LFU Cache** | O(1) | O(1) | O(1) | O(1) | O(n) |

*Amortized | **Min/Max only

---

### Sorting Algorithms

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|:----:|:-------:|:-----:|:-----:|:------:|
| **Bubble Sort** | O(n) | O(n²) | O(n²) | O(1) | Yes |
| **Selection Sort** | O(n²) | O(n²) | O(n²) | O(1) | No |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | Yes |
| **Shell Sort** | O(n log n) | O(n^1.5) | O(n²) | O(1) | No |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| **Counting Sort** | O(n+k) | O(n+k) | O(n+k) | O(n+k) | Yes |
| **Radix Sort** | O(d×(n+k)) | O(d×(n+k)) | O(d×(n+k)) | O(n+k) | Yes |
| **Bucket Sort** | O(n+k) | O(n+k) | O(n²) | O(n+k) | Yes |

---

### Searching Algorithms

| Algorithm | Time | Space | Condition |
|-----------|:----:|:-----:|-----------|
| **Linear Search** | O(n) | O(1) | Any array |
| **Binary Search** | O(log n) | O(1) | Sorted array |
| **Ternary Search** | O(log n) | O(1) | Unimodal function |
| **Interpolation Search** | O(log log n) | O(1) | Uniformly distributed |
| **Exponential Search** | O(log n) | O(1) | Unbounded arrays |
| **Jump Search** | O(√n) | O(1) | Sorted array |
| **Fibonacci Search** | O(log n) | O(1) | Sorted array |

---

### Graph Algorithms

| Algorithm | Time | Space | Purpose |
|-----------|:----:|:-----:|---------|
| **BFS** | O(V+E) | O(V) | Shortest path (unweighted) |
| **DFS** | O(V+E) | O(V) | Cycle detection, traversal |
| **Dijkstra's** | O(E log V) | O(V) | Shortest path (non-negative) |
| **Bellman-Ford** | O(V×E) | O(V) | Shortest path (with negatives) |
| **Floyd-Warshall** | O(V³) | O(V²) | All-pairs shortest path |
| **Kruskal's MST** | O(E log E) | O(V) | Minimum spanning tree |
| **Prim's MST** | O(E log V) | O(V) | Minimum spanning tree |
| **Topological Sort** | O(V+E) | O(V) | DAG ordering |
| **Kosaraju's SCC** | O(V+E) | O(V) | Strongly connected components |
| **Tarjan's SCC** | O(V+E) | O(V) | Strongly connected components |
| **Ford-Fulkerson** | O(E×max_flow) | O(V) | Maximum flow |
| **Edmonds-Karp** | O(V×E²) | O(V) | Maximum flow (BFS-based) |
| **Dinic's** | O(V²×E) | O(V) | Maximum flow |

---

### String Algorithms

| Algorithm | Preprocess | Matching | Total |
|-----------|:----------:|:--------:|:-----:|
| **KMP** | O(m) | O(n) | O(n+m) |
| **Rabin-Karp** | O(m) | O(n) | O(n+m) |
| **Z-Algorithm** | - | O(n+m) | O(n+m) |
| **Manacher's** | - | O(n) | O(n) |
| **Suffix Array** | O(n log n) | O(m log n) | O(n log n) |

---

## 🔧 Java 17+ Quick Reference

### Records
```java
public record Node<T>(T data, Node<T> next) {}
public record Edge(int from, int to, int weight) {}
public record Pair<K, V>(K key, V value) {}
```

### Pattern Matching for instanceof
```java
if (obj instanceof Node<?> n) {
    // n is automatically cast and available
}
```

### Switch Expressions
```java
var result = switch (choice) {
    case 1 -> "insert";
    case 2 -> "delete";
    case 3, 4 -> "update";
    default -> throw new IllegalArgumentException();
};
```

### var (Local Variable Type Inference)
```java
var list = new ArrayList<String>();  // Inferred as ArrayList<String>
var count = 0;                        // Inferred as int
var node = new Node<>(data, null);   // Inferred as Node<T>
```

### Text Blocks
```java
String diagram = """
        [Root]
        /    \\
    [Left]  [Right]
    """;
```

---

## 📋 Implementation Categories

### Fundamental Data Structures (File 01)
- Linear structures (Arrays, Linked Lists, Stacks, Queues)
- Hash tables with collision handling
- Basic trees and heaps

### Advanced Data Structures (File 02)
- Self-balancing trees (AVL, Red-Black, Splay)
- Tries and suffix structures
- Graph representations
- Advanced structures (Union-Find, Segment Tree, Fenwick)
- Probabilistic structures (Bloom Filter, Skip List)
- Cache implementations (LRU, LFU)

### Algorithms Part 1 (File 03)
- All sorting algorithms
- Searching and binary search variants
- Recursion and backtracking
- Divide and conquer
- Greedy algorithms

### Algorithms Part 2 (File 04)
- Dynamic programming (all patterns)
- Graph algorithms (traversal, shortest path, MST, flow)
- String algorithms
- Mathematical algorithms

### Utilities (File 05)
- Common helper classes
- Template patterns
- Comparator utilities
- Testing helpers

---

## 🎯 Study Recommendations

### Phase 1: Foundations
Start with File 01 - Fundamental Data Structures
- Arrays and Linked Lists (A.1-A.4)
- Stacks and Queues (A.6-A.11)
- Hash Tables (B.1-B.3)
- Binary Trees and BST (C.1-C.2)

### Phase 2: Core Algorithms
Move to File 03 - Algorithms Part 1
- Sorting algorithms (J.1-J.7)
- Binary search (K.2-K.7)
- Basic recursion and backtracking (L.1-L.6)

### Phase 3: Advanced
Tackle File 02 - Advanced Data Structures
- Segment Trees and Fenwick Trees
- Graph representations
- Union-Find

### Phase 4: Complex Algorithms
Finish with File 04 - Algorithms Part 2
- Dynamic programming patterns
- Graph algorithms
- String matching

---

## 🔗 External Resources

- [Java 17 Documentation](https://docs.oracle.com/en/java/javase/17/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [VisuAlgo](https://visualgo.net/)
- [Algorithm Visualizer](https://algorithm-visualizer.org/)

---

*Last Updated: 2026-04-18 | Java Version: 17+*
