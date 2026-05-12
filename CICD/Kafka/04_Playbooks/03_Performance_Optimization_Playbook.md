---
tags: [cicd, kafka, playbook, performance, optimization, tuning, throughput, latency, benchmarking]
aliases: ["Performance Optimization", "Throughput Tuning", "Latency Tuning"]
status: stable
updated: 2026-05-09
---

# Performance Optimization Playbook

> [!summary] Goal
> Step-by-step guide to optimize Kafka throughput and latency. Covers benchmarking, identifying bottlenecks, producer/consumer/broker tuning, and network/disk optimization.

## Table of Contents

1. [Benchmarking Methodology](#benchmarking-methodology)
2. [Producer Optimization](#producer-optimization)
3. [Consumer Optimization](#consumer-optimization)
4. [Broker Optimization](#broker-optimization)
5. [Pitfalls](#pitfalls)

---

## Benchmarking Methodology

> [!info] Benchmarking
> Before optimizing, establish a baseline. Measure current throughput, latency (p50/p95/p99/p999), and resource utilization (CPU, disk, network, GC). Without a baseline, you can't measure improvement.

```bash
# 1. Create a benchmark topic
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic perf-test \
  --partitions 12 --replication-factor 3

# 2. Producer benchmark (baseline)
kafka-producer-perf-test \
  --topic perf-test \
  --num-records 5000000 \
  --record-size 1024 \
  --throughput -1 \
  --producer-props \
    bootstrap.servers=localhost:9092 \
    acks=all \
    batch.size=65536 \
    linger.ms=5 \
    compression.type=snappy

# Expected output:
# 5000000 records sent, 180000.0 records/sec (175.78 MB/sec),
#   3.20 ms avg latency, 25.10 ms max latency, 2.50 ms 50th, 6.80 ms 95th, 12.40 ms 99th

# 3. Consumer benchmark
kafka-consumer-perf-test \
  --topic perf-test \
  --messages 5000000 \
  --broker-list localhost:9092 \
  --group perf-group

# 4. System resource baseline
# Before test: record CPU, disk, network, GC
# During test: record peak utilization
# After test: compare performance to baseline
```

### Benchmark variations to try

```text
Test different configurations to identify the bottleneck:

  1. Record size: 100B, 1KB, 10KB, 100KB
     → Larger records = higher throughput (bytes/sec) but lower records/sec
     → Very small records = overhead dominates (per-record metadata)

  2. Ack mode: 0, 1, all
     → acks=0: highest throughput, no durability
     → acks=1: good durability, lower throughput
     → acks=all: best durability, network-bound (wait for replicas)

  3. Compression: none, snappy, lz4, zstd
     → Compression reduces network/storage at CPU cost
     → Snappy/lz4: low CPU cost, good for text data
     → Zstd: best compression, slightly higher CPU

  4. Partition count: 3, 6, 12, 24
     → More partitions = more parallelism, more overhead
     → Find the sweet spot (usually 2-4× brokers)
```

---

## Producer Optimization

### Step 1: Find the bottleneck

```text
If throughput is lower than expected, identify:
  - CPU: is the producer CPU-bound? (high user CPU)
  - Network: is the producer network-bound? (high send throughput)
  - Broker: is the broker the bottleneck? (broker metrics)
  - Batching: are batches full?

Check batch metrics via JMX:
  - batch-size-avg: should be close to batch.size
  - If avg is << batch.size: increase linger.ms or produce rate
  - buffer-exhausted-rate: producer can't keep up with broker
```

### Step 2: Tune batching

```properties
# Tuning batching parameters

# For high throughput (sacrifice latency):
batch.size=1048576       # 1 MB per batch
linger.ms=100            # Wait 100ms to fill large batches
compression.type=zstd    # Best compression ratio
buffer.memory=67108864   # 64 MB total buffer

# For balanced (moderate throughput + latency):
batch.size=65536         # 64 KB
linger.ms=10             # 10ms max wait
compression.type=snappy

# For low latency (sacrifice throughput):
batch.size=16384         # 16 KB
linger.ms=0              # Send immediately
compression.type=none    # No CPU overhead for compression
```

### Step 3: Compression tuning

```bash
# Test compression impact
for comp in none snappy lz4 zstd gzip; do
  kafka-producer-perf-test --topic perf-test \
    --num-records 1000000 --record-size 1024 --throughput -1 \
    --producer-props \
      bootstrap.servers=localhost:9092 \
      acks=1 \
      compression.type=$comp
done

# Typical results (text data):
# none:  180 MB/s,  75% CPU
# snappy: 310 MB/s, 45% CPU  ← FASTER than none! (less data to send)
# lz4:    320 MB/s, 40% CPU  ← fastest
# zstd:   280 MB/s, 30% CPU  ← best compression (70%+ reduction)
# gzip:   150 MB/s, 90% CPU  ← slowest
```

### Producer optimization checklist

```text
  [ ] batch.size set to at least 64KB (prefer 512KB-1MB for high throughput)
  [ ] linger.ms set to 5-100ms (not 0 unless latency-critical)
  [ ] compression.type set (snappy or lz4 as default, zstd for archival)
  [ ] buffer.memory large enough (at least 32MB, prefer 64MB+)
  [ ] enable.idempotence=true (required for EOS, sets acks=all)
  [ ] max.in.flight.requests.per.connection=5 with idempotence
  [ ] retries set high (MAX_INT with idempotence)
  [ ] max.request.size matches expected max message size
```

---

## Consumer Optimization

### Step 1: Find the bottleneck

```text
Consumer bottlenecks are usually:
  - Processing time: consumer code is slow (most common)
  - Fetch latency: network or broker overload
  - GC: consumer application GC pauses cause rebalance

Check consumer JMX metrics:
  - fetch-latency-avg: time to fetch from broker
  - records-consumed-rate: records processed per second
  - records-lag-max: if growing → consumer can't keep up
```

### Step 2: Tune fetch parameters

```properties
# For high throughput (batch consumption):
fetch.min.bytes=524288           # 512 KB minimum per fetch
fetch.max.wait.ms=500            # Wait for more data
max.partition.fetch.bytes=10485760  # 10 MB per partition
max.poll.records=1000            # Process 1000 records at once

# For low latency (near-real-time):
fetch.min.bytes=1                # Return immediately
fetch.max.wait.ms=50             # Wait max 50ms
max.partition.fetch.bytes=1048576   # 1 MB per partition
max.poll.records=100             # Process 100 records at once
```

### Step 3: Parallelize processing

```java
// Parallel processing within a single consumer
ExecutorService executor = Executors.newFixedThreadPool(4);

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    List<CompletableFuture<Void>> futures = new ArrayList<>();

    for (ConsumerRecord<String, String> record : records) {
        futures.add(CompletableFuture.runAsync(() -> process(record), executor));
    }

    // Wait for ALL records to complete
    CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
    consumer.commitSync();  // Commit AFTER all are processed
}
```

### Step 4: Rebalance tuning

```properties
# Minimize rebalance impact during performance testing:
session.timeout.ms=60000         # 60 seconds (tolerate longer GC pauses)
heartbeat.interval.ms=20000      # Heartbeat every 20s
max.poll.interval.ms=600000      # 10 min max processing time

# Use cooperative rebalancing:
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

---

## Broker Optimization

### Step 1: Disk optimization

```bash
# 1. Use multiple disks (JBOD)
# log.dirs=/data/kafka-0,/data/kafka-1,/data/kafka-2

# 2. Check disk performance
iostat -x 1  # Watch: %util, await, r/s, w/s
# If %util > 90%: disk is the bottleneck
# If await > 10ms: disk is slow (NVMe: < 2ms, SSD: < 5ms, HDD: > 10ms)

# 3. Mount with noatime
# /dev/nvme0n1 /data/kafka ext4 defaults,noatime 0 0

# 4. Check disk queue depth
# If queue depth is consistently > 2× disk's optimal queue: add more disks
```

### Step 2: Network optimization

```bash
# 1. Check network throughput
# Use iperf between producer and broker servers

# 2. Check for packet loss
netstat -s | grep -i "packet"

# 3. Increase socket buffers (sysctl)
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# 4. Use multiple network threads
# num.network.threads = 2 × CPU cores (e.g., 8 for 4-core)
```

### Step 3: Request handler tuning

```properties
# Broker request handler tuning
num.network.threads=8          # Network threads (accept connections)
num.io.threads=16              # I/O threads (process requests)
num.replica.fetchers=4         # Follower fetch threads

# Queue size
queued.max.requests=500        # Per-network-thread request queue
# If queue fills: clients get errors → increase queue or add brokers
```

### Broker optimization checklist

```text
  [ ] Multiple disks (JBOD) configured
  [ ] Disk mount: noatime, noop scheduler (or none for NVMe)
  [ ] vm.swappiness = 1 (or 0)
  [ ] vm.dirty_ratio and vm.dirty_background_ratio tuned
  [ ] num.network.threads and num.io.threads tuned for CPU cores
  [ ] Network socket buffers increased (sysctl)
  [ ] File descriptor limits increased
  [ ] JVM heap = 6-8 GB, G1GC
  [ ] Page cache not starved (heap < 25% of total RAM)
```

---

## Pitfalls

### OOM when batch is too large

If `batch.size` is set to 10 MB and you have 100 partitions, the producer buffers up to 1 GB of data. If `buffer.memory` is 32 MB, you get `BufferExhaustedException` or OOM. Ensure `batch.size × partitions × (max inflight + 1) ≤ buffer.memory`.

### Compression on single-record batches

With `linger.ms=0`, each batch contains one record. Compression on a single record is useless (the compressed output may be larger). If you need compression and low latency, set `linger.ms=1` or higher.

### Benchmark on a different workload than production

Benchmarks with 1 KB records give different results than production with 10 KB or 100 KB records. Always benchmark with the same record size, compression type, and throughput expected in production. Use production-like data (not random bytes — random data doesn't compress).

---

> [!question]- Interview Questions
>
> **Q: How do you identify whether the producer or broker is the bottleneck?**
> A: Check producer-side metrics: `buffer-exhausted-rate` (producer backlogged → broker is bottleneck) vs `request-latency-avg` (producer waits for broker). Check broker-side metrics: `RequestHandlerAvgIdlePercent` < 0.3 (broker CPU), `NetworkProcessorAvgIdlePercent` < 0.3 (broker network), disk `%util` (disk I/O). The bottleneck is where the metric is under pressure.
>
> **Q: How do you optimize Kafka for sustained high throughput?**
> A: (1) Increase partition count to match parallelism needs (2-4× broker count). (2) Tune producer batching: `batch.size=1MB`, `linger.ms=100`, `compression.type=zstd`. (3) Tune consumer: `fetch.min.bytes=1MB`, process in parallel. (4) Broker: multiple JBOD disks, `num.io.threads=16+`, 6-8 GB heap, rest to page cache. (5) Benchmark to find the true bottleneck. (6) Add brokers if traffic exceeds cluster capacity.

---

## Cross-Links

- [[CICD/Kafka/02_Core/04_Performance_Tuning]] for detailed tuning parameter reference
- [[CICD/Kafka/03_Advanced/A04_Monitoring_and_Observability]] for metrics collection
- [[CICD/Kafka/01_Foundations/03_Producers_Deep_Dive]] for producer internals
- [[CICD/Kafka/01_Foundations/04_Consumers_Deep_Dive]] for consumer internals
