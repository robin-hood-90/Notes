---
tags: [c, core, gdb, debugging, breakpoints, core-dumps, reverse-debugging]
aliases: ["GDB", "Debugging", "GNU Debugger", "Breakpoints", "Core Dumps", "Reverse Debugging"]
status: stable
updated: 2026-05-09
---

# Debugging with GDB

> [!summary] Goal
> Debug C programs effectively with GDB: set breakpoints, inspect memory, navigate stack frames, analyze core dumps, and debug multi-process/multi-threaded programs. Essential for finding segfaults, logic errors, and memory corruption.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Breakpoints](#breakpoints)
3. [Inspecting State](#inspecting-state)
4. [Core Dump Analysis](#core-dump-analysis)
5. [Debugging Multiple Processes](#debugging-multiple-processes)
6. [GDB Automation](#gdb-automation)
7. [Pitfalls](#pitfalls)

---

## Getting Started

> [!info] GDB
> The GNU Debugger (GDB) allows you to inspect a program's state as it runs — step through code, examine variables, set breakpoints, and analyze crashes. Compile with `-g` to include debug symbols (variable names, line numbers, source references).

```bash
# Compile with debug symbols
gcc -g -O0 program.c -o program

# Start GDB
gdb ./program

# Run with arguments
gdb --args ./program arg1 arg2

# GDB trick: run GDB on a core dump
gdb ./program core

# Common GDB flags
gdb -q ./program                # Quiet mode (no banner)
gdb -ex "set pagination off" ./program  # Suppress page breaks
```

### Basic session

```bash
gdb ./program
(gdb) break main          # Set breakpoint at main()
(gdb) run                 # Run program (stops at main)
(gdb) next                # Step over (doesn't enter function calls)
(gdb) step                # Step into (enters function calls)
(gdb) continue            # Continue until next breakpoint
(gdb) print x             # Print variable x
(gdb) quit                # Exit GDB
```

### Compilation for debugging

```bash
# Debug build (recommended)
gcc -g -O0 -Wall -Wextra program.c -o program

# With address sanitizer (find UB + memory bugs during debugging)
gcc -g -O0 -fsanitize=address -fsanitize=undefined program.c -o program

# Minimum symbols for release debugging
gcc -g1 program.c -o program   # Less symbol info, smaller binary
```

---

## Breakpoints

### Breakpoint types

| Command | Effect |
|---------|--------|
| `break main` | Break at function `main` |
| `break 42` | Break at line 42 |
| `break file.c:42` | Break at line 42 of file.c |
| `break func if x > 5` | Conditional breakpoint |
| `break *0x4004c0` | Break at memory address |
| `watch x` | Break when x changes |
| `rwatch x` | Break when x is read |
| `catch fork` | Break on fork() call |

### Conditional breakpoints

```bash
# Break at line 100 only when i == 42
(gdb) break 100 if i == 42

# Break when a condition changes
(gdb) watch x if x > 100

# Modify a condition
(gdb) condition 1 i == 99   # Change breakpoint 1's condition
(gdb) condition 1            # Remove condition from breakpoint 1
```

### Managing breakpoints

```bash
(gdb) info breakpoints       # List all breakpoints
(gdb) disable 1              # Disable breakpoint 1 (keep it)
(gdb) enable 1               # Re-enable
(gdb) delete 1               # Remove permanently
(gdb) ignore 1 100           # Skip breakpoint 1 for 100 hits
```

---

## Inspecting State

### Variables and memory

```bash
(gdb) print x                # Print variable
(gdb) print &x               # Print address
(gdb) print *ptr             # Dereference pointer
(gdb) print array[0]@10      # Print 10 elements of array
(gdb) print /x x             # Print in hexadecimal
(gdb) print (char*)ptr       # Cast and print

# Examining memory directly
(gdb) x/10x ptr              # 10 hex words at ptr
(gdb) x/20c ptr              # 20 characters
(gdb) x/s ptr                # Null-terminated string
(gdb) x/i $rip               # Disassemble current instruction

# Format specifiers: x(hex), d(decimal), c(char), s(string), i(instruction)
```

### Stack navigation

```bash
# After a crash or breakpoint
(gdb) backtrace              # Show call stack (bt)
(gdb) backtrace full         # Show stack with local variables
(gdb) frame 2                # Move to frame 2 (0 = innermost)
(gdb) info locals            # Show local variables in current frame
(gdb) info args              # Show function arguments
(gdb) up                     # Move up one frame (toward caller)
(gdb) down                   # Move down one frame
```

### Thread inspection

```bash
(gdb) info threads           # List all threads
(gdb) thread 2               # Switch to thread 2
(gdb) thread apply all bt    # Backtrace for all threads
(gdb) thread apply all bt full  # Full backtrace for all threads
```

---

## Core Dump Analysis

> [!info] Core dump
> A core dump is a file containing the memory contents of a process at the moment of a crash. You can load it in GDB to examine the program state without running the program. This is essential for debugging crashes that are hard to reproduce.

### Enabling core dumps

```bash
# Allow core dumps
ulimit -c unlimited          # Set in shell before running program
# Check limit
ulimit -c                    # Should say "unlimited"

# Core dump location (on Linux)
# /var/lib/systemd/coredump/ or current directory as "core" or "core.PID"

# Read a core dump
gdb ./program /path/to/core
(gdb) bt                    # Show stack at crash
(gdb) info registers        # Show CPU registers at crash
(gdb) frame 0               # Go to crash frame
(gdb) info locals           # Local variables at crash
```

### Example crash analysis

```bash
# Program crashes with segfault
gdb ./program core
(gdb) bt
#0  0x0000555555554712 in process_data (arr=0x0, n=100) at program.c:23
#1  0x00005555555546a0 in main () at program.c:45

(gdb) frame 0
(gdb) info locals
# arr = 0x0                  # NULL pointer — caused the crash
(gdb) print n
# 100                        # Trying to access arr[0] through arr[99]

# Fix: check for NULL before accessing arr in process_data()
```

---

## Debugging Multiple Processes

```bash
# Follow fork/exec
(gdb) set follow-fork-mode child    # Debug the child after fork
(gdb) set follow-fork-mode parent   # Debug the parent (default)

# Detach from one and debug the other
(gdb) set detach-on-fork on         # Debug one, let the other run (default)
(gdb) set detach-on-fork off        # Both are under GDB control

# Debug multiple processes
(gdb) info inferiors               # List all processes
(gdb) inferior 2                   # Switch to process 2
```

### Debugging a running process

```bash
# Attach to a running process by PID
gdb -p 1234

# Or inside GDB
(gdb) attach 1234
(gdb) detach
```

---

## GDB Automation

### .gdbinit — automatic setup

```bash
# ~/.gdbinit or ./.gdbinit (project-specific)
set pagination off
set confirm off
set print pretty on
set print elements 500        # Show more array elements

# Define custom commands
define print_arr
    p *($arg0)@$arg1
end

# Aliases
alias bt = backtrace
```

### GDB scripts

```python
# save_command.gdb — GDB commands in a file
break main
run
next 3
print x
continue

# Run: gdb -batch -x commands.gdb ./program
```

### Reverse debugging (recording)

```bash
# GDB can record execution and step backward
(gdb) record                 # Start recording
(gdb) run                    # Run program
(gdb) reverse-step           # Step backward
(gdb) reverse-next           # Step over backward
(gdb) reverse-continue       # Continue backward until breakpoint
```

---

## Pitfalls

### Debugging optimized code (-O2)

Optimized code can be misleading in GDB: variables disappear, line numbers jump, inlined functions don't appear in backtraces. Always debug with `-O0` first. Use `-Og` if you need some optimization.

### ASLR complicates debugging

Address Space Layout Randomization changes addresses each run, making breakpoints at fixed addresses unreliable. Break by function/line instead. (GDB handles ASLR for symbolic breakpoints — only affects hardware breakpoints.)

### Missing symbols from stripped binaries

```bash
# Stripped binary — no symbols
gdb ./program     # (gdb) bt — shows only addresses, no function names
# Compile with -g for debugging, strip for production
```

### `watch` performance

Hardware watchpoints (limited, fast) are used when possible. Software watchpoints (unlimited, 1000× slower) kick in for complex conditions. Don't use `watch` on large structures in tight loops.

---

> [!question]- Interview Questions
>
> **Q: How do you debug a segfault with GDB?**
> A: Compile with `-g -O0`. Run `gdb ./program`, then `run`. When the crash happens, type `bt` (backtrace) to see the call stack. Use `frame 0` to see the crash frame, then `info locals` to see variable values. Often the crash is a NULL pointer or an out-of-bounds access.
>
> **Q: What is the difference between `next` and `step` in GDB?**
> A: `next` executes the current line and stops at the next line in the same function (it steps OVER function calls). `step` executes the current line and stops — if the line contains a function call, it steps INTO that function. Use `next` to skip library calls, `step` to follow your own function calls.
>
> **Q: How do you debug a core dump?**
> A: Enable core dumps with `ulimit -c unlimited`. Run the program until it crashes. Run `gdb ./program core`. Use `bt` to see the call stack at crash, `frame` to navigate, `info locals` to see variable values. The core dump contains the full program state at the moment of the crash.
>
> **Q: How do you debug a program that crashes only in release mode?**
> A: Release-mode bugs are often caused by UB that optimization exposes. Compile with `-O2 -g -fsanitize=address -fsanitize=undefined` to get debug symbols with sanitizers. If you can't use sanitizers, add logging, use `assert()`, and add `volatile` to prevent optimization of specific variables.
>
> **Q: What is conditional breakpoint and when would you use it?**
> A: A conditional breakpoint stops only when a condition is true: `break 42 if i == 1000`. Use it when a bug appears only on a specific iteration of a loop — instead of pressing `continue` 999 times, set the condition to stop at the failing iteration.

---

## Cross-Links

- [[C/02_Core/06_Undefined_Behavior_and_Memory_Safety]] for UB detection
- [[C/04_Playbooks/01_Debug_Segfaults_and_Invalid_Memory_Access]] for segfault debugging
- [[C/04_Playbooks/02_Use_Sanitizers_ASan_UBSan_TSan]] for sanitizer-based debugging
- [[C/04_Playbooks/03_Valgrind_Leaks_and_Heap_Corruption]] for heap debugging
- [[C/03_Advanced/08_Performance_Profiling_and_Optimization]] for profiling (perf)
