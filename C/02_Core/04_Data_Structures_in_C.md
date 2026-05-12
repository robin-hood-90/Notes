---
tags: [c, core, data-structures, linked-lists, hash-tables, trees, generic-containers]
aliases: ["Data Structures in C", "Linked Lists", "Hash Tables", "Generic Containers", "list_head"]
status: stable
updated: 2026-05-09
---

# Data Structures in C

> [!summary] Goal
> Build fundamental data structures from scratch in C: linked lists (singly, doubly, circular), stacks, queues, hash tables, and binary trees. Implement generic containers using void pointers, function pointers, and macros (Linux kernel style). Essential for OS data structures, device driver lists, and memory management.

## Table of Contents

1. [Singly Linked List](#singly-linked-list)
2. [Doubly Linked List](#doubly-linked-list)
3. [Linux Kernel List Pattern](#linux-kernel-list-pattern)
4. [Stack and Queue](#stack-and-queue)
5. [Hash Table](#hash-table)
6. [Binary Search Tree](#binary-search-tree)
7. [Generic Containers](#generic-containers)
8. [Pitfalls](#pitfalls)

---

## Singly Linked List

> [!info] Singly linked list
> Each node contains data and a pointer to the next node. Traversal is forward-only. Insertion and deletion at the head are O(1). Search and deletion by value are O(n). Simple and memory-efficient — only one pointer per node.

```c
typedef struct Node {
    int value;
    struct Node *next;
} Node;

// Insert at head
Node *list_insert_head(Node *head, int value) {
    Node *node = malloc(sizeof(Node));
    if (!node) return head;
    node->value = value;
    node->next = head;
    return node;
}

// Insert at tail
Node *list_insert_tail(Node *head, int value) {
    Node *node = malloc(sizeof(Node));
    if (!node) return head;
    node->value = value;
    node->next = NULL;

    if (!head) return node;

    Node *cur = head;
    while (cur->next) cur = cur->next;
    cur->next = node;
    return head;
}

// Delete by value
Node *list_delete(Node *head, int value) {
    Node *prev = NULL;
    Node *cur = head;

    while (cur) {
        if (cur->value == value) {
            if (prev) prev->next = cur->next;
            else head = cur->next;       // Deleting head
            free(cur);
            return head;
        }
        prev = cur;
        cur = cur->next;
    }
    return head;  // Not found
}

// Find
Node *list_find(Node *head, int value) {
    for (Node *cur = head; cur; cur = cur->next) {
        if (cur->value == value) return cur;
    }
    return NULL;
}

// Free entire list
void list_free(Node *head) {
    Node *cur = head;
    while (cur) {
        Node *next = cur->next;
        free(cur);
        cur = next;
    }
}
```

---

## Doubly Linked List

> [!info] Doubly linked list
> Each node has both `next` and `prev` pointers. Traversal works in both directions. Deletion of a given node is O(1) — no need to find the predecessor. Used by: Linux kernel linked lists, LRU caches, `std::list`.

```c
typedef struct DNode {
    int value;
    struct DNode *prev;
    struct DNode *next;
} DNode;

// Insert at head
DNode *dlist_insert_head(DNode *head, int value) {
    DNode *node = malloc(sizeof(DNode));
    if (!node) return head;
    node->value = value;
    node->prev = NULL;
    node->next = head;

    if (head) head->prev = node;
    return node;
}

// Delete a known node (O(1))
void dlist_delete(DNode *node) {
    if (node->prev) node->prev->next = node->next;
    if (node->next) node->next->prev = node->prev;
    free(node);
}

// Move to front (LRU helper)
void dlist_move_to_front(DNode **head, DNode *node) {
    if (node == *head) return;
    // Unlink
    node->prev->next = node->next;
    if (node->next) node->next->prev = node->prev;
    // Insert at head
    node->next = *head;
    node->prev = NULL;
    if (*head) (*head)->prev = node;
    *head = node;
}
```

---

## Linux Kernel List Pattern

> [!info] Embedded list node
> The Linux kernel doesn't use a data-carrying list structure. Instead, each struct embeds a `list_head` node, and the list operations use `container_of()` to get the containing struct. This makes **any** struct listable without modifying type-specific code.

```c
// The list node (embedded in any struct you want to make listable)
typedef struct list_head {
    struct list_head *next;
    struct list_head *prev;
} list_head;

#define LIST_HEAD_INIT(name) { &(name), &(name) }
#define LIST_HEAD(name) list_head name = LIST_HEAD_INIT(name)

// Initialize a head node
static inline void init_list_head(list_head *head) {
    head->next = head;
    head->prev = head;
}

// Insert between two consecutive nodes
static inline void __list_add(list_head *new, list_head *prev, list_head *next) {
    next->prev = new;
    new->next = next;
    new->prev = prev;
    prev->next = new;
}

// Add after head (tail insert)
static inline void list_add_tail(list_head *new, list_head *head) {
    __list_add(new, head->prev, head);
}

// Add after head (head insert)
static inline void list_add(list_head *new, list_head *head) {
    __list_add(new, head, head->next);
}

// Delete a node
static inline void list_del(list_head *entry) {
    entry->prev->next = entry->next;
    entry->next->prev = entry->prev;
}

// Check if list is empty
static inline int list_empty(const list_head *head) {
    return head->next == head;
}

// Get the containing struct from a list_head pointer
#define container_of(ptr, type, member) \
    ((type *)((char *)(ptr) - offsetof(type, member)))

// Iterate over a list
#define list_for_each(pos, head) \
    for (pos = (head)->next; pos != (head); pos = pos->next)

// Iterate over a list, getting the containing struct
#define list_for_each_entry(pos, head, member)                       \
    for (pos = container_of((head)->next, typeof(*pos), member);     \
         &pos->member != (head);                                     \
         pos = container_of(pos->member.next, typeof(*pos), member))
```

### Using the kernel list

```c
// Any struct can be made listable by embedding list_head
typedef struct {
    int id;
    char name[64];
    list_head list;              // Embedded list head
} User;

// Create a list
LIST_HEAD(users);

// Add users
User *u1 = malloc(sizeof(User));
u1->id = 1;
strcpy(u1->name, "Alice");
list_add_tail(&u1->list, &users);   // Add to list

User *u2 = malloc(sizeof(User));
u2->id = 2;
strcpy(u2->name, "Bob");
list_add_tail(&u2->list, &users);

// Iterate
User *pos;
list_for_each_entry(pos, &users, list) {
    printf("User %d: %s\n", pos->id, pos->name);
}

// Delete
list_del(&u2->list);
free(u2);
```

---

## Stack and Queue

```c
// Stack — LIFO, implemented as a singly linked list

typedef struct Stack {
    int *data;
    int top;
    int capacity;
} Stack;

Stack *stack_create(int capacity) {
    Stack *s = malloc(sizeof(Stack));
    s->data = malloc(capacity * sizeof(int));
    s->top = -1;
    s->capacity = capacity;
    return s;
}

void stack_push(Stack *s, int value) {
    if (s->top >= s->capacity - 1) return;  // Full
    s->data[++s->top] = value;
}

int stack_pop(Stack *s) {
    if (s->top < 0) return -1;   // Empty
    return s->data[s->top--];
}

int stack_peek(Stack *s) {
    return s->top >= 0 ? s->data[s->top] : -1;
}

void stack_free(Stack *s) { free(s->data); free(s); }

// Queue — FIFO, circular buffer

typedef struct {
    int *data;
    int head;
    int tail;
    int size;
    int capacity;
} Queue;

Queue *queue_create(int capacity) {
    Queue *q = malloc(sizeof(Queue));
    q->data = calloc(capacity, sizeof(int));
    q->head = 0;
    q->tail = 0;
    q->size = 0;
    q->capacity = capacity;
    return q;
}

void enqueue(Queue *q, int value) {
    if (q->size >= q->capacity) return;
    q->data[q->tail] = value;
    q->tail = (q->tail + 1) % q->capacity;
    q->size++;
}

int dequeue(Queue *q) {
    if (q->size == 0) return -1;
    int value = q->data[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->size--;
    return value;
}
```

---

## Hash Table

> [!info] Hash table
> A hash table maps keys to values using a hash function to compute an index into an array of buckets. Collisions are handled via chaining (linked list per bucket) or open addressing (probing). Average O(1) lookup, insertion, deletion.

```c
typedef struct Entry {
    char *key;
    int value;
    struct Entry *next;    // Chaining
} Entry;

typedef struct {
    Entry **buckets;
    int size;              // Number of buckets
    int count;             // Number of entries
} HashTable;

// djb2 hash function — simple and effective for strings
unsigned long hash(const char *str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) hash = ((hash << 5) + hash) + c;
    return hash;
}

HashTable *ht_create(int size) {
    HashTable *ht = malloc(sizeof(HashTable));
    ht->buckets = calloc(size, sizeof(Entry *));
    ht->size = size;
    ht->count = 0;
    return ht;
}

void ht_put(HashTable *ht, const char *key, int value) {
    int index = hash(key) % ht->size;
    
    // Update existing key
    for (Entry *e = ht->buckets[index]; e; e = e->next) {
        if (strcmp(e->key, key) == 0) {
            e->value = value;
            return;
        }
    }
    
    // Insert new entry
    Entry *e = malloc(sizeof(Entry));
    e->key = strdup(key);
    e->value = value;
    e->next = ht->buckets[index];
    ht->buckets[index] = e;
    ht->count++;
    
    // Simple resizing heuristic
    if (ht->count > ht->size * 2) {
        ht_resize(ht, ht->size * 2);
    }
}

int ht_get(HashTable *ht, const char *key, int *found) {
    int index = hash(key) % ht->size;
    for (Entry *e = ht->buckets[index]; e; e = e->next) {
        if (strcmp(e->key, key) == 0) {
            *found = 1;
            return e->value;
        }
    }
    *found = 0;
    return 0;
}

void ht_free(HashTable *ht) {
    for (int i = 0; i < ht->size; i++) {
        Entry *e = ht->buckets[i];
        while (e) {
            Entry *next = e->next;
            free(e->key);
            free(e);
            e = next;
        }
    }
    free(ht->buckets);
    free(ht);
}
```

---

## Binary Search Tree

```c
typedef struct BSTNode {
    int key;
    struct BSTNode *left;
    struct BSTNode *right;
} BSTNode;

BSTNode *bst_insert(BSTNode *root, int key) {
    if (!root) {
        BSTNode *n = malloc(sizeof(BSTNode));
        n->key = key;
        n->left = n->right = NULL;
        return n;
    }
    if (key < root->key) root->left = bst_insert(root->left, key);
    else if (key > root->key) root->right = bst_insert(root->right, key);
    return root;
}

BSTNode *bst_search(BSTNode *root, int key) {
    if (!root || root->key == key) return root;
    if (key < root->key) return bst_search(root->left, key);
    return bst_search(root->right, key);
}

void bst_inorder(BSTNode *root, void (*visit)(int)) {
    if (!root) return;
    bst_inorder(root->left, visit);
    visit(root->key);
    bst_inorder(root->right, visit);
}

void bst_free(BSTNode *root) {
    if (!root) return;
    bst_free(root->left);
    bst_free(root->right);
    free(root);
}
```

---

## Generic Containers

### Using void pointers + function pointers

```c
typedef struct {
    void **data;
    int size;
    int capacity;
    void (*free_fn)(void *ptr);       // Custom destructor
} GenericArray;

GenericArray *ga_create(int initial_cap, void (*free_fn)(void *)) {
    GenericArray *ga = malloc(sizeof(GenericArray));
    ga->data = malloc(initial_cap * sizeof(void *));
    ga->size = 0;
    ga->capacity = initial_cap;
    ga->free_fn = free_fn;
    return ga;
}

void ga_push(GenericArray *ga, void *item) {
    if (ga->size >= ga->capacity) {
        ga->capacity *= 2;
        ga->data = realloc(ga->data, ga->capacity * sizeof(void *));
    }
    ga->data[ga->size++] = item;
}

void ga_free(GenericArray *ga) {
    for (int i = 0; i < ga->size; i++) {
        if (ga->free_fn) ga->free_fn(ga->data[i]);
    }
    free(ga->data);
    free(ga);
}
```

---

## Pitfalls

### Forgetting to update head pointer on insertion/deletion

```c
// ❌ Wrong: doesn't update the caller's head pointer
void insert_bad(Node *head, int val) {
    Node *new = malloc(...);
    new->next = head;
    head = new;              // Only changes local copy!
}

// ✅ Correct: return new head or use pointer-to-pointer
void insert_good(Node **head, int val) {
    Node *new = malloc(...);
    new->next = *head;
    *head = new;
}
```

### List cycle from pointer errors

A single miswired `next` pointer creates an infinite loop. Always test list operations, especially `->next->prev = node` in doubly linked lists.

### Hash table collision degradation

If too many keys hash to the same bucket, the linked list grows long and the table degrades to O(n). Resize when load factor exceeds 2. Use a good hash function (djb2, siphash, xxhash).

### Memory leaks in generic containers

Generic containers that store `void *` have no way to know how to free the stored data. Always provide a destructor function pointer.

---

> [!question]- Interview Questions
>
> **Q: How does the Linux kernel's linked list differ from a standard linked list?**
> A: Standard lists embed data in the node structure. The kernel embeds a `list_head` node inside the data structure. Kernel list operations use `container_of()` to get the containing struct from the list node. This makes any struct listable without type-specific code — one set of list functions for all types.
>
> **Q: How do you resize a hash table without blocking?**
> A: Incremental resizing (used in Redis, Go maps): maintain two tables, every operation moves a few entries from old to new. Once all entries are moved, free the old table. This avoids latency spikes from blocking while rehashing millions of entries.
>
> **Q: Implement a function to reverse a singly linked list in place.**
> A: Three pointers: prev = NULL, cur = head, next. At each step: save next, point cur->next to prev, advance prev and cur. Once cur is NULL, prev is the new head. Time O(n), space O(1).
>
> **Q: What is the purpose of a sentinel/dummy node in a linked list?**
> A: A sentinel node removes edge cases for empty lists and head operations. The sentinel is always present — `head->next` is the first real node, `head->prev` is the last. Even an empty list has `head->next == head->prev == head`. No need to check for NULL in insert/delete.
>
> **Q: What is the load factor of a hash table and when should you resize?**
> A: Load factor = number of entries / number of buckets. For chaining, a load factor of 1.0-2.0 is acceptable. For open addressing, keep it below 0.7 (performance degrades rapidly above 0.8). Resize by doubling the bucket count and rehashing all entries.

---

## Cross-Links

- [[C/01_Foundations/01_C_Basics_and_Pointers]] for pointer fundamentals
- [[C/01_Foundations/03_Dynamic_Memory]] for malloc/free in data structures
- [[C/01_Foundations/05_Structs_Unions_and_Bit_Fields]] for struct layout
- [[C/02_Core/01_Function_Pointers_Callbacks_and_vtables]] for comparator callbacks
- [[C/02_Core/05_Algorithms_and_Recursion]] for tree traversal algorithms
