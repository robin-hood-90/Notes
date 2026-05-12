---
tags: [cpp, core, random, regex, mt19937, distributions, regular-expressions, pattern-matching, ctre]
aliases: ["std::random", "std::regex", "Random Number Generation", "Regular Expressions", "Mersenne Twister"]
status: stable
updated: 2026-05-11
---

# `std::random` and `std::regex`

> [!summary] Goal
> Master C++ random number generation: engines, distributions, seeding strategies, and pitfalls. Master C++ regular expressions: grammar, operations (`match`/`search`/`replace`), iterators, performance, and alternatives.

## Table of Contents

1. [std::random — Random Number Generation](#stdrandom-random-number-generation)
2. [std::regex — Regular Expressions](#stdregex-regular-expressions)

---

## `std::random` — Random Number Generation

> [!info] Random
> C++11 provides a two-tier random library: **engines** (produce raw random bits) and **distributions** (transform raw bits into a desired distribution). Unlike `rand()` (which is global, low-quality, and threads-unsafe), each engine and distribution is a separate object that can be controlled and combined.

### Engines

```cpp
#include <random>

// The workhorses:
std::mt19937 rng(42);               // Mersenne Twister (32-bit, 2^19937-1 period)
std::mt19937_64 rng64(42);          // 64-bit version
std::ranlux48 rng_lux(42);          // 48-bit RANLUX (higher quality, slower)

// Minimal engines (small state, lower quality):
std::minstd_rand rng_lin(42);        // Linear congruential (small, fast, low quality)

// Seeding with std::random_device (non-deterministic source, if available):
std::random_device rd;
std::mt19937 rng(rd());             // Seed from hardware entropy

// Better seeding with seed_seq:
std::random_device rd;
std::array<int, 624> seed_data;
std::generate(seed_data.begin(), seed_data.end(), std::ref(rd));
std::seed_seq seq(seed_data.begin(), seed_data.end());
std::mt19937 rng(seq);              // Full 624-word seed for MT
```

### Distributions

```cpp
// Uniform integer:
std::uniform_int_distribution<int> dice(1, 6);
int roll = dice(rng);                     // 1..6 inclusive

// Uniform real:
std::uniform_real_distribution<double> unit(0.0, 1.0);
double u = unit(rng);                      // [0.0, 1.0)

// Normal (Gaussian):
std::normal_distribution<double> normal(0.0, 1.0);  // mean=0, stddev=1
double sample = normal(rng);

// Bernoulli (coin flip):
std::bernoulli_distribution coin(0.5);   // 50% true
bool heads = coin(rng);

// Exponential (for Poisson process simulation):
std::exponential_distribution<double> exp_dist(1.0);  // lambda=1

// Poisson:
std::poisson_distribution<int> poisson(4.0);  // mean=4

// Discrete (custom weights):
std::discrete_distribution<int> weighted({10, 30, 60});  // weights for 0,1,2
int choice = weighted(rng);                               // 0:10%, 1:30%, 2:60%

// Piecewise constant / linear:
std::piecewise_constant_distribution<double> piecewise(
    {0.0, 0.5, 1.0},           // interval boundaries
    {1.0, 10.0}                  // densities per interval
);
```

### Creating a good seed

```cpp
// ⚠️  Common BUG: default-constructed Mersenne Twister.
// The default seed is the same every run!

std::mt19937 rng;       // DEFAULT seed (typically 5489) — SAME SEQUENCE every run!

// ✅ ALWAYS seed properly:
std::random_device rd;
std::mt19937 rng(rd());

// ⚠️  random_device may be deterministic on some platforms.
// MinGW: returns the same sequence every run (not truly random).
// MSVC/WSL/macOS: uses real hardware entropy.
// For security-critical seeding, use std::seed_seq with multiple entropy sources.

// Multi-source seeding:
std::random_device rd;
auto seed = std::chrono::steady_clock::now().time_since_epoch().count();
std::seed_seq seq{rd(), static_cast<unsigned>(seed)};
std::mt19937 rng(seq);
```

### The `C` random concept (C++20)

```cpp
// C++20 introduces std::uniform_random_bit_generator concept.
// It's satisfied by all random engines and can be used to define
// generic generator interfaces.

template<std::uniform_random_bit_generator Gen>
double generate_uniform(Gen& g) {
    std::uniform_real_distribution<double> dist;
    return dist(g);
}
```

### Pitfalls and performance

```text
Pitfall 1: Creating a new engine per call
  ❌ for (int i = 0; i < N; ++i) {
      std::mt19937 rng(rd());      // Reset engine EVERY iteration
      double x = dist(rng);
  }
  ✅ std::mt19937 rng(rd());
     for (int i = 0; i < N; ++i) {
      double x = dist(rng);
  }

Pitfall 2: Thread safety
  std::mt19937 is NOT thread-safe.
  ✅ Thread-local RNG: thread_local std::mt19937 rng(rd());

Pitfall 3: std::random_device quality
  On MinGW and some embedded platforms, random_device is deterministic.
  Always check: (rd.entropy() > 0)  // 0 = deterministic source

Pitfall 4: std::default_random_engine
  It's implementation-defined (might be minstd_rand on one platform,
  mt19937 on another). Don't use it for portable code.

Performance (million calls):
  uniform_int_distribution: ~15ns/call
  normal_distribution:      ~30ns/call
  mt19937 generation:       ~5ns/call
```

---

## `std::regex` — Regular Expressions

> [!info] regex
> `std::regex` (C++11) provides regular expression matching, searching, and replacing. Multiple grammar options (`ECMAScript`, `basic`, `extended`, `awk`, `grep`, `egrep`). Note: `std::regex` is infamously slow — it's fine for one-off matching but not for hot paths (use `ctre` compile-time regex or manual parsing for performance).

### Grammar selection

```cpp
#include <regex>

// Default grammar: modified ECMAScript (most familiar syntax)
std::regex re("\\d+");                           // ECMAScript (default)

// Other grammars:
std::regex re_basic("\\{0,1\\}", std::regex::basic);      // BRE: \{0,1\}
std::regex re_extended("[0-9]+", std::regex::extended);   // ERE: [0-9]+
std::regex re_awk("^[0-9]+$", std::regex::awk);           // AWK-style
std::regex re_grep("\\{0,1\\}", std::regex::grep);        // grep BRE
std::regex re_egrep("[0-9]+", std::regex::egrep);         // grep ERE
```

### Core operations

```cpp
// 1. regex_match — exact match (full string must match)
std::regex re(R"(\d{4}-\d{2}-\d{2})");  // YYYY-MM-DD
std::string date = "2026-05-11";
bool exact = std::regex_match(date, re);  // true

// 2. regex_search — find first match anywhere in string
std::regex re_digits(R"(\d+)");
std::string text = "Order 12345, total 99.95";
std::smatch match;                          // String match result
if (std::regex_search(text, match, re_digits)) {
    std::println("Found: {}", match.str());   // "12345"
}

// 3. regex_replace — replace matching parts
std::string result = std::regex_replace(
    text, re_digits, "[NUM]"
);
// result: "Order [NUM], total [NUM].95"

// Back-references in replacement:
result = std::regex_replace(
    text, std::regex("(\\d+)\\.(\\d+)"), "$1 dollars and $2 cents"
);
// result: "Order 12345, total 99 dollars and 95 cents"
```

### Match results

```cpp
std::regex re(R"((\w+)@(\w+\.\w+))");
std::string email = "user@example.com";
std::smatch match;

if (std::regex_match(email, match, re)) {
    std::println("Full match: {}", match.str());        // "user@example.com"
    std::println("Group 1:   {}", match[1].str());      // "user"
    std::println("Group 2:   {}", match[2].str());      // "example.com"
    std::println("Prefix:    {}", match.prefix().str());
    std::println("Suffix:    {}", match.suffix().str());
}

// Iterating over all matches:
std::regex word_re(R"(\w+)");
std::string text = "hello world from C++";
auto begin = std::sregex_iterator(text.begin(), text.end(), word_re);
auto end = std::sregex_iterator{};

for (auto it = begin; it != end; ++it) {
    std::println("Word: {}", it->str());     // hello, world, from, C
}
// Note: "C++" matches as "C" (the '+' is not a word character)

// Token iterator (different matches between matches):
std::regex delim(",");
std::string csv = "a,b,c,d";
auto token_it = std::sregex_token_iterator(csv.begin(), csv.end(), delim, -1);
// -1 returns the NON-matching parts (between commas)
for (auto it = token_it; it != std::sregex_token_iterator{}; ++it) {
    std::println("Token: {}", it->str());   // a, b, c, d
}
```

### Flags and options

```cpp
// Common regex flags:
//   std::regex::icase       — case insensitive
//   std::regex::optimize    — spend more time compiling for faster matching
//   std::regex::nosubs      — don't store sub-matches (faster)

std::regex re("hello", std::regex::icase);
std::regex_match("HELLO", re);   // true

// regex_match, regex_search, regex_replace also take flags:
std::regex_search(
    text, match, re,
    std::regex_constants::match_not_null   // Empty string is NOT a match
    | std::regex_constants::match_any     // Shortest match wins
);
```

### Performance (why std::regex is slow)

```text
std::regex performance vs alternatives (10k matches of "\\d+" on typical CPU):

Library           Time          Notes
──────────────────────────────────────────────────
std::regex        50-200 μs/m   Heavy construction, NFA backtracking
Boost.Regex       30-100 μs/m   Better optimized
CTRE (compile)    1-3 μs/m      Compile-time regex (C++20, lib only)
Manual parse      <1 μs/m       Hand-rolled char-by-char

Why std::regex is slow:
  1. Each std::regex constructor compiles the pattern (NFA/DFA building).
  2. std::regex uses NFA backtracking (exponential worst case).
  3. It allocates significant memory per match (match_results).
  4. The implementation is template-heavy with vtable dispatch.

Mitigation:
  1. Reuse std::regex objects (don't recreate for every match).
  2. Use std::regex::optimize for patterns used frequently.
  3. Use std::regex::nosubs if you don't need captured groups.
  4. Prefer raw string literals (R"(...)") to avoid escaping.

When to use alternatives:
  - CTRE (compile_time_regular_expressions) by Hana Dusíková:
    constexpr auto re = ctre::match<R"(\d+)">;
    if (re("12345")) { /* compile-time regex, almost zero overhead */ }
  - Manual parsing for simple patterns (starts_with, find_first_of).
  - PEGTL or Boost.Spirit for complex grammars.
```

### regex with wide strings and char8_t

```cpp
// Wide regex:
std::wregex wre(L"\\d+");
std::wstring wtext(L"Hello 123");
std::wsmatch wmatch;
std::regex_search(wtext, wmatch, wre);  // matches "123"

// C++20 char8_t support (not all implementations complete):
// std::u8regex (if available)
```

---

## Cross-Links

- [[C++/02_Core/05_Concurrency_and_Parallelism]] for thread-safe RNG (thread_local engines)
- [[C++/01_Foundations/07_Exception_Handling_and_Safety]] for string exceptions in stoi used with regex
- [[C++/02_Core/06_File_IO_Filesystem_and_Format]] for reading files for regex processing
- [[C++/02_Core/09_Optional_Chrono_and_Format]] for std::format with random values
