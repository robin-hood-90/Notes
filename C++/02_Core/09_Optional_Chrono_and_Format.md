---
tags: [cpp, core, optional, chrono, format, time, chrono-io, formatter, print]
aliases: ["std::optional", "std::chrono", "std::format", "std::print", "C++20 Time", "Chrono I/O"]
status: stable
updated: 2026-05-11
---

# `std::optional`, `std::chrono`, and `std::format`

> [!summary] Goal
> Master three essential vocabulary types and text utilities: `std::optional` for maybe-values (including C++23 monadic operations), `std::chrono` for time (durations, time points, calendars, time zones), and `std::format`/`std::print` for type-safe, efficient text formatting.

## Table of Contents

1. [std::optional — The Maybe Monad](#stdoptional-the-maybe-monad)
2. [std::chrono — Time Types](#stdchrono-time-types)
3. [std::format and std::print](#stdformat-and-stdprint)

---

## `std::optional` — The Maybe Monad

> [!info] optional
> `std::optional<T>` (C++17) represents either a value of type `T` or "no value." Unlike a raw pointer (which can be null) or a sentinel flag (which requires a separate variable), `optional` encapsulates the maybe-value semantics in a single type with a well-defined interface.

### Construction and basic access

```cpp
#include <optional>
#include <string>

// Construction
std::optional<int> empty;                               // nullopt
std::optional<int> has_value = 42;                      // has value
std::optional<int> from_nullopt = std::nullopt;          // nullopt
std::optional<std::string> in_place(std::in_place, "hello");  // in-place, avoids move

// Access
if (has_value) { /* true if has value */ }
if (has_value.has_value()) { /* same */ }

int val = has_value.value();               // Returns value or throws std::bad_optional_access
int safe = has_value.value_or(0);          // Returns value or 0 if empty
int ref = *has_value;                       // UB if empty (like dereferencing nullptr)
```

### C++23 monadic operations

```cpp
// C++23 adds functional composition — chaining maybe-values without unwrapping.
// These make optional behave like a "Maybe monad":

// 1. transform — map the value if present
std::optional<int> opt = 42;
auto squared = opt.transform([](int x) { return x * x; });  // optional(1764)
auto empty_sq = std::optional<int>{}.transform([](auto x) { return x; });  // nullopt

// 2. and_then — flat-map: return another optional
std::optional<std::string> get_env(const char* name);  // maybe returns env var
auto port_str = get_env("PORT");                       // optional<string>
auto port = port_str.and_then([](const std::string& s) {
    char* end;
    long val = std::strtol(s.c_str(), &end, 10);
    if (*end == '\0' && val >= 0 && val <= 65535) {
        return std::optional<int>(static_cast<int>(val));
    }
    return std::optional<int>{};
});

// 3. or_else — provide fallback if empty
auto fallback = port.or_else([]() -> std::optional<int> {
    return 8080;  // default port
});

// Chaining example: parse an int from an env var
auto parse_port = get_env("PORT")
    .and_then([](const std::string& s) -> std::optional<int> {
        try { return std::stoi(s); } catch (...) { return std::nullopt; }
    })
    .transform([](int p) -> int { return std::clamp(p, 1024, 65535); })
    .or_else([]() -> std::optional<int> { return 8080; });
```

### When to use `std::optional`

```cpp
// ✅ DO: optional return when "no result" is not an error
std::optional<User> find_user(int id);  // Not found is normal

// ✅ DO: optional parameter for "maybe pass something"
void configure(/* ... */ std::optional<int> timeout_ms = std::nullopt);

// ✅ DO: optional member for optional fields in data models
struct Config { std::optional<int> port; };  // port not specified → use default

// ❌ DON'T: optional for error handling (use std::expected in C++23)
// ❌ DON'T: optional for nullable references (use T*)
// ❌ DON'T: optional<bool> (use std::optional<bool> tristate — it's valid but confusing)
```

---

## `std::chrono` — Time Types

> [!info] chrono
> `std::chrono` provides three families of types: **durations** (time spans — hours, milliseconds, etc.), **time points** (points on a timeline), and **clocks** (epoch + tick rate). C++20 added calendar types (`year_month_day`, `weekday`) and time zone support.

### Durations

```cpp
#include <chrono>
using namespace std::chrono_literals;

// Duration is a ratio-based time span:
// std::chrono::duration<T, Ratio> where Ratio = period (default: seconds)

std::chrono::seconds sec(10);
std::chrono::milliseconds ms = 1000ms;
std::chrono::microseconds us = 1'000'000us;
std::chrono::nanoseconds ns = 1'000'000'000ns;
std::chrono::minutes min = 5min;
std::chrono::hours h = 2h;

// Conversion (truncating if lossy):
auto ms_from_sec = std::chrono::duration_cast<std::chrono::milliseconds>(sec);
// ms_from_sec.count() == 10000

// Floating-point durations:
using FpSeconds = std::chrono::duration<double>;
FpSeconds fp_sec = 2.5s;  // 2.5 seconds

// Cast to count:
int64_t count_ms = ms_from_sec.count();  // 10000

// Arithmetic:
auto total = 5min + 30s;  // duration = 330 seconds (type: minutes?)
// C++17 uses common_type — total is minutes with fractional seconds truncated
// Better: auto total = 5min + 30s;  // type = seconds (since C++20, seconds is common)
```

### Clocks and time points

```cpp
// Three standard clocks:
//   system_clock   — wall clock (epoch: 1970-01-01 UTC)
//   steady_clock   — monotonic (never adjusted back — for measuring intervals)
//   high_resolution_clock — highest resolution (often alias of steady_clock)

// Time points:
auto now = std::chrono::system_clock::now();       // time_point
auto steady = std::chrono::steady_clock::now();

// Duration since epoch:
auto epoch = now.time_since_epoch();  // duration
auto seconds_since_epoch = std::chrono::duration_cast<std::chrono::seconds>(epoch);

// Measuring intervals:
auto start = std::chrono::steady_clock::now();
do_work();
auto end = std::chrono::steady_clock::now();
auto elapsed = end - start;  // duration
auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed);
std::println("Work took {} ms", ms.count());
```

### C++20 calendar types

```cpp
// C++20 adds human-friendly date types:

using namespace std::chrono;

// Create a date:
auto date = 2026y / May / 11d;   // year_month_day{2026, May, 11}
// auto date = May/11/2026;       // Also valid: order doesn't matter

// Query:
year_month_day ymd = floor<days>(system_clock::now());
year y = ymd.year();         // 2026
month m = ymd.month();       // May
day d = ymd.day();           // 11d

// Weekday:
weekday wd = ymd;            // Monday (0=Sun, 1=Mon, ..., 6=Sat)
weekday_indexed wdi = Sunday[2];  // 2nd Sunday

// Last day of month:
auto last = ymd.year() / ymd.month() / last;
// Or: ymd.year() / ymd.month() / Sunday[last];  // last Sunday of month

// Difference in days:
auto d1 = 2026y/May/11d;
auto d2 = 2026y/June/1d;
auto diff = sys_days{d2} - sys_days{d1};  // days{21}
```

### Time zones (C++20)

```cpp
// C++20 introduces IANA time zone database:

using namespace std::chrono;

// Get the current time in a specific time zone:
auto utc = system_clock::now();
auto ny = zoned_time{"America/New_York", utc};
auto tokyo = zoned_time{"Asia/Tokyo", utc};

// Convert between time zones:
auto ny_to_tokyo = zoned_time{"Asia/Tokyo", ny};

// Format time zone output:
std::println("New York: {:%F %T %Z}", ny);    // "2026-05-11 07:30:00 EDT"
std::println("Tokyo:   {:%F %T %Z}", tokyo);  // "2026-05-11 20:30:00 JST"

// local_time is a time_point without a time zone anchor
auto local = local_days{2026y/May/11d} + 12h + 30min;

// Time zone availability:
const std::vector<std::string>& zones = get_tzdb().zones;  // All IANA zones
```

---

## `std::format` and `std::print`

> [!info] format
> `std::format` (C++20) provides Python-like `{}` formatting. It's type-safe, often faster than `printf` (compile-time format string checking), and produces `std::string`. `std::print` (C++23) outputs directly to stdout/stderr.

### Basic syntax

```cpp
#include <format>
#include <print>

// Simple formatting:
std::string s = std::format("Hello {}!", "world");   // "Hello world!"
std::println("Hello {}!", "world");                   // Prints to stdout

// Positional arguments:
s = std::format("{1} {0}", "world", "Hello");          // "Hello world"

// Format specifiers: {arg:format_spec}
// format_spec: fill align sign # 0 width precision type

// Width and alignment:
std::println("{:10}", 42);            // "        42" (right)
std::println("{:<10}", 42);           // "42        " (left)
std::println("{:^10}", 42);           // "    42    " (center)
std::println("{:0>10}", 42);          // "0000000042" (right, zero-padded)

// Sign:
std::println("{:+}", 42);             // "+42"
std::println("{: }", -42);            // "-42" (space for positive)
std::println("{:-}", 42);             // "42" (only negative sign)

// Precision (floating-point):
std::println("{:.2f}", 3.14159);      // "3.14"
std::println("{:.10f}", 3.14159);     // "3.1415900000"
std::println("{:e}", 3.14159);        // "3.141590e+00"
std::println("{:.2%}", 0.856);        // "85.60%"

// Integer bases:
std::println("{:#x}", 255);           // "0xff"
std::println("{:#b}", 255);           // "0b11111111"
std::println("{:#o}", 255);           // "0o377"
```

### Custom formatters

```cpp
// Custom formatter for user types:

struct Point { double x, y; };

template<>
struct std::formatter<Point> {
    // Parse the format spec (optional — default: no spec)
    constexpr auto parse(auto& ctx) {
        return ctx.begin();  // no spec supported
    }

    // Format the value:
    auto format(const Point& p, auto& ctx) const {
        return std::format_to(ctx.out(), "({}, {})", p.x, p.y);
    }
};

// Usage:
std::println("{}", Point{1.0, 2.5});   // "(1.0, 2.5)"

// Advanced: format spec parsing for custom options
template<>
struct std::formatter<Point> {
    bool show_brackets = true;

    constexpr auto parse(auto& ctx) {
        auto it = ctx.begin();
        if (it != ctx.end() && *it == 'n') {
            show_brackets = false;
            ++it;
        }
        return it;
    }

    auto format(const Point& p, auto& ctx) const {
        if (show_brackets)
            return std::format_to(ctx.out(), "({}, {})", p.x, p.y);
        else
            return std::format_to(ctx.out(), "{}, {}", p.x, p.y);
    }
};

// Usage:
// std::println("{}", Point{1, 2});   // "(1, 2)"
// std::println("{:n}", Point{1, 2}); // "1, 2"
```

### Chrono formatting (C++20)

```cpp
using namespace std::chrono;

auto now = system_clock::now();

// Default format for system_clock::time_point:
std::println("{}", now);  // "2026-05-11 15:30:45"

// Custom chrono format:
std::println("{:%Y-%m-%d %H:%M:%S %Z}", now);  // "2026-05-11 15:30:45 UTC"

// Calendar type:
auto date = 2026y / May / 11d;
std::println("{:%B %d, %Y}", date);  // "May 11, 2026"
std::println("{:%A}", sys_days{date});  // "Monday"

// Duration:
auto dur = 2h + 30min + 15s;
std::println("{:%H:%M:%S}", dur);  // "02:30:15"
```

### Performance

```text
std::format vs alternatives (relative speed, repeating benchmark):

Operation               sprintf    << (ostringstream)   std::format
──────────────────────────────────────────────────────────────────
Format 1 int            ~40ns      ~150ns                ~50ns
Format 1 double         ~80ns      ~200ns                ~70ns
Bulk 1000 calls         ~30μs      ~90μs                 ~35μs
Custom type formatting  ~60ns      ~180ns                ~80ns

std::format is typically:
  - 2-3× faster than ostringstream
  - Comparable to sprintf (sometimes slower, but type-safe)
  - Compile-time checked (catches errors at compile time)
  - Extensible via formatter specialization
```

---

## Cross-Links

- [[C++/02_Core/06_File_IO_Filesystem_and_Format]] for file-based formatting with format_to
- [[C++/01_Foundations/07_Exception_Handling_and_Safety]] for optional vs exceptions for error handling
- [[C++/03_Advanced/06_Modules_and_Cpp20_23_Features]] for std::expected vs optional comparison
- [[C++/02_Core/02_STL_Containers_Deep_Dive]] for container-like usage of optional
