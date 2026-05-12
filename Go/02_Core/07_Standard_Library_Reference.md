---
tags: [go, core, stdlib, flag, slog, sort, url, maps, slices, fs, exec]
aliases: ["Standard Library Reference", "flag", "slog", "sort", "net/url", "maps", "slices", "os/exec", "io/fs"]
status: stable
updated: 2026-05-03
---

# Standard Library Reference

> [!summary] Goal
> Master Go's most useful standard library packages: `flag`, `sort`, `log/slog`, `net/url`, `maps/slices`, `cmp`, `io/fs`, `os/exec`, and `path/filepath`.

## Table of Contents

1. [`flag` — Command-Line Flags](#flag-command-line-flags)
2. [`sort` — Sorting Slices](#sort-sorting-slices)
3. [`log/slog` — Structured Logging (Go 1.21)](#log-slog-structured-logging)
4. [`net/url` — URL Parsing and Building](#net-url-url-parsing-and-building)
5. [`maps` and `slices` — Generic Utilities (Go 1.21)](#maps-and-slices-generic-utilities)
6. [`cmp` — Comparisons (Go 1.21)](#cmp-comparisons)
7. [`io/fs` — Filesystem Abstractions](#io-fs-filesystem-abstractions)
8. [`os/exec` — Running External Commands](#os-exec-running-external-commands)
9. [`path/filepath` — File Path Operations](#path-filepath-file-path-operations)

---

## `flag` — Command-Line Flags

```go
import "flag"

func main() {
    // Define flags
    name := flag.String("name", "world", "name to greet")
    count := flag.Int("count", 1, "number of times")
    debug := flag.Bool("debug", false, "enable debug mode")

    // Parse from os.Args[1:]
    flag.Parse()

    // Non-flag arguments
    for _, arg := range flag.Args() {
        fmt.Println(arg)
    }

    fmt.Printf("Hello %s (%d times, debug=%v)\n", *name, *count, *debug)
}
```

```bash
go run main.go -name=Alice -count=3 -debug extra1 extra2
# Hello Alice (3 times, debug=true)
# extra1
# extra2
```

### Flag types

| Function | Go type | Default | Example |
|----------|---------|---------|---------|
| `flag.String(name, def, usage)` | `*string` | any string | `-host=localhost` |
| `flag.Int(name, def, usage)` | `*int` | any int | `-port=8080` |
| `flag.Bool(name, def, usage)` | `*bool` | `true`/`false` | `-verbose` (sets true) |
| `flag.Duration(name, def, usage)` | `*time.Duration` | any duration | `-timeout=30s` |
| `flag.Float64(name, def, usage)` | `*float64` | any float | `-rate=0.5` |

### Subcommands with `flag.NewFlagSet`

```go
import "flag"

func main() {
    if len(os.Args) < 2 {
        fmt.Println("expected subcommand: serve or version")
        os.Exit(1)
    }

    switch os.Args[1] {
    case "serve":
        fs := flag.NewFlagSet("serve", flag.ExitOnError)
        port := fs.Int("port", 8080, "server port")
        fs.Parse(os.Args[2:])
        fmt.Printf("starting server on port %d\n", *port)

    case "version":
        fmt.Println("v1.0.0")

    default:
        fmt.Printf("unknown subcommand: %s\n", os.Args[1])
        os.Exit(1)
    }
}
```

---

## `sort` — Sorting Slices

```go
import "sort"

// Sort built-in types
ints := []int{3, 1, 4, 1, 5}
sort.Ints(ints)                        // [1, 1, 3, 4, 5]

strs := []string{"c", "a", "b"}
sort.Strings(strs)                     // ["a", "b", "c"]

// Sort with custom comparator
users := []User{{"Alice", 30}, {"Bob", 25}}
sort.Slice(users, func(i, j int) bool {
    return users[i].Age < users[j].Age
})

// Stable sort — preserves order of equal elements
sort.SliceStable(users, func(i, j int) bool {
    return users[i].Name < users[j].Name
})

// Check if sorted
sort.SliceIsSorted(ints, func(i, j int) bool {
    return ints[i] < ints[j]
})

// Reverse sort
sort.Sort(sort.Reverse(sort.IntSlice(ints)))

// Binary search
index := sort.Search(len(ints), func(i int) bool {
    return ints[i] >= 3                 // finds first index where ints[i] >= 3
})
```

---

## `log/slog` — Structured Logging (Go 1.21)

```go
import "log/slog"

func main() {
    // Text handler (default)
    slog.Info("server starting", "port", 8080)

    // JSON handler (recommended for production)
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
        AddSource: true,
    }))
    slog.SetDefault(logger)

    // Log levels
    slog.Debug("debug message", "key", "value")     // hidden by default
    slog.Info("info message", "count", 42)
    slog.Warn("warn message", "error", err)
    slog.Error("error message", "err", err)

    // Structured attributes
    slog.Info("request processed",
        slog.String("method", "GET"),
        slog.Int("status", 200),
        slog.Duration("duration", 150*time.Millisecond),
        slog.Group("user",
            slog.String("id", "abc"),
            slog.Int("age", 30),
        ),
    )
    // {"time":"...", "level":"INFO", "msg":"request processed",
    //  "method":"GET", "status":200, "duration":150000000,
    //  "user":{"id":"abc", "age":30}}

    // Context-based logging
    ctx := context.Background()
    slog.InfoContext(ctx, "with context", "reqID", "abc-123")
}
```

---

## `net/url` — URL Parsing and Building

```go
import "net/url"

// Parse a URL
u, err := url.Parse("https://user:pass@example.com:8080/path?id=42&q=golang#section")
if err != nil {
    panic(err)
}

fmt.Println(u.Scheme)           // "https"
fmt.Println(u.User.Username())  // "user"
fmt.Println(u.Host)             // "example.com:8080"
fmt.Println(u.Hostname())       // "example.com"
fmt.Println(u.Port())           // "8080"
fmt.Println(u.Path)             // "/path"
fmt.Println(u.Fragment)         // "section"

// Query parameters
q := u.Query()
q.Get("id")                     // "42"
q.Get("q")                      // "golang"
q.Has("missing")                // false
q.Add("lang", "go")
q.Set("id", "99")
u.RawQuery = q.Encode()         // "id=99&q=golang&lang=go"

// Build a URL
u2 := &url.URL{
    Scheme: "https",
    Host:   "api.example.com",
    Path:   "/search",
    RawQuery: url.Values{
        "q": {"golang"},
        "page": {"2"},
    }.Encode(),
}
fmt.Println(u2.String())        // "https://api.example.com/search?page=2&q=golang"
```

---

## `maps` and `slices` — Generic Utilities (Go 1.21)

```go
import (
    "maps"
    "slices"
)

// maps — generic map operations
src := map[string]int{"a": 1, "b": 2}
dst := maps.Clone(src)            // deep copy
maps.Copy(dst, src)               // copy into existing map
maps.Equal(src, dst)              // compare
maps.DeleteFunc(src, func(k string, v int) bool {
    return v < 2                  // delete entries where value < 2
})

// slices — generic slice operations
nums := []int{3, 1, 2, 1, 4}
slices.Sort(nums)                 // [1, 1, 2, 3, 4]
slices.SortFunc(nums, func(a, b int) int {
    return b - a                  // descending
})
idx := slices.Index(nums, 3)      // find index
contains := slices.Contains(nums, 5)
unique := slices.Compact(nums)    // remove adjacent duplicates (sort first!)
clipped := slices.Clip(nums)      // remove unused capacity
nums2 := slices.Delete(nums, 1, 3) // remove elements 1-2
```

---

## `cmp` — Comparisons (Go 1.21)

```go
import "cmp"

cmp.Compare(1, 2)       // -1 (less)
cmp.Compare(2, 2)       // 0 (equal)
cmp.Compare(3, 2)       // 1 (greater)

cmp.Less(1, 2)          // true

// cmp.Or returns the first non-zero value
cmp.Or("", "fallback")  // "fallback"
cmp.Or(0, 42, 100)      // 42

// Useful with sort.SliceFunc
slices.SortFunc(items, func(a, b Item) int {
    return cmp.Compare(a.Priority, b.Priority)
})
```

---

## `io/fs` — Filesystem Abstractions

```go
import "io/fs"

// The fs.FS interface represents a read-only filesystem
// os.DirFS creates an fs.FS from the OS filesystem
// embed.FS creates an fs.FS from embedded files

// Read a file
data, err := fs.ReadFile(os.DirFS("/etc"), "hostname")

// Read directory
entries, err := fs.ReadDir(os.DirFS("."), ".")
for _, entry := range entries {
    fmt.Println(entry.Name(), entry.IsDir())
}

// Walk directory
fs.WalkDir(os.DirFS("src"), ".", func(path string, d fs.DirEntry, err error) error {
    if err != nil {
        return err
    }
    fmt.Println(path)
    return nil
})

// Stat a file
info, err := fs.Stat(os.DirFS("."), "main.go")
fmt.Println(info.Size(), info.ModTime())

// Subdirectory
sub, err := fs.Sub(os.DirFS("."), "internal")
```

---

## `os/exec` — Running External Commands

```go
import "os/exec"

// Simple command
out, err := exec.Command("ls", "-la").Output()
fmt.Println(string(out))

// Stdin / Stdout plumbing
cmd := exec.Command("grep", "error")
cmd.Stdin = strings.NewReader("log line 1\nerror line\nlog line 3\n")
var buf bytes.Buffer
cmd.Stdout = &buf
cmd.Run()
fmt.Println(buf.String())          // "error line"

// With context cancellation
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
if err := exec.CommandContext(ctx, "sleep", "10").Run(); err != nil {
    fmt.Println("command timed out:", err)
}

// Streaming output
cmd := exec.Command("tail", "-f", "/var/log/syslog")
cmd.Stdout = os.Stdout
cmd.Stderr = os.Stderr
cmd.Start()
// ... do other work ...
cmd.Wait()
```

---

## `path/filepath` — File Path Operations

```go
import "path/filepath"

// Join path elements
path := filepath.Join("src", "main", "go")     // "src/main/go"
path = filepath.Join("/base", "dir", "..")     // "/base" (cleaned)

// Split
dir, file := filepath.Split("/var/log/syslog") // "/var/log/", "syslog"

// Components
ext := filepath.Ext("/var/log/syslog")         // ".log"
base := filepath.Base("/var/log/syslog")       // "syslog"
dir := filepath.Dir("/var/log/syslog")         // "/var/log"

// Walk
filepath.WalkDir(".", func(path string, d fs.DirEntry, err error) error {
    if err != nil {
        return err
    }
    fmt.Println(path, d.Size())
    return nil
})

// Glob
matches, _ := filepath.Glob("**/*.go")
for _, m := range matches {
    fmt.Println(m)
}

// Absolute / Relative
abs, _ := filepath.Abs(".")
rel, _ := filepath.Rel("/base", "/base/sub/file.txt") // "sub/file.txt"
```

---

## Cross-Links

- [[Go/01_Foundations/04_Modules_Packages_and_Tooling]] for `go build` and tooling reference
- [[Go/02_Core/04_NetHTTP_Server_Middleware_and_Clients]] for HTTP server/client patterns
- [[Go/02_Core/05_Stdlib_IO_Encoding_and_JSON]] for I/O and encoding reference
- [[Go/05_Projects/03_CLI_Tool_with_Subcommands]] for full CLI tool implementation

---

## References

- [flag package](https://pkg.go.dev/flag)
- [sort package](https://pkg.go.dev/sort)
- [log/slog](https://pkg.go.dev/log/slog)
- [net/url](https://pkg.go.dev/net/url)
- [maps package](https://pkg.go.dev/maps)
- [slices package](https://pkg.go.dev/slices)
- [cmp package](https://pkg.go.dev/cmp)
- [io/fs package](https://pkg.go.dev/io/fs)
- [os/exec package](https://pkg.go.dev/os/exec)
- [path/filepath](https://pkg.go.dev/path/filepath)
