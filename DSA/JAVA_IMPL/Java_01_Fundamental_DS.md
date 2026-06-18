# Java 01: Fundamental Data Structures

Complete Java 17+ implementations of linear data structures, hash tables, basic trees, and heaps.

---

## Table of Contents

### Section A: Linear Data Structures
- [A.1 Static Array](#a1-static-array)
- [A.2 Dynamic Array](#a2-dynamic-array)
- [A.3 Singly Linked List](#a3-singly-linked-list)
- [A.4 Doubly Linked List](#a4-doubly-linked-list)
- [A.5 Circular Linked List](#a5-circular-linked-list)
- [A.6 Stack (Array Implementation)](#a6-stack-array-implementation)
- [A.7 Stack (Linked Implementation)](#a7-stack-linked-implementation)
- [A.8 Queue (Array Implementation)](#a8-queue-array-implementation)
- [A.9 Queue (Linked Implementation)](#a9-queue-linked-implementation)
- [A.10 Circular Queue](#a10-circular-queue)
- [A.11 Deque](#a11-deque)
- [A.12 Monotonic Stack](#a12-monotonic-stack)
- [A.13 Monotonic Queue](#a13-monotonic-queue)

### Section B: Hash-Based Structures
- [B.1 Hash Table (Separate Chaining)](#b1-hash-table-separate-chaining)
- [B.2 Hash Table (Open Addressing)](#b2-hash-table-open-addressing)
- [B.3 HashSet](#b3-hashset)
- [B.4 Rolling Hash](#b4-rolling-hash)

### Section C: Basic Trees
- [C.1 Binary Tree](#c1-binary-tree)
- [C.2 Binary Search Tree](#c2-binary-search-tree)
- [C.3 AVL Tree](#c3-avl-tree)
- [C.4 N-ary Tree](#c4-n-ary-tree)

### Section D: Heaps
- [D.1 Binary Min Heap](#d1-binary-min-heap)
- [D.2 Binary Max Heap](#d2-binary-max-heap)

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
    private static final class Node<T> {
        T data;
        Node<T> next;
        Node(T data) { this.data = data; }
    }

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
        var node = new Node<>(element);
        node.next = head;
        head = node;
        if (tail == null) {
            tail = head;
        }
        size++;
    }
    
    /**
     * Add element at the tail. O(1) time with tail pointer.
     */
    public void addLast(T element) {
        var newNode = new Node<>(element);
        if (tail == null) {
            head = tail = newNode;
        } else {
            tail.next = newNode;
            tail = newNode;
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
        var data = head.data;
        head = head.next;
        if (head == null) {
            tail = null;
        }
        size--;
        return data;
    }

    /**
     * Remove last element. O(n) time for singly linked list.
     */
    public T removeLast() {
        if (head == null) {
            throw new NoSuchElementException("List is empty");
        }
        if (head == tail) {
            var data = head.data;
            head = tail = null;
            size = 0;
            return data;
        }
        var cur = head;
        while (cur.next != tail) cur = cur.next;
        var data = tail.data;
        cur.next = null;
        tail = cur;
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
        
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        
        return slow.data;
    }
    
    /**
     * Detect cycle using Floyd's algorithm. O(n) time, O(1) space.
     */
    public boolean hasCycle() {
        if (head == null) return false;
        
        var slow = head;
        var fast = head;
        
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            
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
        var cur = head;
        tail = head;
        while (cur != null) {
            var nxt = cur.next;
            cur.next = prev;
            prev = cur;
            cur = nxt;
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
            sb.append(current.data);
            if (current.next != null) sb.append(" -> ");
            current = current.next;
        }
        return sb.append("]").toString();
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

    private static final class Node<T> {
        T data;
        Node<T> next;
        Node(T data) { this.data = data; }
    }

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
        return tail == null ? null : tail.next;
    }
    
    /**
     * Add element at front. O(1) time.
     */
    public void addFirst(T element) {
        if (tail == null) {
            var node = new Node<>(element);
            node.next = node;
            tail = node;
            size = 1;
            return;
        }
        var node = new Node<>(element);
        node.next = tail.next;
        tail.next = node;
        size++;
    }
    
    /**
     * Add element at end. O(1) time.
     */
    public void addLast(T element) {
        addFirst(element);
        tail = tail.next;
    }
    
    /**
     * Remove element from front. O(1) time.
     */
    public T removeFirst() {
        if (tail == null) {
            throw new NoSuchElementException("List is empty");
        }

        var head = tail.next;
        if (head == tail) {
            // Only one element
            tail = null;
            size = 0;
            return head.data;
        } else {
            tail.next = head.next;
        }
        size--;
        return head.data;
    }
    
    /**
     * Rotate list by moving head to next position. O(1) time.
     */
    public void rotate() {
        if (tail != null) {
            tail = tail.next;
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

### A.6 Stack (Array Implementation)

```java
import java.util.*;

public class ArrayStack {
    static final class IntStack {
        int[] a;
        int top;
        IntStack(int cap) { a = new int[Math.max(1, cap)]; }
        boolean isEmpty() { return top == 0; }
        int size() { return top; }
        void push(int x) {
            if (top == a.length) a = Arrays.copyOf(a, a.length << 1);
            a[top++] = x;
        }
        int peek() {
            if (top == 0) throw new NoSuchElementException();
            return a[top - 1];
        }
        int pop() {
            if (top == 0) throw new NoSuchElementException();
            return a[--top];
        }
        void clear() { top = 0; }
    }
}
```

---

### A.7 Stack (Linked Implementation)

```java
import java.util.*;

public class LinkedStack {
    static final class Stack<T> {
        static final class Node<T> {
            T v; Node<T> next;
            Node(T v, Node<T> next) { this.v = v; this.next = next; }
        }
        Node<T> head;
        int size;
        boolean isEmpty() { return size == 0; }
        void push(T x) { head = new Node<>(x, head); size++; }
        T peek() {
            if (head == null) throw new NoSuchElementException();
            return head.v;
        }
        T pop() {
            if (head == null) throw new NoSuchElementException();
            var v = head.v;
            head = head.next;
            size--;
            return v;
        }
    }
}
```

---

### A.8 Queue (Array Implementation)

```java
import java.util.*;

public class ArrayQueue {
    static final class IntQueue {
        int[] a;
        int head, tail, size;
        IntQueue(int cap) { a = new int[Math.max(1, cap)]; }
        boolean isEmpty() { return size == 0; }
        int size() { return size; }

        void offer(int x) {
            if (size == a.length) grow();
            a[tail] = x;
            tail = (tail + 1) % a.length;
            size++;
        }

        int peek() {
            if (size == 0) throw new NoSuchElementException();
            return a[head];
        }

        int poll() {
            if (size == 0) throw new NoSuchElementException();
            var v = a[head];
            head = (head + 1) % a.length;
            size--;
            return v;
        }

        private void grow() {
            var b = new int[a.length << 1];
            for (var i = 0; i < size; i++) b[i] = a[(head + i) % a.length];
            a = b;
            head = 0;
            tail = size;
        }
    }
}
```

---

### A.9 Queue (Linked Implementation)

```java
import java.util.*;

public class LinkedQueue {
    static final class Queue<T> {
        static final class Node<T> {
            T v; Node<T> next;
            Node(T v) { this.v = v; }
        }
        Node<T> head, tail;
        int size;
        boolean isEmpty() { return size == 0; }

        void offer(T x) {
            var n = new Node<>(x);
            if (tail == null) head = tail = n;
            else { tail.next = n; tail = n; }
            size++;
        }

        T peek() {
            if (head == null) throw new NoSuchElementException();
            return head.v;
        }

        T poll() {
            if (head == null) throw new NoSuchElementException();
            var v = head.v;
            head = head.next;
            if (head == null) tail = null;
            size--;
            return v;
        }
    }
}
```

---

### A.10 Circular Queue

```java
// Same as ArrayQueue.IntQueue (circular buffer); included as separate heading for navigation.
```

---

### A.11 Deque

```java
import java.util.*;

public class ArrayDequeImpl {
    static final class IntDeque {
        int[] a;
        int head, tail, size;
        IntDeque(int cap) { a = new int[Math.max(1, cap)]; }
        boolean isEmpty() { return size == 0; }
        int size() { return size; }

        void addFirst(int x) {
            if (size == a.length) grow();
            head = (head - 1 + a.length) % a.length;
            a[head] = x;
            size++;
        }

        void addLast(int x) {
            if (size == a.length) grow();
            a[tail] = x;
            tail = (tail + 1) % a.length;
            size++;
        }

        int peekFirst() {
            if (size == 0) throw new NoSuchElementException();
            return a[head];
        }

        int peekLast() {
            if (size == 0) throw new NoSuchElementException();
            return a[(tail - 1 + a.length) % a.length];
        }

        int removeFirst() {
            if (size == 0) throw new NoSuchElementException();
            var v = a[head];
            head = (head + 1) % a.length;
            size--;
            return v;
        }

        int removeLast() {
            if (size == 0) throw new NoSuchElementException();
            tail = (tail - 1 + a.length) % a.length;
            var v = a[tail];
            size--;
            return v;
        }

        private void grow() {
            var b = new int[a.length << 1];
            for (var i = 0; i < size; i++) b[i] = a[(head + i) % a.length];
            a = b;
            head = 0;
            tail = size;
        }
    }
}
```

---

### A.12 Monotonic Stack

```java
import java.util.*;

public class MonotonicStack {
    // Next greater element to the right; -1 if none.
    public static int[] nextGreaterRight(int[] a) {
        var n = a.length;
        var res = new int[n];
        Arrays.fill(res, -1);
        var st = new int[n];
        var top = 0;
        for (var i = n - 1; i >= 0; i--) {
            while (top > 0 && a[st[top - 1]] <= a[i]) top--;
            res[i] = (top == 0) ? -1 : a[st[top - 1]];
            st[top++] = i;
        }
        return res;
    }

    // Next smaller element to the right; -1 if none.
    public static int[] nextSmallerRight(int[] a) {
        var n = a.length;
        var res = new int[n];
        Arrays.fill(res, -1);
        var st = new int[n];
        var top = 0;
        for (var i = n - 1; i >= 0; i--) {
            while (top > 0 && a[st[top - 1]] >= a[i]) top--;
            res[i] = (top == 0) ? -1 : a[st[top - 1]];
            st[top++] = i;
        }
        return res;
    }
}
```

---

### A.13 Monotonic Queue

```java
import java.util.*;

public class MonotonicQueue {
    // Sliding window maximum in O(n).
    public static int[] slidingWindowMax(int[] a, int k) {
        var n = a.length;
        if (k <= 0 || k > n) throw new IllegalArgumentException();
        var res = new int[n - k + 1];
        var dq = new ArrayDeque<Integer>(); // store indices, values decreasing
        for (var i = 0; i < n; i++) {
            while (!dq.isEmpty() && dq.peekFirst() <= i - k) dq.pollFirst();
            while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();
            dq.addLast(i);
            if (i >= k - 1) res[i - k + 1] = a[dq.peekFirst()];
        }
        return res;
    }
}
```

---

## Section B: Hash-Based Structures

---

### B.1 Hash Table (Separate Chaining)

```java
import java.util.*;

public class HashTableChaining {
    static final class IntIntMap {
        static final class Node {
            int k, v;
            Node next;
            Node(int k, int v, Node next) { this.k = k; this.v = v; this.next = next; }
        }

        Node[] buckets;
        int size;
        int mask;

        IntIntMap(int capPow2) {
            var cap = 1;
            while (cap < capPow2) cap <<= 1;
            buckets = new Node[cap];
            mask = cap - 1;
        }

        private int idx(int key) {
            var h = key * 0x9E3779B9;
            return h & mask;
        }

        Integer get(int key) {
            for (var n = buckets[idx(key)]; n != null; n = n.next) {
                if (n.k == key) return n.v;
            }
            return null;
        }

        void put(int key, int val) {
            var i = idx(key);
            for (var n = buckets[i]; n != null; n = n.next) {
                if (n.k == key) { n.v = val; return; }
            }
            buckets[i] = new Node(key, val, buckets[i]);
            if (++size * 2 > buckets.length) rehash();
        }

        boolean remove(int key) {
            var i = idx(key);
            Node prev = null;
            for (var n = buckets[i]; n != null; ) {
                if (n.k == key) {
                    if (prev == null) buckets[i] = n.next;
                    else prev.next = n.next;
                    size--;
                    return true;
                }
                prev = n;
                n = n.next;
            }
            return false;
        }

        private void rehash() {
            var old = buckets;
            buckets = new Node[old.length << 1];
            mask = buckets.length - 1;
            size = 0;
            for (var head : old) {
                for (var n = head; n != null; n = n.next) put(n.k, n.v);
            }
        }
    }
}
```

---

### B.2 Hash Table (Open Addressing)

```java
import java.util.*;

public class HashTableOpenAddressing {
    static final class IntIntMap {
        static final int EMPTY = Integer.MIN_VALUE;
        static final int DELETED = Integer.MIN_VALUE + 1;
        int[] keys;
        int[] vals;
        int size;
        int used;
        int mask;

        IntIntMap(int capPow2) {
            var cap = 1;
            while (cap < capPow2) cap <<= 1;
            keys = new int[cap];
            vals = new int[cap];
            Arrays.fill(keys, EMPTY);
            mask = cap - 1;
        }

        private int h(int k) {
            var x = k * 0x9E3779B9;
            return x & mask;
        }

        Integer get(int k) {
            for (int i = h(k), step = 0; step <= mask; step++, i = (i + 1) & mask) {
                var kk = keys[i];
                if (kk == EMPTY) return null;
                if (kk == k) return vals[i];
            }
            return null;
        }

        void put(int k, int v) {
            if ((used + 1) * 2 > keys.length) rehash();
            var i = h(k);
            var firstDel = -1;
            for (;;) {
                var kk = keys[i];
                if (kk == EMPTY) {
                    if (firstDel != -1) i = firstDel;
                    keys[i] = k;
                    vals[i] = v;
                    size++;
                    used++;
                    return;
                }
                if (kk == DELETED) {
                    if (firstDel == -1) firstDel = i;
                } else if (kk == k) {
                    vals[i] = v;
                    return;
                }
                i = (i + 1) & mask;
            }
        }

        boolean remove(int k) {
            var i = h(k);
            for (;;) {
                var kk = keys[i];
                if (kk == EMPTY) return false;
                if (kk == k) {
                    keys[i] = DELETED;
                    size--;
                    return true;
                }
                i = (i + 1) & mask;
            }
        }

        private void rehash() {
            var oldK = keys;
            var oldV = vals;
            keys = new int[oldK.length << 1];
            vals = new int[oldV.length << 1];
            Arrays.fill(keys, EMPTY);
            mask = keys.length - 1;
            size = 0;
            used = 0;
            for (var i = 0; i < oldK.length; i++) {
                var k = oldK[i];
                if (k != EMPTY && k != DELETED) put(k, oldV[i]);
            }
        }
    }
}
```

---

### B.3 HashSet

```java
import java.util.*;

public class IntHashSet {
    static final int EMPTY = Integer.MIN_VALUE;
    static final int DELETED = Integer.MIN_VALUE + 1;
    int[] keys;
    int size;
    int used;
    int mask;

    public IntHashSet(int capPow2) {
        var cap = 1;
        while (cap < capPow2) cap <<= 1;
        keys = new int[cap];
        Arrays.fill(keys, EMPTY);
        mask = cap - 1;
    }

    private int h(int k) {
        var x = k * 0x9E3779B9;
        return x & mask;
    }

    public boolean contains(int k) {
        for (int i = h(k), step = 0; step <= mask; step++, i = (i + 1) & mask) {
            var kk = keys[i];
            if (kk == EMPTY) return false;
            if (kk == k) return true;
        }
        return false;
    }

    public boolean add(int k) {
        if ((used + 1) * 2 > keys.length) rehash();
        var i = h(k);
        var firstDel = -1;
        for (;;) {
            var kk = keys[i];
            if (kk == EMPTY) {
                if (firstDel != -1) i = firstDel;
                keys[i] = k;
                size++;
                used++;
                return true;
            }
            if (kk == DELETED) {
                if (firstDel == -1) firstDel = i;
            } else if (kk == k) {
                return false;
            }
            i = (i + 1) & mask;
        }
    }

    public boolean remove(int k) {
        var i = h(k);
        for (;;) {
            var kk = keys[i];
            if (kk == EMPTY) return false;
            if (kk == k) {
                keys[i] = DELETED;
                size--;
                return true;
            }
            i = (i + 1) & mask;
        }
    }

    private void rehash() {
        var old = keys;
        keys = new int[old.length << 1];
        Arrays.fill(keys, EMPTY);
        mask = keys.length - 1;
        size = 0;
        used = 0;
        for (var k : old) if (k != EMPTY && k != DELETED) add(k);
    }
}
```

---

### B.4 Rolling Hash

```java
public class RollingHashOne {
    static final long MOD = 1_000_000_007L;
    static final long BASE = 911382323L;

    static final class Hasher {
        final int n;
        final long[] p;
        final long[] h;
        Hasher(String s) {
            n = s.length();
            p = new long[n + 1];
            h = new long[n + 1];
            p[0] = 1;
            for (var i = 0; i < n; i++) {
                p[i + 1] = (p[i] * BASE) % MOD;
                h[i + 1] = (h[i] * BASE + s.charAt(i)) % MOD;
            }
        }
        long get(int l, int r) {
            var x = (h[r] - (h[l] * p[r - l]) % MOD);
            if (x < 0) x += MOD;
            return x;
        }
    }
}
```

---

## Section C: Basic Trees

---

### C.1 Binary Tree

```java
import java.util.*;

public class BinaryTreeBasics {
    static final class Node {
        int val;
        Node left, right;
        Node(int val) { this.val = val; }
    }

    public static List<Integer> bfs(Node root) {
        if (root == null) return List.of();
        var res = new ArrayList<Integer>();
        var q = new ArrayDeque<Node>();
        q.add(root);
        while (!q.isEmpty()) {
            var u = q.poll();
            res.add(u.val);
            if (u.left != null) q.add(u.left);
            if (u.right != null) q.add(u.right);
        }
        return res;
    }

    public static List<Integer> inorderIter(Node root) {
        var res = new ArrayList<Integer>();
        var st = new ArrayDeque<Node>();
        var cur = root;
        while (cur != null || !st.isEmpty()) {
            while (cur != null) {
                st.push(cur);
                cur = cur.left;
            }
            cur = st.pop();
            res.add(cur.val);
            cur = cur.right;
        }
        return res;
    }
}
```

---

### C.2 Binary Search Tree

```java
public class BST {
    static final class Node {
        int val;
        Node left, right;
        Node(int val) { this.val = val; }
    }

    public static Node insert(Node root, int x) {
        if (root == null) return new Node(x);
        var cur = root;
        while (true) {
            if (x < cur.val) {
                if (cur.left == null) { cur.left = new Node(x); break; }
                cur = cur.left;
            } else if (x > cur.val) {
                if (cur.right == null) { cur.right = new Node(x); break; }
                cur = cur.right;
            } else {
                break;
            }
        }
        return root;
    }

    public static boolean contains(Node root, int x) {
        var cur = root;
        while (cur != null) {
            if (x < cur.val) cur = cur.left;
            else if (x > cur.val) cur = cur.right;
            else return true;
        }
        return false;
    }

    public static Node delete(Node root, int x) {
        if (root == null) return null;
        if (x < root.val) root.left = delete(root.left, x);
        else if (x > root.val) root.right = delete(root.right, x);
        else {
            if (root.left == null) return root.right;
            if (root.right == null) return root.left;
            // replace with inorder successor
            var s = root.right;
            while (s.left != null) s = s.left;
            root.val = s.val;
            root.right = delete(root.right, s.val);
        }
        return root;
    }
}
```

---

### C.3 AVL Tree

```java
public class AVL {
    static final class Node {
        int val;
        int h;
        Node left, right;
        Node(int val) { this.val = val; this.h = 1; }
    }

    static int height(Node n) { return n == null ? 0 : n.h; }
    static int bf(Node n) { return n == null ? 0 : height(n.left) - height(n.right); }
    static void pull(Node n) { n.h = 1 + Math.max(height(n.left), height(n.right)); }

    static Node rotRight(Node y) {
        var x = y.left;
        var t = x.right;
        x.right = y;
        y.left = t;
        pull(y);
        pull(x);
        return x;
    }

    static Node rotLeft(Node x) {
        var y = x.right;
        var t = y.left;
        y.left = x;
        x.right = t;
        pull(x);
        pull(y);
        return y;
    }

    public static Node insert(Node n, int x) {
        if (n == null) return new Node(x);
        if (x < n.val) n.left = insert(n.left, x);
        else if (x > n.val) n.right = insert(n.right, x);
        else return n;

        pull(n);
        var b = bf(n);
        if (b > 1 && x < n.left.val) return rotRight(n);
        if (b < -1 && x > n.right.val) return rotLeft(n);
        if (b > 1 && x > n.left.val) { n.left = rotLeft(n.left); return rotRight(n); }
        if (b < -1 && x < n.right.val) { n.right = rotRight(n.right); return rotLeft(n); }
        return n;
    }
}
```

---

### C.4 N-ary Tree

```java
import java.util.*;

public class NAryTree {
    static final class Node {
        int val;
        List<Node> children = new ArrayList<>();
        Node(int val) { this.val = val; }
    }

    public static List<Integer> bfs(Node root) {
        if (root == null) return List.of();
        var res = new ArrayList<Integer>();
        var q = new ArrayDeque<Node>();
        q.add(root);
        while (!q.isEmpty()) {
            var u = q.poll();
            res.add(u.val);
            for (var v : u.children) q.add(v);
        }
        return res;
    }
}
```

---

## Section D: Heaps

---

### D.1 Binary Min Heap

```java
import java.util.*;

public class MinHeap {
    int[] a;
    int n;

    public MinHeap(int cap) {
        a = new int[Math.max(1, cap)];
    }

    public boolean isEmpty() { return n == 0; }
    public int size() { return n; }

    public void push(int x) {
        if (n == a.length) a = Arrays.copyOf(a, a.length << 1);
        a[n] = x;
        siftUp(n++);
    }

    public int peek() {
        if (n == 0) throw new NoSuchElementException();
        return a[0];
    }

    public int pop() {
        if (n == 0) throw new NoSuchElementException();
        var res = a[0];
        a[0] = a[--n];
        siftDown(0);
        return res;
    }

    private void siftUp(int i) {
        while (i > 0) {
            var p = (i - 1) >>> 1;
            if (a[p] <= a[i]) break;
            var t = a[p]; a[p] = a[i]; a[i] = t;
            i = p;
        }
    }

    private void siftDown(int i) {
        while (true) {
            var l = i * 2 + 1;
            if (l >= n) break;
            var r = l + 1;
            var m = (r < n && a[r] < a[l]) ? r : l;
            if (a[i] <= a[m]) break;
            var t = a[i]; a[i] = a[m]; a[m] = t;
            i = m;
        }
    }
}
```

---

### D.2 Binary Max Heap

```java
// Same as MinHeap but reversed comparisons.
```
