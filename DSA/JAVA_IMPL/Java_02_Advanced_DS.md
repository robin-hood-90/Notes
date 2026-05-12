# Java 02: Advanced Data Structures

Complete Java 17+ implementations of advanced trees, graph structures, and specialized data structures.

---

## Table of Contents

### Section E: Advanced Trees
- [E.1 Red-Black Tree](#e-1-red-black-tree)
- [E.2 Splay Tree](#e-2-splay-tree)
- [E.3 B-Tree](#e-3-b-tree)
- [E.4 Segment Tree](#e-4-segment-tree)
- [E.5 Fenwick Tree (BIT)](#e-5-fenwick-tree)

### Section F: Trie & Suffix Structures
- [F.1 Trie (Prefix Tree)](#f-1-trie)
- [F.2 Compressed Trie](#f-2-compressed-trie)
- [F.3 Suffix Trie](#f-3-suffix-trie)
- [F.4 Suffix Array](#f-4-suffix-array)

### Section G: Graph Representations
- [G.1 Graph (Adjacency Matrix)](#g-1-graph)
- [G.2 Graph (Adjacency List)](#g-2-graph)
- [G.3 Weighted Graph](#g-3-weighted-graph)
- [G.4 Directed Graph](#g-4-directed-graph)

### Section H: Union-Find & Advanced Structures
- [H.1 Union-Find (DSU)](#h-1-union-find)
- [H.2 Union-Find with Rollback](#h-2-union-find-with-rollback)
- [H.3 Bloom Filter](#h-3-bloom-filter)
- [H.4 Skip List](#h-4-skip-list)

### Section I: Caches
- [I.1 LRU Cache](#i-1-lru-cache)
- [I.2 LFU Cache](#i-2-lfu-cache)

---

## Section E: Advanced Trees

---

### E.1 Red-Black Tree

**Concept:** Self-balancing BST where each node is colored red or black, ensuring height ≤ 2log(n).

**Properties:**
1. Every node is either red or black
2. Root is always black
3. All leaves (NIL) are black
4. Red nodes cannot have red children
5. Every path from root to leaf has same number of black nodes

**Visual:**
```
       [B:20]
      /      \
   [R:10]   [R:30]
   /    \     /    \
[NIL] [NIL] [NIL] [NIL]
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Search | O(log n) | O(1) |
| Insert | O(log n) | O(1) |
| Delete | O(log n) | O(1) |

```java
/**
 * Red-Black Tree implementation - self-balancing BST.
 * Guarantees O(log n) operations by maintaining balance properties.
 */
public class RedBlackTree<T extends Comparable<T>> {
    
    private enum Color { RED, BLACK }
    
    private static class Node<T> {
        T data;
        Node<T> left, right, parent;
        Color color;
        
        Node(T data) {
            this.data = data;
            this.color = Color.RED; // New nodes are red
        }
    }
    
    private Node<T> root;
    private int size;
    
    public RedBlackTree() {
        this.root = null;
        this.size = 0;
    }
    
    public void insert(T data) {
        var node = new Node<>(data);
        
        // Standard BST insert
        root = bstInsert(root, node);
        
        // Fix Red-Black properties
        fixInsert(node);
        
        // Ensure root is black
        root.color = Color.BLACK;
        size++;
    }
    
    private Node<T> bstInsert(Node<T> root, Node<T> node) {
        if (root == null) return node;
        
        if (node.data.compareTo(root.data) < 0) {
            root.left = bstInsert(root.left, node);
            root.left.parent = root;
        } else if (node.data.compareTo(root.data) > 0) {
            root.right = bstInsert(root.right, node);
            root.right.parent = root;
        }
        
        return root;
    }
    
    private void fixInsert(Node<T> node) {
        while (node != root && node.parent.color == Color.RED) {
            var parent = node.parent;
            var grandparent = parent.parent;
            
            if (parent == grandparent.left) {
                var uncle = grandparent.right;
                
                // Case 1: Uncle is red
                if (uncle != null && uncle.color == Color.RED) {
                    parent.color = Color.BLACK;
                    uncle.color = Color.BLACK;
                    grandparent.color = Color.RED;
                    node = grandparent;
                } else {
                    // Case 2: Node is right child
                    if (node == parent.right) {
                        node = parent;
                        leftRotate(node);
                    }
                    
                    // Case 3: Node is left child
                    parent.color = Color.BLACK;
                    grandparent.color = Color.RED;
                    rightRotate(grandparent);
                }
            } else {
                // Mirror cases
                var uncle = grandparent.left;
                
                if (uncle != null && uncle.color == Color.RED) {
                    parent.color = Color.BLACK;
                    uncle.color = Color.BLACK;
                    grandparent.color = Color.RED;
                    node = grandparent;
                } else {
                    if (node == parent.left) {
                        node = parent;
                        rightRotate(node);
                    }
                    
                    parent.color = Color.BLACK;
                    grandparent.color = Color.RED;
                    leftRotate(grandparent);
                }
            }
        }
    }
    
    private void leftRotate(Node<T> x) {
        var y = x.right;
        x.right = y.left;
        
        if (y.left != null) {
            y.left.parent = x;
        }
        
        y.parent = x.parent;
        
        if (x.parent == null) {
            root = y;
        } else if (x == x.parent.left) {
            x.parent.left = y;
        } else {
            x.parent.right = y;
        }
        
        y.left = x;
        x.parent = y;
    }
    
    private void rightRotate(Node<T> y) {
        var x = y.left;
        y.left = x.right;
        
        if (x.right != null) {
            x.right.parent = y;
        }
        
        x.parent = y.parent;
        
        if (y.parent == null) {
            root = x;
        } else if (y == y.parent.right) {
            y.parent.right = x;
        } else {
            y.parent.left = x;
        }
        
        x.right = y;
        y.parent = x;
    }
    
    public boolean search(T data) {
        return searchNode(root, data) != null;
    }
    
    private Node<T> searchNode(Node<T> node, T data) {
        if (node == null) return null;
        
        var cmp = data.compareTo(node.data);
        if (cmp < 0) return searchNode(node.left, data);
        if (cmp > 0) return searchNode(node.right, data);
        return node;
    }
    
    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
}
```

**Key Points:**
- Guarantees O(log n) worst-case for all operations
- Used in Java's `TreeMap` and `TreeSet`
- More relaxed balancing than AVL (fewer rotations)
- Color flips propagate up, rotations fix violations

---

### E.2 Splay Tree

**Concept:** Self-adjusting BST that moves accessed nodes to root via splaying. Amortized O(log n).

**Visual:**
```
Access 10:
Before:      After Splay:
    20           10
   /            /  \
  10     ->   5   20
 /                /
5                15
```

**Complexity:**
| Operation | Amortized | Worst |
|-----------|:---------:|:-----:|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |

```java
/**
 * Splay Tree - self-adjusting BST.
 * Frequently accessed elements move closer to root.
 */
public class SplayTree<T extends Comparable<T>> {
    
    private static class Node<T> {
        T data;
        Node<T> left, right, parent;
        
        Node(T data) {
            this.data = data;
        }
    }
    
    private Node<T> root;
    private int size;
    
    public void insert(T data) {
        if (root == null) {
            root = new Node<>(data);
            size++;
            return;
        }
        
        root = splay(root, data);
        
        var cmp = data.compareTo(root.data);
        if (cmp == 0) return; // Duplicate
        
        var node = new Node<>(data);
        if (cmp < 0) {
            node.left = root.left;
            node.right = root;
            root.left = null;
        } else {
            node.right = root.right;
            node.left = root;
            root.right = null;
        }
        
        root = node;
        size++;
    }
    
    public boolean search(T data) {
        root = splay(root, data);
        return root != null && data.compareTo(root.data) == 0;
    }
    
    /**
     * Splay operation - brings data to root.
     */
    private Node<T> splay(Node<T> node, T data) {
        if (node == null) return null;
        
        var cmp = data.compareTo(node.data);
        
        if (cmp < 0) {
            if (node.left == null) return node;
            
            if (data.compareTo(node.left.data) < 0) {
                // Zig-zig (left-left)
                node.left.left = splay(node.left.left, data);
                node = rightRotate(node);
            } else if (data.compareTo(node.left.data) > 0) {
                // Zig-zag (left-right)
                node.left.right = splay(node.left.right, data);
                if (node.left.right != null) {
                    node.left = leftRotate(node.left);
                }
            }
            
            return node.left == null ? node : rightRotate(node);
        } else if (cmp > 0) {
            if (node.right == null) return node;
            
            if (data.compareTo(node.right.data) > 0) {
                // Zag-zag (right-right)
                node.right.right = splay(node.right.right, data);
                node = leftRotate(node);
            } else if (data.compareTo(node.right.data) < 0) {
                // Zag-zig (right-left)
                node.right.left = splay(node.right.left, data);
                if (node.right.left != null) {
                    node.right = rightRotate(node.right);
                }
            }
            
            return node.right == null ? node : leftRotate(node);
        }
        
        return node; // Found
    }
    
    private Node<T> leftRotate(Node<T> x) {
        var y = x.right;
        x.right = y.left;
        y.left = x;
        return y;
    }
    
    private Node<T> rightRotate(Node<T> x) {
        var y = x.left;
        x.left = y.right;
        y.right = x;
        return y;
    }
}
```

**Key Points:**
- Amortized O(log n) - good for sequences of operations
- Recently accessed items are fast to access again
- No extra storage needed for balance info
- Used in cache implementations

---

### E.3 B-Tree

**Concept:** Self-balancing search tree optimized for systems with slow storage. Each node has multiple keys.

**Visual (order 3):**
```
       [20|50]
      /   |   \
[5|10] [30|40] [60|70]
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Search | O(log n) | O(1) |
| Insert | O(log n) | O(1) |
| Delete | O(log n) | O(1) |

```java
/**
 * B-Tree implementation optimized for disk storage.
 * Each node contains multiple keys and children.
 */
public class BTree<T extends Comparable<T>> {
    
    private static class Node<T> {
        List<T> keys;
        List<Node<T>> children;
        boolean isLeaf;
        
        Node(boolean isLeaf) {
            this.keys = new ArrayList<>();
            this.children = new ArrayList<>();
            this.isLeaf = isLeaf;
        }
    }
    
    private Node<T> root;
    private final int minDegree; // t
    private int size;
    
    public BTree(int minDegree) {
        if (minDegree < 2) {
            throw new IllegalArgumentException("Min degree must be at least 2");
        }
        this.minDegree = minDegree;
        this.root = new Node<>(true);
        this.size = 0;
    }
    
    public void insert(T key) {
        var root = this.root;
        
        // If root is full, split
        if (root.keys.size() == 2 * minDegree - 1) {
            var newRoot = new Node<T>(false);
            newRoot.children.add(this.root);
            this.root = newRoot;
            splitChild(newRoot, 0, root);
        }
        
        insertNonFull(this.root, key);
        size++;
    }
    
    private void insertNonFull(Node<T> node, T key) {
        var i = node.keys.size() - 1;
        
        if (node.isLeaf) {
            // Insert into leaf
            node.keys.add(null); // Expand
            while (i >= 0 && key.compareTo(node.keys.get(i)) < 0) {
                node.keys.set(i + 1, node.keys.get(i));
                i--;
            }
            node.keys.set(i + 1, key);
        } else {
            // Find child to insert into
            while (i >= 0 && key.compareTo(node.keys.get(i)) < 0) {
                i--;
            }
            i++;
            
            // Split child if full
            if (node.children.get(i).keys.size() == 2 * minDegree - 1) {
                splitChild(node, i, node.children.get(i));
                if (key.compareTo(node.keys.get(i)) > 0) {
                    i++;
                }
            }
            
            insertNonFull(node.children.get(i), key);
        }
    }
    
    private void splitChild(Node<T> parent, int i, Node<T> fullChild) {
        var newChild = new Node<T>(fullChild.isLeaf);
        var mid = minDegree - 1;
        
        // Move keys from fullChild to newChild
        for (var j = 0; j < mid; j++) {
            newChild.keys.add(fullChild.keys.remove(mid + 1));
        }
        
        // Move children if not leaf
        if (!fullChild.isLeaf) {
            for (var j = 0; j <= mid; j++) {
                newChild.children.add(fullChild.children.remove(mid + 1));
            }
        }
        
        // Insert median key to parent
        parent.children.add(i + 1, newChild);
        parent.keys.add(i, fullChild.keys.remove(mid));
    }
    
    public boolean search(T key) {
        return searchNode(root, key);
    }
    
    private boolean searchNode(Node<T> node, T key) {
        var i = 0;
        while (i < node.keys.size() && key.compareTo(node.keys.get(i)) > 0) {
            i++;
        }
        
        if (i < node.keys.size() && key.compareTo(node.keys.get(i)) == 0) {
            return true;
        }
        
        if (node.isLeaf) {
            return false;
        }
        
        return searchNode(node.children.get(i), key);
    }
    
    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
}
```

**Key Points:**
- Minimizes disk I/O by storing multiple keys per node
- All leaves at same depth (perfectly balanced)
- Used in databases and file systems
- B+ Tree variant stores all data in leaves

---

### E.4 Segment Tree

**Concept:** Binary tree for range queries and updates. Each node represents an interval.

**Visual (array [1,3,5,7,9,11]):**
```
           [0-5:36]
          /        \
    [0-2:9]        [3-5:27]
    /     \        /      \
[0-1:4] [2-2:5] [3-4:16] [5-5:11]
/    \           /    \
[0:1][1:3]   [3:7][4:9]
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Build | O(n) | O(n) |
| Query | O(log n) | O(1) |
| Point Update | O(log n) | O(1) |
| Range Update* | O(log n) | O(1) |

*With lazy propagation

```java
/**
 * Segment Tree for range sum queries and updates.
 * Supports point updates and range queries in O(log n).
 */
public class SegmentTree {
    
    private final long[] tree;
    private final int n;
    
    public SegmentTree(int[] arr) {
        this.n = arr.length;
        // Size: 4*n is safe for segment trees
        this.tree = new long[4 * n];
        build(arr, 0, 0, n - 1);
    }
    
    /**
     * Build segment tree recursively.
     */
    private void build(int[] arr, int node, int start, int end) {
        if (start == end) {
            tree[node] = arr[start];
            return;
        }
        
        var mid = (start + end) / 2;
        build(arr, 2 * node + 1, start, mid);
        build(arr, 2 * node + 2, mid + 1, end);
        
        tree[node] = tree[2 * node + 1] + tree[2 * node + 2];
    }
    
    /**
     * Query sum in range [l, r]. O(log n) time.
     */
    public long query(int l, int r) {
        return query(0, 0, n - 1, l, r);
    }
    
    private long query(int node, int start, int end, int l, int r) {
        // Complete overlap
        if (l <= start && end <= r) {
            return tree[node];
        }
        
        // No overlap
        if (end < l || start > r) {
            return 0;
        }
        
        // Partial overlap
        var mid = (start + end) / 2;
        var leftSum = query(2 * node + 1, start, mid, l, r);
        var rightSum = query(2 * node + 2, mid + 1, end, l, r);
        
        return leftSum + rightSum;
    }
    
    /**
     * Update element at index. O(log n) time.
     */
    public void update(int index, int value) {
        update(0, 0, n - 1, index, value);
    }
    
    private void update(int node, int start, int end, int index, int value) {
        if (start == end) {
            tree[node] = value;
            return;
        }
        
        var mid = (start + end) / 2;
        if (index <= mid) {
            update(2 * node + 1, start, mid, index, value);
        } else {
            update(2 * node + 2, mid + 1, end, index, value);
        }
        
        tree[node] = tree[2 * node + 1] + tree[2 * node + 2];
    }
}
```

**Key Points:**
- Versatile: supports sum, min, max, GCD queries
- Can be extended with lazy propagation for range updates
- Array-based implementation is cache-friendly
- 4*n size is sufficient for any segment tree

---

### E.5 Fenwick Tree (BIT)

**Concept:** Binary Indexed Tree for prefix sums. More memory-efficient than segment tree.

**Visual (array [1,2,3,4,5]):**
```
Index: 1  2  3  4  5
BIT:   1  3  3  10 5

Tree structure (parent = i + lsb(i)):
1 -> 2 -> 4
3 -> 4
5
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Build | O(n log n) | O(n) |
| Update | O(log n) | O(1) |
| Prefix Sum | O(log n) | O(1) |
| Range Sum | O(log n) | O(1) |

```java
/**
 * Fenwick Tree (Binary Indexed Tree) for prefix sums.
 * More space-efficient than segment tree.
 */
public class FenwickTree {
    
    private final long[] bit;
    private final int n;
    
    public FenwickTree(int n) {
        this.n = n;
        this.bit = new long[n + 1]; // 1-indexed
    }
    
    public FenwickTree(int[] arr) {
        this(arr.length);
        for (var i = 0; i < arr.length; i++) {
            add(i + 1, arr[i]);
        }
    }
    
    /**
     * Add value at index (1-indexed). O(log n) time.
     */
    public void add(int index, int delta) {
        while (index <= n) {
            bit[index] += delta;
            index += index & (-index); // Move to parent
        }
    }
    
    /**
     * Get prefix sum [1..index]. O(log n) time.
     */
    public long prefixSum(int index) {
        var sum = 0L;
        while (index > 0) {
            sum += bit[index];
            index -= index & (-index); // Move to parent
        }
        return sum;
    }
    
    /**
     * Get range sum [l..r]. O(log n) time.
     */
    public long rangeSum(int l, int r) {
        return prefixSum(r) - prefixSum(l - 1);
    }
    
    /**
     * Update element at index (0-indexed). O(log n) time.
     */
    public void update(int index, int value) {
        var current = rangeSum(index + 1, index + 1);
        add(index + 1, value - (int) current);
    }
}
```

**Key Points:**
- Uses `i & (-i)` to isolate lowest set bit
- 1-indexed for simpler bit manipulation
- More cache-friendly than segment tree
- Can be extended for 2D range queries

---

*Continue with remaining sections...*

## Section F: Trie and Suffix Structures

---

### F.1 Trie (Prefix Tree)

**Concept:** Tree where each node represents a character. Used for prefix-based operations.

**Visual (words: "cat", "car", "dog"):**
```
       ROOT
      /    \
    [c]    [d]
    |       |
    [a]    [o]
   /   \     |
 [t*]  [r*] [g*]
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Insert | O(L) | O(L) |
| Search | O(L) | O(1) |
| Prefix Search | O(P) | O(1) |

```java
/**
 * Trie (Prefix Tree) implementation.
 * Efficient for prefix-based string operations.
 */
public class Trie {
    
    private static class TrieNode {
        Map<Character, TrieNode> children;
        boolean isEndOfWord;
        int prefixCount; // Number of words with this prefix
        
        TrieNode() {
            this.children = new HashMap<>();
            this.isEndOfWord = false;
            this.prefixCount = 0;
        }
    }
    
    private final TrieNode root;
    private int size;
    
    public Trie() {
        this.root = new TrieNode();
        this.size = 0;
    }
    
    /**
     * Insert word into trie. O(L) time.
     */
    public void insert(String word) {
        var node = root;
        for (var ch : word.toCharArray()) {
            node = node.children.computeIfAbsent(ch, k -> new TrieNode());
            node.prefixCount++;
        }
        if (!node.isEndOfWord) {
            node.isEndOfWord = true;
            size++;
        }
    }
    
    /**
     * Search for exact word. O(L) time.
     */
    public boolean search(String word) {
        var node = findNode(word);
        return node != null && node.isEndOfWord;
    }
    
    /**
     * Check if any word starts with prefix. O(P) time.
     */
    public boolean startsWith(String prefix) {
        return findNode(prefix) != null;
    }
    
    /**
     * Count words with given prefix. O(P) time.
     */
    public int countWordsWithPrefix(String prefix) {
        var node = findNode(prefix);
        return node == null ? 0 : node.prefixCount;
    }
    
    private TrieNode findNode(String str) {
        var node = root;
        for (var ch : str.toCharArray()) {
            node = node.children.get(ch);
            if (node == null) return null;
        }
        return node;
    }
    
    /**
     * Delete word from trie. O(L) time.
     */
    public boolean delete(String word) {
        return delete(root, word, 0);
    }
    
    private boolean delete(TrieNode node, String word, int index) {
        if (index == word.length()) {
            if (!node.isEndOfWord) return false;
            node.isEndOfWord = false;
            size--;
            return node.children.isEmpty();
        }
        
        var ch = word.charAt(index);
        var child = node.children.get(ch);
        if (child == null) return false;
        
        var shouldDeleteChild = delete(child, word, index + 1);
        
        if (shouldDeleteChild) {
            node.children.remove(ch);
            return node.children.isEmpty() && !node.isEndOfWord;
        }
        
        return false;
    }
    
    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
}
```

**Key Points:**
- O(L) operations where L = word length
- Can store additional info (frequency, index)
- Used in autocomplete, spell checkers, IP routing
- Space-optimized with compressed trie

---

*Continue with remaining implementations...*

## Section I: Caches

---

### I.1 LRU Cache

**Concept:** Evicts least recently accessed item when full. Uses HashMap + Doubly Linked List.

**Visual:**
```
HashMap:          Doubly Linked List (MRU -> LRU):
key1 -> Node     head -> [key1] <-> [key2] <-> [key3] -> tail
key2 -> Node
key3 -> Node
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Get | O(1) | O(1) |
| Put | O(1) | O(1) |

```java
/**
 * LRU (Least Recently Used) Cache implementation.
 * Uses HashMap for O(1) lookup and Doubly Linked List for O(1) eviction.
 */
public class LRUCache<K, V> {
    
    private final int capacity;
    private final Map<K, Node> cache;
    private final DoublyLinkedList<K, V> list;
    
    private record Node<K, V>(K key, V value) {}
    
    public LRUCache(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive");
        }
        this.capacity = capacity;
        this.cache = new HashMap<>();
        this.list = new DoublyLinkedList<>();
    }
    
    /**
     * Get value by key. O(1) time.
     */
    public V get(K key) {
        if (!cache.containsKey(key)) {
            return null;
        }
        
        // Move to front (most recently used)
        var node = cache.get(key);
        list.remove(node);
        list.addFirst(node);
        
        return node.value();
    }
    
    /**
     * Put key-value pair. O(1) time.
     */
    public void put(K key, V value) {
        if (cache.containsKey(key)) {
            // Update existing
            var node = cache.get(key);
            list.remove(node);
        } else if (cache.size() >= capacity) {
            // Evict least recently used
            var lru = list.removeLast();
            cache.remove(lru.key());
        }
        
        var newNode = new Node<>(key, value);
        list.addFirst(newNode);
        cache.put(key, newNode);
    }
    
    public int size() { return cache.size(); }
    public boolean isEmpty() { return cache.isEmpty(); }
    public boolean containsKey(K key) { return cache.containsKey(key); }
}
```

**Key Points:**
- HashMap provides O(1) key lookup
- Doubly Linked List maintains access order
- Move accessed nodes to front
- Remove from tail when evicting

---

### I.2 LFU Cache

**Concept:** Evicts least frequently accessed item. Uses two HashMaps + LinkedHashSet per frequency.

**Visual:**
```
Key -> Node: {key, value, freq}

Freq -> LinkedHashSet of Keys:
1: {key2, key3}  (accessed 1 time)
2: {key1}        (accessed 2 times)
3: {key4}        (accessed 3 times)
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Get | O(1) | O(1) |
| Put | O(1) | O(1) |

```java
/**
 * LFU (Least Frequently Used) Cache implementation.
 * Evicts based on access frequency, ties broken by recency.
 */
public class LFUCache<K, V> {
    
    private final int capacity;
    private int minFreq;
    private final Map<K, Node> keyNodeMap;
    private final Map<Integer, LinkedHashSet<K>> freqKeysMap;
    
    private record Node<K, V>(K key, V value, int freq) {}
    
    public LFUCache(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive");
        }
        this.capacity = capacity;
        this.minFreq = 0;
        this.keyNodeMap = new HashMap<>();
        this.freqKeysMap = new HashMap<>();
    }
    
    /**
     * Get value and increment frequency. O(1) time.
     */
    public V get(K key) {
        if (!keyNodeMap.containsKey(key)) {
            return null;
        }
        
        var node = keyNodeMap.get(key);
        updateFrequency(key, node);
        
        return node.value();
    }
    
    /**
     * Put key-value pair. O(1) time.
     */
    public void put(K key, V value) {
        if (keyNodeMap.containsKey(key)) {
            // Update existing
            var node = keyNodeMap.get(key);
            updateFrequency(key, node);
            keyNodeMap.put(key, new Node<>(key, value, node.freq()));
            return;
        }
        
        // Evict if necessary
        if (keyNodeMap.size() >= capacity) {
            evictLFU();
        }
        
        // Add new entry with frequency 1
        var newNode = new Node<>(key, value, 1);
        keyNodeMap.put(key, newNode);
        freqKeysMap.computeIfAbsent(1, k -> new LinkedHashSet<>()).add(key);
        minFreq = 1;
    }
    
    private void updateFrequency(K key, Node<K, V> node) {
        var freq = node.freq();
        
        // Remove from old frequency set
        var keys = freqKeysMap.get(freq);
        keys.remove(key);
        if (keys.isEmpty() && freq == minFreq) {
            minFreq++;
        }
        
        // Add to new frequency set
        var newFreq = freq + 1;
        freqKeysMap.computeIfAbsent(newFreq, k -> new LinkedHashSet<>()).add(key);
        
        // Update node
        keyNodeMap.put(key, new Node<>(key, node.value(), newFreq));
    }
    
    private void evictLFU() {
        var keys = freqKeysMap.get(minFreq);
        var evictKey = keys.iterator().next(); // Oldest in set
        keys.remove(evictKey);
        keyNodeMap.remove(evictKey);
        
        if (keys.isEmpty()) {
            freqKeysMap.remove(minFreq);
        }
    }
    
    public int size() { return keyNodeMap.size(); }
    public boolean isEmpty() { return keyNodeMap.isEmpty(); }
}
```

**Key Points:**
- Tracks access frequency for each key
- Multiple keys can have same frequency
- Eviction: lowest frequency, oldest if tie
- Used in database query caches, CDN edge caches

---

## Section H: Union-Find

---

### H.1 Union-Find (DSU)

**Concept:** Tracks disjoint sets with path compression and union by rank.

**Visual:**
```
Before union(1, 4):
1 -> 2 -> 3     4 -> 5

After union:
1 -> 2 -> 3
      |
      4 -> 5
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Find | O(α(n)) | O(1) |
| Union | O(α(n)) | O(1) |

```java
/**
 * Union-Find (Disjoint Set Union) with path compression and union by rank.
 * α(n) is inverse Ackermann, effectively O(1).
 */
public class UnionFind {
    
    private final int[] parent;
    private final int[] rank;
    private final int[] size;
    private int count; // Number of components
    
    public UnionFind(int n) {
        this.parent = new int[n];
        this.rank = new int[n];
        this.size = new int[n];
        this.count = n;
        
        for (var i = 0; i < n; i++) {
            parent[i] = i;
            size[i] = 1;
        }
    }
    
    /**
     * Find root of element with path compression. O(α(n)) time.
     */
    public int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]); // Path compression
        }
        return parent[x];
    }
    
    /**
     * Union two sets by rank. O(α(n)) time.
     */
    public boolean union(int x, int y) {
        var rootX = find(x);
        var rootY = find(y);
        
        if (rootX == rootY) return false; // Already connected
        
        // Union by rank
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
            size[rootY] += size[rootX];
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
            size[rootX] += size[rootY];
        } else {
            parent[rootY] = rootX;
            size[rootX] += size[rootY];
            rank[rootX]++;
        }
        
        count--;
        return true;
    }
    
    /**
     * Check if two elements are in same set.
     */
    public boolean isConnected(int x, int y) {
        return find(x) == find(y);
    }
    
    /**
     * Get size of component containing element.
     */
    public int componentSize(int x) {
        return size[find(x)];
    }
    
    public int count() { return count; }
}
```

**Key Points:**
- Path compression flattens tree structure
- Union by rank keeps tree shallow
- Used in Kruskal's MST, cycle detection, connected components
- α(n) < 5 for all practical n

---

## Section G: Graph Representations

---

### G.2 Graph (Adjacency List)

**Concept:** Most common graph representation using HashMap of adjacency lists.

**Visual:**
```
0: [1, 2]
1: [0, 3]
2: [0, 3]
3: [1, 2]

Graph:
0 --- 1
|  &#92;   |
2 --- 3
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Add vertex | O(1) | O(1) |
| Add edge | O(1) | O(1) |
| Remove edge | O(degree) | O(1) |
| Adjacent check | O(degree) | O(1) |
| Space | O(V + E) | - |

```java
/**
 * Graph implemented with adjacency list.
 * Most space-efficient for sparse graphs.
 */
public class Graph<T> {
    
    private final Map<T, List<T>> adjacencyList;
    private final boolean directed;
    private int edgeCount;
    
    public Graph() {
        this(false);
    }
    
    public Graph(boolean directed) {
        this.adjacencyList = new HashMap<>();
        this.directed = directed;
        this.edgeCount = 0;
    }
    
    /**
     * Add vertex to graph. O(1) time.
     */
    public void addVertex(T vertex) {
        adjacencyList.computeIfAbsent(vertex, k -> new ArrayList<>());
    }
    
    /**
     * Add edge between vertices. O(1) time.
     */
    public void addEdge(T from, T to) {
        addVertex(from);
        addVertex(to);
        
        adjacencyList.get(from).add(to);
        edgeCount++;
        
        if (!directed) {
            adjacencyList.get(to).add(from);
        }
    }
    
    /**
     * Get all neighbors of vertex. O(1) time.
     */
    public List<T> getNeighbors(T vertex) {
        return adjacencyList.getOrDefault(vertex, Collections.emptyList());
    }
    
    /**
     * Check if edge exists. O(degree) time.
     */
    public boolean hasEdge(T from, T to) {
        return adjacencyList.containsKey(from) && 
               adjacencyList.get(from).contains(to);
    }
    
    /**
     * Remove edge. O(degree) time.
     */
    public void removeEdge(T from, T to) {
        if (!adjacencyList.containsKey(from)) return;
        
        adjacencyList.get(from).remove(to);
        edgeCount--;
        
        if (!directed && adjacencyList.containsKey(to)) {
            adjacencyList.get(to).remove(from);
        }
    }
    
    /**
     * BFS traversal from start vertex.
     */
    public List<T> bfs(T start) {
        var result = new ArrayList<T>();
        var visited = new HashSet<T>();
        var queue = new ArrayDeque<T>();
        
        queue.offer(start);
        visited.add(start);
        
        while (!queue.isEmpty()) {
            var current = queue.poll();
            result.add(current);
            
            for (var neighbor : getNeighbors(current)) {
                if (visited.add(neighbor)) {
                    queue.offer(neighbor);
                }
            }
        }
        
        return result;
    }
    
    /**
     * DFS traversal from start vertex.
     */
    public List<T> dfs(T start) {
        var result = new ArrayList<T>();
        var visited = new HashSet<T>();
        dfsHelper(start, visited, result);
        return result;
    }
    
    private void dfsHelper(T vertex, Set<T> visited, List<T> result) {
        visited.add(vertex);
        result.add(vertex);
        
        for (var neighbor : getNeighbors(vertex)) {
            if (!visited.contains(neighbor)) {
                dfsHelper(neighbor, visited, result);
            }
        }
    }
    
    public int vertexCount() { return adjacencyList.size(); }
    public int edgeCount() { return edgeCount; }
    public boolean isEmpty() { return adjacencyList.isEmpty(); }
    public Set<T> vertices() { return new HashSet<>(adjacencyList.keySet()); }
}
```

**Key Points:**
- Most common graph representation
- Space-efficient for sparse graphs
- Easy to iterate over neighbors
- Can store edge weights with `Map<T, Map<T, Integer>>`

---

*Continue with remaining implementations...*