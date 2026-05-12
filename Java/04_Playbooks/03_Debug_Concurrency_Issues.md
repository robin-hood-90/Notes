---
tags: [java, playbook, concurrency, deadlock, thread-dump, race-condition, loom]
aliases: ["Debug Concurrency Issues", "Thread Dump Analysis", "Deadlock Detection", "Race Conditions", "Loom Debugging"]
status: stable
updated: 2026-05-09
---

# Playbook: Debug Concurrency Issues

> [!summary] Goal
> Diagnose and fix concurrency problems: deadlocks, race conditions, thread starvation, and lock contention. Use thread dumps, JFR, and JMC to identify issues in both platform threads and virtual threads (Loom).

## Table of Contents

1. [Thread Dump Analysis](#thread-dump-analysis)
2. [Deadlock Detection](#deadlock-detection)
3. [Race Condition Patterns](#race-condition-patterns)
4. [Virtual Thread Debugging](#virtual-thread-debugging)
5. [Pitfalls](#pitfalls)

---

## Thread Dump Analysis

> [!info] Thread dump
> A thread dump shows the stack trace of every live thread. Taken every 5-10 seconds across several samples, it reveals what the application is doing over time. Tools: `jstack <pid>`, `kill -3 <pid>`, `jcmd <pid> Thread.print`, or JMC (Java Mission Control).

```bash
# Take thread dumps (Linux)
jstack -l <pid> > dump1.txt
sleep 5
jstack -l <pid> > dump2.txt

# Or continuously (for detecting stuck threads)
for i in {1..10}; do
    jstack <pid> > "dump_$i.txt"
    sleep 2
done

# With jcmd (same output, different tool)
jcmd <pid> Thread.print > dump.txt
```

### Reading a thread dump

```text
# Thread dump key sections:

"http-thread-1" #12 prio=5 os_prio=0 cpu=15.63ms elapsed=123.45s
  java.lang.Thread.State: BLOCKED
    at com.example.DataService.getData(DataService.java:45)
    - waiting to lock <0x00000007ff5f8d10> (a java.lang.Object)
    at com.example.RequestHandler.handle(RequestHandler.java:23)

"http-thread-2" #13 prio=5 os_prio=0 cpu=0.63ms elapsed=123.45s
  java.lang.Thread.State: BLOCKED
    at com.example.AuthService.validate(AuthService.java:67)
    - waiting to lock <0x00000007ff5f8d10> (a java.lang.Object)

  Locked ownable synchronizers:
    - <0x00000007ff5f8d10> (a java.util.concurrent.locks.ReentrantLock$NonfairSync)

### State analysis:
# RUNNABLE    → actively executing (may be CPU-bound or doing non-blocking I/O)
# BLOCKED     → waiting for a monitor lock (synchronized or Lock)
# WAITING     → waiting on Object.wait(), LockSupport.park(), or condition
# TIMED_WAITING → waiting with timeout (Thread.sleep(), wait(timeout), parkNanos())
```

### What each thread state means

| State | Meaning | Action |
|-------|---------|--------|
| **RUNNABLE** | Thread is executing or ready to execute | Normal; many RUNNABLE threads at high CPU → optimize hotspots |
| **BLOCKED** | Waiting for a monitor lock | Check lock contention; optimize synchronized blocks |
| **WAITING** | Waiting indefinitely for another thread | `Object.wait()`, `LockSupport.park()` — normal for thread pools |
| **TIMED_WAITING** | Waiting with timeout | `Thread.sleep()`, `wait(timeout)` — normal |
| Many threads BLOCKED on the same lock | Lock contention | Reduce hold time, use read-write lock, split lock |

---

## Deadlock Detection

> [!info] Deadlock
> A deadlock occurs when two or more threads each hold locks that the others need. None can proceed. The JVM detects deadlocks at thread dump time and reports them.

```bash
# Jstack automatically detects deadlocks
jstack -l <pid>

# Output:
# Found one Java-level deadlock:
# =============================
# "thread-2":
#   waiting to lock <0x...> (a Account)
#   held by "thread-1"
# "thread-1":
#   waiting to lock <0x...> (a Account)
#   held by "thread-2"
#
# Found 1 deadlock.
```

### Manual deadlock detection

```java
// Programmatic deadlock detection
ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();
long[] deadlockedIds = threadBean.findDeadlockedThreads();
if (deadlockedIds != null) {
    ThreadInfo[] infos = threadBean.getThreadInfo(deadlockedIds, true, true);
    for (ThreadInfo info : infos) {
        System.err.println("Deadlocked thread: " + info.getThreadName());
    }
}
```

### Deadlock prevention patterns

```java
// ❌ Deadlock-prone: lock ordering varies
public void transfer(Account from, Account to, double amount) {
    synchronized (from) {
        synchronized (to) {   // If another thread calls transfer(to, from) → deadlock!
            from.debit(amount);
            to.credit(amount);
        }
    }
}

// ✅ Fixed: always lock in System.identityHashCode order
public void transfer(Account a, Account b, double amount) {
    Object first = System.identityHashCode(a) < System.identityHashCode(b) ? a : b;
    Object second = System.identityHashCode(a) < System.identityHashCode(b) ? b : a;
    
    synchronized (first) {
        synchronized (second) {
            a.debit(amount);
            b.credit(amount);
        }
    }
}

// ✅ Alternative: ReentrantLock with tryLock
public boolean transfer(Account from, Account to, double amount) {
    if (from.lock.tryLock()) {
        try {
            if (to.lock.tryLock()) {
                try {
                    from.debit(amount);
                    to.credit(amount);
                    return true;
                } finally { to.lock.unlock(); }
            }
        } finally { from.lock.unlock(); }
    }
    return false;   // Could not acquire both locks
}
```

---

## Race Condition Patterns

### Check-then-act

```java
// ❌ Race: two threads can both see count > 0 and both proceed
if (count > 0) {
    count--;                          // count may have changed!
}

// ✅ Fix: atomic operation
synchronized (this) {
    if (count > 0) {
        count--;
    }
}

// Or with AtomicInteger:
if (count.decrementAndGet() < 0) {
    count.incrementAndGet();          // Compensate
    throw new RuntimeException("No items");
}
```

### Put-if-absent

```java
// ❌ Race: two threads can both get null and both put
if (!map.containsKey(key)) {
    map.put(key, value);              // Second put overwrites first!
}

// ✅ Fix: ConcurrentHashMap.putIfAbsent
map.putIfAbsent(key, value);

// ✅ Fix: synchronized
synchronized (map) {
    if (!map.containsKey(key)) {
        map.put(key, value);
    }
}
```

---

## Virtual Thread Debugging

```java
// Virtual thread stacks look different — they show both VT and carrier thread
// "ForkJoinPool-1-worker-1" #41
// java.lang.Thread.State: RUNNABLE
//   at com.example.Service.process(Service.java:25)
//   ...
//   CarrierThread: "ForkJoinPool-1-worker-1" #41
//     VirtualThread: "my-virtual-thread" #42
```

### Debugging with jcmd

```bash
# Virtual thread dump (prints all virtual threads)
jcmd <pid> Thread.dump_to_file -format=json vthreads.json

# Includes virtual thread mounts and unmounts
jcmd <pid> JFR.start name=vthreads settings=profile
jcmd <pid> JFR.dump name=vthreads filename=vthreads.jfr
```

### Common VT issues

```text
Pinning detection:
  - If you see carrier threads blocked when VTs should be unmounting
  - Check for synchronized blocks in the stack trace
  - Use `-Djdk.tracePinnedThreads=short` to log pinning events

Mount/unmount overhead:
  - If VT count is very high and CPU is high in mount/unmount
  - Check for very short-lived VTs (〈 1ms) — overhead dominates
```

---

## Pitfalls

### Taking only one thread dump

A single thread dump shows a snapshot, not a trend. Multiple dumps seconds apart reveal whether threads are making progress. A thread that appears in RUNNABLE across all dumps in the same method is likely stuck in a hot loop.

### Ignoring lock order

Deadlocks happen when different threads acquire locks in different orders. Always establish a global lock ordering and enforce it. Even if a deadlock hasn't happened yet, the code is broken — it's just waiting for the right timing.

### Thread dump in high-CPU vs low-CPU incidents

In high-CPU incidents, threads are RUNNABLE and you need to find the hottest methods (use `async-profiler` or `perf`). Thread dumps alone won't show CPU hotspots — they show the current stack, not where CPU is being spent. For high CPU, use JFR or async-profiler instead.

---

## Cross-Links

- [[Java/02_Core/01_Concurrency_Threads_and_Executors]] for concurrency fundamentals
- [[Java/03_Advanced/01_CompletableFuture_and_Structured_Concurrency]] for async composition
- [[Java/03_Advanced/03_JVM_Tooling_JFR_JStack_JMap]] for JFR profiling
- [[Java/03_Advanced/06_Virtual_Threads_and_Structured_Concurrency]] for VT debugging
- [[Java/04_Playbooks/01_Diagnose_High_CPU_or_Latency]] for CPU-specific debugging
