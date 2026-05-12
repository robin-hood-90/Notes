---
tags: [c, core, function-pointers, callbacks, vtables, oop-in-c, qsort]
aliases: ["Function Pointers", "Callbacks", "Vtables", "OOP in C", "qsort callback"]
status: stable
updated: 2026-05-09
---

# Function Pointers, Callbacks, and Vtables

> [!summary] Goal
> Master function pointers — declare, assign, call, pass as arguments, and store in structs. Build vtables for object-oriented programming in C. Essential for callbacks, event-driven code, and OS device driver frameworks.

## Table of Contents

1. [Function Pointer Basics](#function-pointer-basics)
2. [Callbacks](#callbacks)
3. [Vtables — OOP in C](#vtables-oop-in-c)
4. [Inheritance in C](#inheritance-in-c)
5. [Pitfalls](#pitfalls)

---

## Function Pointer Basics

> [!info] Function pointer
> A function pointer stores the address of a function. Unlike data pointers, they point to executable code (the .text segment). The type of a function pointer encodes the function's return type and parameter types. Calling a function through a pointer has no overhead compared to a direct call.

```c
// Declaration syntax: return_type (*name)(parameter_types)
int (*op)(int, int);      // Pointer to a function taking two ints, returning int

// Assign — a function name decays to a pointer (like arrays)
int add(int a, int b) { return a + b; }
op = add;                 // OK: function name decays to pointer
op = &add;                // Same: address-of operator is optional

// Call
int result = op(3, 4);    // 7 — call through pointer
result = (*op)(3, 4);     // Same — dereference then call

// No performance difference between direct and pointer call
```

### Array of function pointers

```c
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }
int divide(int a, int b) { return b ? a / b : 0; }

// Array of function pointers
int (*ops[])(int, int) = {add, sub, mul, divide};

// Call through array
int result = ops[2](10, 5);   // mul(10, 5) = 50

// With enum for readability
typedef enum { OP_ADD, OP_SUB, OP_MUL, OP_DIV } OpCode;
int result = ops[OP_MUL](10, 5);
```

### Function pointer typedef

```c
// Without typedef — verbose
void sort(int *arr, int n, int (*compare)(const void *, const void *));

// With typedef — clear intent
typedef int (*comparator_fn)(const void *, const void *);
void sort(int *arr, int n, comparator_fn compare);

// For complex signatures
typedef void (*signal_handler)(int);
signal_handler old = signal(SIGINT, my_handler);
```

---

## Callbacks

> [!info] Callback
> A callback is a function pointer passed as an argument to another function. The receiving function "calls back" the pointed-to function at the appropriate time. This is the foundation of event-driven programming, asynchronous operations, and the Strategy pattern in C.

### qsort callback — the classic example

```c
#include <stdlib.h>

// Comparator function must match: int (*)(const void*, const void*)
int compare_ints(const void *a, const void *b) {
    int ia = *(const int *)a;
    int ib = *(const int *)b;
    if (ia < ib) return -1;
    if (ia > ib) return 1;
    return 0;
}

int compare_strings(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

int numbers[] = {42, 3, 17, 8, 99};
qsort(numbers, 5, sizeof(int), compare_ints);
// numbers → {3, 8, 17, 42, 99}
```

### Generic callback pattern

```c
typedef struct {
    void (*on_data)(void *user_data, const char *data, size_t len);
    void (*on_error)(void *user_data, int error_code, const char *msg);
    void (*on_complete)(void *user_data);
    void *user_data;     // User-provided context passed to all callbacks
} Callbacks;

void process_stream(const char *input, Callbacks *cb) {
    // Simulate async processing
    cb->on_data(cb->user_data, input, strlen(input));
    // On failure:
    // cb->on_error(cb->user_data, -1, "parse error");
    cb->on_complete(cb->user_data);
}

// Usage
void my_data_handler(void *ctx, const char *data, size_t len) {
    printf("Got %zu bytes: %.*s\n", len, (int)len, data);
}

void my_complete_handler(void *ctx) {
    printf("Done!\n");
}

Callbacks cb = {
    .on_data = my_data_handler,
    .on_complete = my_complete_handler,
    .on_error = NULL,        // Not handling errors
    .user_data = NULL
};

process_stream("hello", &cb);
```

### Context pointer pattern

```c
// The void* context pointer avoids global variables
// Any data can be passed through without changing the callback signature

typedef struct {
    int count;
    char output[256];
} ProcessorContext;

void data_callback(void *ctx, const char *data, size_t len) {
    ProcessorContext *pc = (ProcessorContext *)ctx;
    pc->count++;
    snprintf(pc->output, sizeof(pc->output), "Received: %.*s", (int)len, data);
}
```

---

## Vtables — OOP in C

> [!info] Vtable
> A **vtable** (virtual table) is a struct containing function pointers, representing the "methods" of an object. Each "object" stores a pointer to its vtable. This is how C++ implements virtual functions, and it's how Linux device drivers define their operations.

### The vtable pattern

```c
// Forward declaration
typedef struct Shape Shape;

// Vtable — all operations this type supports
typedef struct {
    double (*area)(const Shape *self);
    double (*perimeter)(const Shape *self);
    void (*print)(const Shape *self);
} ShapeVtable;

// Object — stores its vtable pointer and instance data
struct Shape {
    const ShapeVtable *vtable;   // Points to the type's vtable
};

// Public API — dispatch through vtable
double shape_area(const Shape *shape) {
    return shape->vtable->area(shape);
}

double shape_perimeter(const Shape *shape) {
    return shape->vtable->perimeter(shape);
}

void shape_print(const Shape *shape) {
    shape->vtable->print(shape);
}
```

### Concrete type — Circle

```c
// Circle struct — Shape + circle-specific data
typedef struct {
    Shape base;          // Must be first field for casting to Shape*
    double radius;
} Circle;

// Circle implementations of Shape methods
static double circle_area(const Shape *shape) {
    const Circle *circle = (const Circle *)shape;
    return 3.14159 * circle->radius * circle->radius;
}

static double circle_perimeter(const Shape *shape) {
    const Circle *circle = (const Circle *)shape;
    return 2.0 * 3.14159 * circle->radius;
}

static void circle_print(const Shape *shape) {
    const Circle *circle = (const Circle *)shape;
    printf("Circle(radius=%.2f)\n", circle->radius);
}

// Circle vtable (static — one per type, shared across instances)
static const ShapeVtable circle_vtable = {
    .area = circle_area,
    .perimeter = circle_perimeter,
    .print = circle_print
};

// Constructor
Circle *circle_create(double radius) {
    Circle *c = malloc(sizeof(Circle));
    c->base.vtable = &circle_vtable;   // Set vtable
    c->radius = radius;
    return c;
}

void circle_destroy(Circle *c) { free(c); }
```

### Concrete type — Rectangle

```c
typedef struct {
    Shape base;
    double width;
    double height;
} Rectangle;

static double rect_area(const Shape *s) {
    const Rectangle *r = (const Rectangle *)s;
    return r->width * r->height;
}

static double rect_perimeter(const Shape *s) {
    const Rectangle *r = (const Rectangle *)s;
    return 2.0 * (r->width + r->height);
}

static void rect_print(const Shape *s) {
    const Rectangle *r = (const Rectangle *)s;
    printf("Rectangle(%.2f x %.2f)\n", r->width, r->height);
}

static const ShapeVtable rect_vtable = {
    .area = rect_area,
    .perimeter = rect_perimeter,
    .print = rect_print
};

Rectangle *rectangle_create(double w, double h) {
    Rectangle *r = malloc(sizeof(Rectangle));
    r->base.vtable = &rect_vtable;
    r->width = w;
    r->height = h;
    return r;
}
```

### Polymorphic usage

```c
// Works with any Shape* — dispatch happens through vtable
void print_shape_info(const Shape *shape) {
    printf("Area: %.2f\n", shape_area(shape));
    printf("Perimeter: %.2f\n", shape_perimeter(shape));
    shape_print(shape);
}

// Create various shapes
Shape *shapes[] = {
    (Shape *)circle_create(5.0),
    (Shape *)rectangle_create(3.0, 4.0)
};

for (int i = 0; i < 2; i++) {
    print_shape_info(shapes[i]);    // Polymorphic call
}

// Cleanup (must cast back to concrete type)
circle_destroy((Circle *)shapes[0]);
free(shapes[1]);
```

---

## Inheritance in C

> [!info] Inheritance via struct embedding
> C achieves "inheritance" by embedding a base struct as the **first field** of a derived struct. This allows casting between base and derived pointers because they share the same starting address. C++ does exactly the same thing under the hood.

```c
// Base "class"
typedef struct {
    int id;
    char name[64];
} Base;

void base_init(Base *b, int id, const char *name) {
    b->id = id;
    strncpy(b->name, name, sizeof(b->name) - 1);
}

// Derived "class" — embeds Base as first field
typedef struct {
    Base base;              // Must be first — enables casting
    double salary;
} Employee;

// Constructor for derived
void employee_init(Employee *e, int id, const char *name, double salary) {
    base_init(&e->base, id, name);   // Call "base constructor"
    e->salary = salary;
}

// Usage — cast Employee* to Base* for polymorphic functions
void print_base_info(Base *b) {
    printf("ID: %d, Name: %s\n", b->id, b->name);
}

Employee emp;
employee_init(&emp, 42, "Alice", 100000.0);
print_base_info((Base *)&emp);       // Works: Base is at offset 0
```

### Kernel-style vtable (Linux file_operations)

```c
// This is the actual pattern used in the Linux kernel for device drivers
struct file_operations {
    ssize_t (*read)(struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write)(struct file *, const char __user *, size_t, loff_t *);
    int (*open)(struct inode *, struct file *);
    int (*release)(struct inode *, struct file *);
    long (*unlocked_ioctl)(struct file *, unsigned int, unsigned long);
    // ... more operations
};

// A driver provides its own file_operations struct
static const struct file_operations my_driver_fops = {
    .read  = my_driver_read,
    .write = my_driver_write,
    .open  = my_driver_open,
    .release = my_driver_release,
};
```

---

## Pitfalls

### Wrong function pointer signature

```c
int add(int a, int b) { return a + b; }
int (*wrong)(int) = add;   // ❌ Compiler warning! Signature mismatch
wrong(5);                  // Undefined behavior — stack corruption!
```

### Forgetting to check callback for NULL

```c
void process(Callbacks *cb) {
    // cb->on_complete(cb->user_data);   // ❌ Crashes if on_complete is NULL
    if (cb->on_complete) cb->on_complete(cb->user_data);  // ✅ Safe
}
```

### Returning pointer to stack-local function pointer

```c
typedef int (*op_fn)(int, int);

op_fn get_op(char c) {
    op_fn f;                      // Stack local — invalid after return!
    if (c == '+') f = add;        // add itself is fine (static code)
    // ... but returning f is fine here because f holds a static address
    return f;
}
// This is OK for function pointers (they point to code, not stack).
// But never return a pointer to a stack-local struct!
```

### Memory management with vtable objects

The vtable is `static const` (shared, read-only). Only the instance data is allocated. When freeing, you MUST know the concrete type to call the correct destructor. This is why C++ has virtual destructors.

---

> [!question]- Interview Questions
>
> **Q: How do you declare a function pointer that takes an int and returns a float?**
> A: `float (*fp)(int);` Read right-left: start at `fp`, go right (nothing), go left to `*` (pointer), go right to `(int)` (function taking int), go left to `float` (returning float). fp is a pointer to a function taking int returning float.
>
> **Q: How does qsort accept different comparison functions?**
> A: qsort takes a function pointer `int (*compare)(const void*, const void*)`. You provide a comparison function that returns <0, 0, or >0. qsort calls it internally to determine element ordering. This is the Strategy pattern — the sorting algorithm is fixed, the comparison strategy is parameterized.
>
> **Q: How can you implement polymorphism in C?**
> A: Use a vtable — a struct of function pointers. Each "object" holds a pointer to its type's vtable. Methods dispatch through the vtable: `shape->vtable->area(shape)`. Different concrete types (Circle, Rectangle) provide different vtable implementations, giving polymorphic behavior without C++.
>
> **Q: What is the Linux kernel's `file_operations` struct?**
> A: It's a vtable that defines the operations a device driver supports: open, read, write, release, ioctl, etc. Each driver provides its own `file_operations` instance. When userspace calls `read()` on a device file, the kernel dispatches through the driver's `read` function pointer. This is the vtable pattern at the heart of Linux VFS.
>
> **Q: Why use a `void *user_data` parameter in callbacks?**
> A: Without a context parameter, the callback has no access to the caller's state — you'd need global variables. The `void *user_data` lets the caller pass any data (a struct, an array, whatever) to the callback without changing the callback's signature. This is the "context pointer" pattern.

---

## Cross-Links

- [[C/01_Foundations/01_C_Basics_and_Pointers]] for pointer fundamentals
- [[C/01_Foundations/08_Enums_Typedef_and_Complex_Declarations]] for function pointer typedef
- [[C/02_Core/04_Data_Structures_in_C]] for linked lists with function pointers
- [[C/05_Projects/02_HTTP_Server_Minimal]] for callbacks in network programming
- [[C/05_Projects/03_Tiny_Shell_Parser_and_Executor]] for command dispatch with function pointers
