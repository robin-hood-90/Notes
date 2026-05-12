---
tags: [cpp, core, file-io, filesystem, format, string-view, fstream, stringstream]
aliases: ["File I/O", "Filesystem", "std::format", "std::string_view", "fstream", "Serialization"]
status: stable
updated: 2026-05-09
---

# File I/O, String Processing, and Filesystem

> [!summary] Goal
> Master C++ file I/O (fstream), string processing (stringstream, string_view, format), and the filesystem library (C++17). Handle text, binary, encoding, and directory operations.

## Table of Contents

1. [File Streams (fstream)](#file-streams)
2. [String Streams](#string-streams)
3. [Filesystem Library (C++17)](#filesystem-library)
4. [String Views](#string-views)
5. [Pitfalls](#pitfalls)

---

## File Streams (fstream)

```cpp
#include <fstream>
#include <iostream>

// Writing to a file
std::ofstream out("output.txt");
if (out.is_open()) {
    out << "Hello, world!\n";
    out << "Line 2\n";
    out.close();  // Optional — destructor calls close()
}

// Reading from a file
std::ifstream in("input.txt");
if (in.is_open()) {
    std::string line;
    while (std::getline(in, line)) {   // Read line by line
        std::cout << line << '\n';
    }
}

// Binary mode
std::ofstream bin("data.bin", std::ios::binary);
int value = 42;              // 4 bytes
double pi = 3.14159;         // 8 bytes
bin.write(reinterpret_cast<const char*>(&value), sizeof(value));
bin.write(reinterpret_cast<const char*>(&pi), sizeof(pi));

std::ifstream bin_in("data.bin", std::ios::binary);
int read_val;
double read_pi;
bin_in.read(reinterpret_cast<char*>(&read_val), sizeof(read_val));
bin_in.read(reinterpret_cast<char*>(&read_pi), sizeof(read_pi));
```

### Error handling

```cpp
std::ifstream file("nonexistent.txt");
if (!file) {
    std::cerr << "Failed to open file\n";
    // Check: errno, strerror
    std::perror("fstream");
}

// Read and check
int x;
if (file >> x) {
    std::cout << "Read: " << x << '\n';
} else {
    std::cerr << "Failed to read integer\n";
}
```

---

## String Streams

> [!info] stringstream
> `std::stringstream` treats a string as a stream. Use for: parsing (tokenizing), serialization (formatting in memory), and type conversions (string ↔ number). `istringstream` for input, `ostringstream` for output, `stringstream` for both.

```cpp
#include <sstream>

// Parse — split by spaces
std::string data = "42 3.14 hello";
std::istringstream iss(data);
int i; double d; std::string s;
iss >> i >> d >> s;                    // i=42, d=3.14, s="hello"

// Format — build a string
std::ostringstream oss;
oss << "Value: " << 42 << ", Pi: " << 3.14159;
std::string result = oss.str();        // "Value: 42, Pi: 3.14159"

// Most common use: fast string concatenation
std::ostringstream concat;
for (int i = 0; i < 10000; ++i) {
    concat << i << ' ';
}
// Much faster than: s += std::to_string(i) + ' ';
```

---

## Filesystem Library (C++17)

```cpp
#include <filesystem>
namespace fs = std::filesystem;

// Path manipulation
fs::path p("/home/user/docs/file.txt");
p.root_name();                   // "/" (or "C:" on Windows)
p.root_directory();              // "/"
p.parent_path();                 // "/home/user/docs"
p.filename();                    // "file.txt"
p.stem();                        // "file"
p.extension();                   // ".txt"
p.is_absolute();                 // true
p.is_relative();                 // false

// Directory iteration
fs::path dir = "/home/user/docs";
if (fs::exists(dir) && fs::is_directory(dir)) {
    for (const auto& entry : fs::directory_iterator(dir)) {
        std::cout << entry.path().filename() << '\n';
    }
}

// Recursive directory iteration
for (const auto& entry : fs::recursive_directory_iterator("/home/user")) {
    if (entry.is_regular_file()) {
        std::cout << entry.path() << " (" << entry.file_size() << " bytes)\n";
    }
}

// File operations
fs::copy("source.txt", "dest.txt");                     // Copy file
fs::rename("old.txt", "new.txt");                       // Rename
fs::remove("file.txt");                                 // Delete single file
fs::remove_all("directory");                            // Delete directory recursively
fs::create_directory("new_dir");                        // Create directory
fs::create_directories("a/b/c/d");                      // Create nested directories

// File status
fs::file_status status = fs::status("file.txt");
fs::space_info space = fs::space("/");                  // Disk space
std::cout << "Capacity: " << space.capacity << '\n';
std::cout << "Free: " << space.free << '\n';
std::cout << "Available: " << space.available << '\n';

// File times
auto ftime = fs::last_write_time("file.txt");          // Last modified time
// Convert to time_t (C++20 has to_utc_time)
```

---

## String Views

> [!info] string_view
> `std::string_view` (C++17) is a **non-owning** reference to a string. It points to an existing string's data without copying. Use as a function parameter when the function only needs to read the string. It can't be used to modify the underlying data. It doesn't null-terminate.

### Why string_view was added — the allocation problem

Before C++17, passing a string literal to a function taking `const std::string&` created a **temporary `std::string`** — which heap-allocated:

```cpp
void process(const std::string& name);  // Old signature

process("hello");  // Creates a temporary std::string! Heap allocation!
// std::string("hello") allocates memory, copies "hello", then destroys it.
// For millions of calls (logging, parsing), this adds significant overhead.

void process(std::string_view name);    // C++17 signature

process("hello");  // NO allocation! Just pointer + length copied.
// string_view just points to the literal "hello" in the binary's .rodata.
```

`string_view` is a `{const char*, size_t}` pair — two pointers/words, no heap allocation. It was specifically designed to fix the "accidental allocation" problem when passing string literals or `char*` to functions that expected `const std::string&`.

### The dangling trap — string_view doesn't own the data

```cpp
std::string_view dangling() {
    std::string local = "temporary";
    return local;           // ❌ Compiles! But local is destroyed on return!
}                           // string_view now points to freed memory — UB!

std::string_view sv = dangling();
std::cout << sv;            // UB — reading freed memory!

// The implicit conversion from std::string to string_view makes this too easy.
// No warning from the compiler — it's a legal conversion.

// Even worse: returning a string_view from a function that creates a std::string:
std::string_view make_view() {
    return std::string("hello");  // ❌ string destroyed, view dangling!
}
```

### string_view is NOT null-terminated

```cpp
std::string_view sv("hello");   // Points to the literal "hello\0"
sv.data()[5];                   // Legal '\0' — happenstance of the literal

std::string_view sv2 = sv.substr(0, 3);  // "hel" — NOT null-terminated!
sv2.data()[3];                  // ❌ UB! No null terminator after "hel"
// Passing sv2.data() to a C function expecting const char* is UB!
printf("%s", sv2.data());       // ❌ UB — reads past the data

// Safe way:
printf("%.*s", sv2.size(), sv2.data());  // ✅ Correct — uses length
```

```cpp
#include <string_view>

// As a function parameter (replaces const std::string& in many cases)
void process(std::string_view sv) {
    // Can read but not modify
    for (char c : sv) { /* ... */ }
    if (sv.starts_with("http")) { /* ... */ }  // C++20
}

// No-copy substrings
std::string s = "hello world";
std::string_view sv = s;
std::string_view sub = sv.substr(6, 5);   // "world" — no allocation!

// From various sources
process("Hello");                  // From string literal — no copy!
process(sv);                       // From another string_view
process(s);                        // From std::string — implicit conversion

// ⚠️ string_view doesn't own the data — the original must outlive it
std::string_view dangerous() {
    std::string s = "temporary";
    return s;                      // ❌ s is destroyed, returned sv is dangling!
}
```

---

## Pitfalls

### Binary file read not checking bytes

```cpp
// ❌ Reading binary without checking — may read garbage
int value;
file.read(reinterpret_cast<char*>(&value), sizeof(value));
// value is garbage if the file doesn't have 4 bytes remaining

// ✅ Check before use
if (file.read(reinterpret_cast<char*>(&value), sizeof(value))) {
    // value is valid
}
```

### string_view is not null-terminated

```cpp
std::string_view sv = "hello";
// sv.data() is NOT guaranteed to be null-terminated for non-literal views!
// Passing sv.data() to a C function expecting a C-string is UB
printf("%s", sv.data());        // ❌ UB if sv doesn't point to a null-terminated string
printf("%.*s", sv.size(), sv.data());  // ✅ Safe
```

### exceptions disabled in filesystem operations

`fs::exists(path)` throws `fs::filesystem_error` if there's an actual error (like permission denied). It returns false if the path simply doesn't exist. Wrap filesystem operations in try/catch if you can't guarantee the path is valid.

### Path construction on different platforms

```cpp
fs::path p = "home" / "user" / "docs";   // ✅ Portable: "/home/user/docs"
// fs::path p = "home\\user\\docs";       // ❌ Not portable
```

---

> [!question]- Interview Questions
>
> **Q: What's the difference between ifstream::read and operator>>?**
> A: `read()` is for binary I/O — reads raw bytes, no formatting, no whitespace skipping. `operator>>` is for formatted text I/O — skips whitespace, parses types (int, double, string). Use `read()` for binary data. Use `operator>>` / `std::getline()` for text.
>
> **Q: What is std::string_view and when should you use it?**
> A: A non-owning reference to a string. Use as a read-only function parameter when the function doesn't need to modify or store the string. Avoids unnecessary copies. Can't replace `const std::string&` when the function calls the C API (needs null-terminated) or stores the string.
>
> **Q: How does std::filesystem work?**
> A: Provides path abstraction, directory iteration, file operations (copy, move, create, delete), and file status queries. `fs::path` handles platform-specific formats. `fs::directory_iterator` iterates a directory. `fs::recursive_directory_iterator` goes into subdirectories. Operations throw `fs::filesystem_error` on failure.
>
> **Q: How do you efficiently build a large string from many parts?**
> A: Use `std::ostringstream` — it allocates efficiently without repeated reallocations. `string::operator+=` may reallocate (though it's often amortized O(1) due to exponential growth). `std::format` (C++20) is also efficient. Avoid `s = s + piece` (creates O(n²) copies).

---

## Cross-Links

- [[C++/02_Core/02_STL_Containers_Deep_Dive]] for string as a container
- [[C++/01_Foundations/02_Classes_and_RAII]] for RAII with file streams
- [[C++/01_Foundations/08_Lambdas_and_Functional_Programming]] for lambdas with filesystem
- [[C++/02_Core/03_STL_Algorithms_and_Ranges]] for algorithms with file data
- [[C++/03_Advanced/07_Performance_Cache_and_Optimization]] for efficient file I/O
