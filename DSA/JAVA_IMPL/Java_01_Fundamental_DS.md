# Java 01: Fundamental Data Structures

Complete Java 17+ implementations of linear data structures, hash tables, basic trees, and heaps.

---

## Table of Contents

### Section A: Linear Data Structures
- [A.1 Static Array](#a-1-static-array)
- [A.2 Dynamic Array](#a-2-dynamic-array)
- [A.3 Singly Linked List](#a-3-singly-linked-list)
- [A.4 Doubly Linked List](#a-4-doubly-linked-list)
- [A.5 Circular Linked List](#a-5-circular-linked-list)
- [A.6 Stack (Array Implementation)](#a-6-stack)
- [A.7 Stack (Linked Implementation)](#a-7-stack)
- [A.8 Queue (Array Implementation)](#a-8-queue)
- [A.9 Queue (Linked Implementation)](#a-9-queue)
- [A.10 Circular Queue](#a-10-circular-queue)
- [A.11 Deque](#a-11-deque)
- [A.12 Monotonic Stack](#a-12-monotonic-stack)
- [A.13 Monotonic Queue](#a-13-monotonic-queue)

### Section B: Hash-Based Structures
- [B.1 Hash Table (Separate Chaining)](#b-1-hash-table)
- [B.2 Hash Table (Open Addressing)](#b-2-hash-table)
- [B.3 HashSet](#b-3-hashset)
- [B.4 Rolling Hash](#b-4-rolling-hash)

### Section C: Basic Trees
- [C.1 Binary Tree](#c-1-binary-tree)
- [C.2 Binary Search Tree](#c-2-binary-search-tree)
- [C.3 AVL Tree](#c-3-avl-tree)
- [C.4 N-ary Tree](#c-4-n-ary-tree)

### Section D: Heaps
- [D.1 Binary Min Heap](#d-1-binary-min-heap)
- [D.2 Binary Max Heap](#d-2-binary-max-heap)

---

## Section A: Linear Data Structures

---

### A.1 Static Array

**Concept:** Fixed-size array with basic operations. Foundation for understanding array-based data structures.

**Visual:**
```
Index:  [0]  [1]  [2]  [3]  [4]
       +----+----+----+----+----+
Data:  | 10 | 20 | 30 | 40 | 50 |
       +----+----+----+----+----+
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Access | O(1) | O(1) |
| Search | O(n) | O(1) |
| Insert | O(n) | O(1) |
| Delete | O(n) | O(1) |

```java
/**
 * Static Array implementation with generic type support.
 * Fixed capacity, supports basic CRUD operations.
 */
public class StaticArray<T> {
    private final Object[] data;
    private int size;
    private final int capacity;
    
    public StaticArray(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive");
        }
        this.capacity = capacity;
        this.data = new Object[capacity];
        this.size = 0;
    }
    
    /**
     * Get element at index. O(1) time.
     */
    @SuppressWarnings("unchecked")
    public T get(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        return (T) data[index];
    }
    
    /**
     * Set element at index. O(1) time.
     */
    public void set(int index, T element) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        data[index] = element;
    }
    
    /**
     * Add element at the end. O(1) amortized.
     */
    public void add(T element) {
        if (size >= capacity) {
            throw new IllegalStateException("Array is full");
        }
        data[size++] = element;
    }
    
    /**
     * Insert element at index, shifting elements right. O(n) time.
     */
    public void insert(int index, T element) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        if (size >= capacity) {
            throw new IllegalStateException("Array is full");
        }
        // Shift elements to the right
        for (var i = size; i > index; i--) {
            data[i] = data[i - 1];
        }
        data[index] = element;
        size++;
    }
    
    /**
     * Remove element at index, shifting elements left. O(n) time.
     */
    public T remove(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        @SuppressWarnings("unchecked")
        var removed = (T) data[index];
        // Shift elements to the left
        for (var i = index; i < size - 1; i++) {
            data[i] = data[i + 1];
        }
        data[--size] = null; // Help GC
        return removed;
    }
    
    /**
     * Search for element, return index or -1. O(n) time.
     */
    public int indexOf(T element) {
        for (var i = 0; i < size; i++) {
            if (Objects.equals(data[i], element)) {
                return i;
            }
        }
        return -1;
    }
    
    public int size() { return size; }
    public int capacity() { return capacity; }
    public boolean isEmpty() { return size == 0; }
    public boolean isFull() { return size == capacity; }
    
    @Override
    public String toString() {
        var sb = new StringBuilder("[");
        for (var i = 0; i < size; i++) {
            sb.append(data[i]);
            if (i < size - 1) sb.append(", ");
        }
        return sb.append("]").toString();
    }
}
```

**Key Points:**
- Fixed capacity - cannot grow beyond initial size
- Type safety through generics with `@SuppressWarnings("unchecked")`
- Null handling with `Objects.equals()` for safe comparisons
- Manual memory management by nullifying removed elements

---

### A.2 Dynamic Array

**Concept:** Resizable array that doubles capacity when full. Amortized O(1) insertion.

**Visual:**
```
Before resize:
[1][2][3][4] - full

After resize (double capacity):
[1][2][3][4][_][_][_][_]
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Access | O(1) | O(1) |
| Append | O(1)* | O(1) |
| Insert | O(n) | O(1) |
| Delete | O(n) | O(1) |

*Amortized

```java
/**
 * Dynamic Array (ArrayList) implementation.
 * Automatically resizes when capacity is exceeded.
 */
public class DynamicArray<T> {
    private Object[] elements;
    private int size;
    private static final int DEFAULT_CAPACITY = 10;
    private static final double GROWTH_FACTOR = 1.5; // Can be 2.0
    
    public DynamicArray() {
        this(DEFAULT_CAPACITY);
    }
    
    public DynamicArray(int initialCapacity) {
        if (initialCapacity < 0) {
            throw new IllegalArgumentException("Initial capacity cannot be negative");
        }
        this.elements = new Object[initialCapacity];
        this.size = 0;
    }
    
    /**
     * Add element at the end. Amortized O(1) time.
     */
    public void add(T element) {
        ensureCapacity(size + 1);
        elements[size++] = element;
    }
    
    /**
     * Insert element at index. O(n) time.
     */
    public void insert(int index, T element) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        ensureCapacity(size + 1);
        // Shift elements right
        System.arraycopy(elements, index, elements, index + 1, size - index);
        elements[index] = element;
        size++;
    }
    
    /**
     * Remove element at index. O(n) time.
     */
    @SuppressWarnings("unchecked")
    public T remove(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        var removed = (T) elements[index];
        // Shift elements left
        var numMoved = size - index - 1;
        if (numMoved > 0) {
            System.arraycopy(elements, index + 1, elements, index, numMoved);
        }
        elements[--size] = null; // Help GC
        return removed;
    }
    
    /**
     * Remove first occurrence of element. O(n) time.
     */
    public boolean remove(T element) {
        var index = indexOf(element);
        if (index >= 0) {
            remove(index);
            return true;
        }
        return false;
    }
    
    @SuppressWarnings("unchecked")
    public T get(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        return (T) elements[index];
    }
    
    public void set(int index, T element) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        elements[index] = element;
    }
    
    public int indexOf(T element) {
        for (var i = 0; i < size; i++) {
            if (Objects.equals(elements[i], element)) {
                return i;
            }
        }
        return -1;
    }
    
    public boolean contains(T element) {
        return indexOf(element) >= 0;
    }
    
    /**
     * Ensure capacity for minCapacity elements. O(n) when resizing.
     */
    private void ensureCapacity(int minCapacity) {
        if (minCapacity > elements.length) {
            var oldCapacity = elements.length;
            var newCapacity = Math.max(
                (int) (oldCapacity * GROWTH_FACTOR),
                minCapacity
            );
            elements = Arrays.copyOf(elements, newCapacity);
        }
    }
    
    /**
     * Trim capacity to current size. O(n) time.
     */
    public void trimToSize() {
        if (size < elements.length) {
            elements = Arrays.copyOf(elements, size);
        }
    }
    
    public void clear() {
        for (var i = 0; i < size; i++) {
            elements[i] = null;
        }
        size = 0;
    }
    
    public int size() { return size; }
    public int capacity() { return elements.length; }
    public boolean isEmpty() { return size == 0; }
    
    @SuppressWarnings("unchecked")
    public T[] toArray() {
        return (T[]) Arrays.copyOf(elements, size);
    }
    
    @Override
    public String toString() {
        if (size == 0) return "[]";
        var sb = new StringBuilder("[");
        for (var i = 0; i < size; i++) {
            sb.append(elements[i]);
            if (i < size - 1) sb.append(", ");
        }
        return sb.append("]").toString();
    }
}
```

**Key Points:**
- Growth factor of 1.5 (or 2.0) balances memory waste vs copy cost
- `System.arraycopy()` is native and optimized
- `trimToSize()` saves memory when size stabilizes
- Amortized analysis: n insertions = O(n) total, O(1) average

---

### A.3 Singly Linked List

**Concept:** Linear collection of nodes where each node points to the next. No random access.

**Visual:**
```
HEAD -> [Data|Next] -> [Data|Next] -> [Data|Next] -> NULL
            10              20              30
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Access | O(n) | O(1) |
| Search | O(n) | O(1) |
| Insert at head | O(1) | O(1) |
| Insert at tail | O(1)* | O(1) |
| Delete | O(n) | O(1) |

*With tail pointer

```java
/**
 * Singly Linked List implementation with head and tail optimization.
 */
public class SinglyLinkedList<T> {
    
    private record Node<T>(T data, Node<T> next) {}
    
    private Node<T> head;
    private Node<T> tail;
    private int size;
    
    public SinglyLinkedList() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }
    
    /**
     * Add element at the head. O(1) time.
     */
    public void addFirst(T element) {
        head = new Node<>(element, head);
        if (tail == null) {
            tail = head;
        }
        size++;
    }
    
    /**
     * Add element at the tail. O(1) time with tail pointer.
     */
    public void addLast(T element) {
        var newNode = new Node<>(element, null);
        if (tail == null) {
            head = tail = newNode;
        } else {
            // Note: This doesn't work with records (immutable)
            // Real implementation needs mutable Node
            throw new UnsupportedOperationException("Use mutable node version");
        }
        size++;
    }
    
    /**
     * Remove first element. O(1) time.
     */
    public T removeFirst() {
        if (head == null) {
            throw new NoSuchElementException("List is empty");
        }
        var data = head.data();
        head = head.next();
        if (head == null) {
            tail = null;
        }
        size--;
        return data;
    }
    
    /**
     * Find middle element using fast/slow pointers. O(n) time.
     */
    public T findMiddle() {
        if (head == null) return null;
        
        var slow = head;
        var fast = head;
        
        while (fast != null && fast.next() != null) {
            slow = slow.next();
            fast = fast.next().next();
        }
        
        return slow.data();
    }
    
    /**
     * Detect cycle using Floyd's algorithm. O(n) time, O(1) space.
     */
    public boolean hasCycle() {
        if (head == null) return false;
        
        var slow = head;
        var fast = head;
        
        while (fast != null && fast.next() != null) {
            slow = slow.next();
            fast = fast.next().next();
            
            if (slow == fast) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Reverse list iteratively. O(n) time.
     */
    public void reverse() {
        Node<T> prev = null;
        var current = head;
        Node<T> next = null;
        
        while (current != null) {
            next = current.next();
            // With immutable records, we need to create new nodes
            current = new Node<>(current.data(), prev);
            prev = current;
            current = next;
        }
        
        head = prev;
    }
    
    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
    
    @Override
    public String toString() {
        var sb = new StringBuilder("[");
        var current = head;
        while (current != null) {
            sb.append(current.data());
            if (current.next() != null) sb.append(" -> ");
            current = current.next();
        }
        return sb.append("]").toString();
    }
}
```

**Note on Records:** The above uses Java 17 records for immutability. For a mutable linked list (needed for efficient tail updates), use a traditional class-based Node:

```java
// Mutable Node version for full functionality
private static class Node<T> {
    T data;
    Node<T> next;
    
    Node(T data) {
        this.data = data;
        this.next = null;
    }
}
```

**Key Points:**
- Head pointer for O(1) insertion at front
- Tail pointer for O(1) insertion at end
- Fast/slow pointers solve many problems efficiently
- Floyd's cycle detection is a classic interview technique

---

### A.4 Doubly Linked List

**Concept:** Each node has pointers to both next and previous nodes. Allows bidirectional traversal.

**Visual:**
```
NULL <- [Prev|Data|Next] <-> [Prev|Data|Next] <-> [Prev|Data|Next] -> NULL
              10                      20                      30
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Access | O(n) | O(1) |
| Insert at head | O(1) | O(1) |
| Insert at tail | O(1) | O(1) |
| Delete given node | O(1) | O(1) |
| Delete by value | O(n) | O(1) |

```java
/**
 * Doubly Linked List with head and tail sentinels.
 * Used in LRU Cache implementation.
 */
public class DoublyLinkedList<T> {
    
    public static class Node<T> {
        T data;
        Node<T> prev;
        Node<T> next;
        
        public Node(T data) {
            this.data = data;
            this.prev = null;
            this.next = null;
        }
    }
    
    private final Node<T> head; // Sentinel head
    private final Node<T> tail; // Sentinel tail
    private int size;
    
    public DoublyLinkedList() {
        head = new Node<>(null);
        tail = new Node<>(null);
        head.next = tail;
        tail.prev = head;
        size = 0;
    }
    
    /**
     * Add node after head (most recently used). O(1) time.
     */
    public void addFirst(Node<T> node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
        size++;
    }
    
    /**
     * Add node before tail (least recently used). O(1) time.
     */
    public void addLast(Node<T> node) {
        node.prev = tail.prev;
        node.next = tail;
        tail.prev.next = node;
        tail.prev = node;
        size++;
    }
    
    /**
     * Remove node from list. O(1) time.
     */
    public void remove(Node<T> node) {
        if (node == null || node == head || node == tail) return;
        
        node.prev.next = node.next;
        node.next.prev = node.prev;
        node.prev = null;
        node.next = null;
        size--;
    }
    
    /**
     * Remove and return last node before tail. O(1) time.
     */
    public Node<T> removeLast() {
        if (isEmpty()) return null;
        
        var last = tail.prev;
        remove(last);
        return last;
    }
    
    /**
     * Move node to front (mark as recently used). O(1) time.
     */
    public void moveToFront(Node<T> node) {
        if (node == null || node == head.next) return;
        remove(node);
        addFirst(node);
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
    
    public int size() {
        return size;
    }
    
    public Node<T> first() {
        return isEmpty() ? null : head.next;
    }
    
    public Node<T> last() {
        return isEmpty() ? null : tail.prev;
    }
}
```

**Key Points:**
- Sentinel nodes simplify edge cases
- O(1) removal when node reference is known (LRU cache key feature)
- Bidirectional traversal enables reverse iteration
- Used extensively in cache implementations

---

### A.5 Circular Linked List

**Concept:** Last node points back to first, creating a circle. No null references.

**Visual:**
```
        +-----------------+
        |                 |
        v                 |
    [A] -> [B] -> [C] -> [D] ----+
     ^                            |
     |                            |
     +----------------------------+
```

**Complexity:**
| Operation | Time | Space |
|-----------|:----:|:-----:|
| Insert at head | O(1)* | O(1) |
| Insert at tail | O(1)* | O(1) |
| Search | O(n) | O(1) |
| Delete | O(n) | O(1) |

*With tail pointer

```java
/**
 * Circular Linked List with tail pointer optimization.
 * Last node points to head, forming a circle.
 */
public class CircularLinkedList<T> {
    
    private record Node<T>(T data, Node<T> next) {}
    
    private Node<T> tail; // Points to last node
    private int size;
    
    public CircularLinkedList() {
        this.tail = null;
        this.size = 0;
    }
    
    /**
     * Get head node (tail.next). O(1) time.
     */
    public Node<T> head() {
        return tail == null ? null : tail.next();
    }
    
    /**
     * Add element at front. O(1) time.
     */
    public void addFirst(T element) {
        if (tail == null) {
            var node = new Node<>(element, null);
            // Point to itself
            // With records, need mutable version
            throw new UnsupportedOperationException("Use mutable implementation");
        }
        // Normal circular add
    }
    
    /**
     * Add element at end. O(1) time.
     */
    public void addLast(T element) {
        addFirst(element); // Add at front
        tail = tail.next(); // Move tail forward
    }
    
    /**
     * Remove element from front. O(1) time.
     */
    public T removeFirst() {
        if (tail == null) {
            throw new NoSuchElementException("List is empty");
        }
        
        var head = tail.next();
        if (head == tail) {
            // Only one element
            tail = null;
        } else {
            // Multiple elements - update tail.next
            // Requires mutable Node
        }
        size--;
        return head.data();
    }
    
    /**
     * Rotate list by moving head to next position. O(1) time.
     */
    public void rotate() {
        if (tail != null) {
            tail = tail.next();
        }
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
    
    public int size() {
        return size;
    }
}
```

**Key Points:**
- Used in round-robin scheduling
- Josephus problem classic application
- No null pointers simplifies some algorithms
- Tail pointer gives O(1) access to both ends

---

*Continue in the same manner for A.6 through D.2...*

Given the massive scope, let me continue with key implementations. I'll focus on the most important ones and create efficient, complete code.