---
tags: [cicd, kafka, playbook, troubleshooting, consumer-lag, connectivity, oom, disk-full, leader-not-available]
aliases: ["Troubleshooting", "Troubleshoot Kafka", "Kafka Debugging"]
status: stable
updated: 2026-05-09
---

# Troubleshoot Consumer Lag

> [!summary] Goal
> Diagnose and fix consumer lag, connectivity issues, OOM, disk-full errors, and LEADER_NOT_AVAILABLE. Step-by-step guides for the most common production Kafka issues.

## Table of Contents

1. [Consumer Lag Spikes](#consumer-lag-spikes)
2. [Connectivity Issues](#connectivity-issues)
3. [Common Errors](#common-errors)
4. [Pitfalls](#pitfalls)

---

## Consumer Lag Spikes

> [!info] Consumer lag spike
> Consumer lag spikes when consumers can't process messages as fast as producers produce. Identify the bottleneck: consumer processing time, broker fetch latency, rebalances, or client-side GC pauses.

### Step-by-step diagnosis

```bash
# 1. Check current lag for ALL consumer groups
kafka-consumer-groups --bootstrap-server localhost:9092 --all-groups --describe

# 2. Identify groups with LAG > threshold
# Focus on: max-lag, which partitions are lagging, rate of change

# 3. Check consumer group state
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group my-group --describe --state

# Possible states: Stable, PreparingRebalance, Dead, Empty
# "PreparingRebalance" → rebalance is ongoing (consumers not processing)

# 4. Get consumer member details
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group my-group --describe --members --verbose
# Shows: member-id, host, client-id, assigned partitions, rack
```

### Root causes and fixes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| **Steady upward lag** | Consumer processing too slow | Increase consumers (<= partitions), optimize processing |
| **Step-function increase** | New partition added | Add more consumers, or increase consumer parallelism |
| **Spike then steady** | Transient broker overload | Check broker metrics (IO wait, GC), add brokers |
| **Spike then zero** | Consumer restarted, caught up | GC pause (check GC logs), or deployment restart |
| **Every 30-60s spike** | Rebalance in progress | Check `session.timeout.ms`, network stability, GC |
| **Certain partitions only** | Partition skew (hot partition) | Check partition distribution, add partitions |

### Processing bottleneck analysis

```bash
# 1. Check consumer processing time (app metrics)
# Look for: avg process time per record, p99 process time

# 2. Check consumer fetch latency
# High fetch latency → broker overload or network issue
# Low fetch latency + high process time → consumer bottleneck

# 3. GC logs (JVM consumer)
# -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCTimeStamps
# Look for: long GC pauses (> 1s), frequent Full GC

# 4. Thread dump analysis
jstack <consumer-pid> > threaddump.txt
# Look for: blocked threads in processing code
```

### Fix: Increase consumers

```bash
# If partitions = N and consumers = M < N:
# Add more consumers (up to N) to distribute load

# Check partition count first
kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic orders

# If partitions = 6 and consumers = 2:
# Add 4 more consumers for full parallelism
```

### Fix: Optimize processing

```java
// Before: sequential processing (one record at a time)
for (ConsumerRecord<String, String> record : records) {
    process(record);  // Slow!
}

// After: batch processing (process all records at once)
List<CompletableFuture<Void>> futures = new ArrayList<>();
for (ConsumerRecord<String, String> record : records) {
    futures.add(CompletableFuture.runAsync(() -> process(record)));
}
CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
// Commit after ALL records in the batch are processed
consumer.commitSync();
```

---

## Connectivity Issues

### Broker unreachable

```bash
# 1. Check network connectivity
nc -zv broker-host 9092
telnet broker-host 9092

# 2. Check if broker is alive
kafka-broker-api-versions --bootstrap-server localhost:9092

# 3. Check listener config
# Common issue: advertised.listeners doesn't match the client's address
# If client resolves broker-1.local → 10.0.0.1 but broker listens on 0.0.0.0:9092:
#   advertised.listeners=PLAINTEXT://broker-1.local:9092
#   listener.security.protocol.map=PLAINTEXT:PLAINTEXT

# 4. Check firewall/security groups
# Kafka uses ephemeral ports for inter-broker connections
# Default: brokers use ports 9092 (client) + random (inter-broker)
# Better: set listeners explicitly
#   listeners=PLAINTEXT://0.0.0.0:9092,INTERNAL://0.0.0.0:9093
#   advertised.listeners=PLAINTEXT://public-ip:9092,INTERNAL://broker-1:9093
```

### Connection refused

```text
Connection refused means:
  - Broker is NOT running, OR
  - Broker is running on a different port, OR
  - Firewall is blocking the port

Check:
  - `ps aux | grep kafka` — is the process running?
  - `ss -tlnp | grep 9092` — is anything listening?
  - `docker logs broker` — any errors on startup?
```

### TLS/SSL handshake failures

```bash
# Enable SSL debug logging on the client:
# -Djavax.net.debug=ssl:handshake:verbose

# Common causes:
# 1. Truststore doesn't contain the CA cert
# 2. Hostname verification fails: ssl.endpoint.identification.algorithm=
#    (set to empty string to disable, but this reduces security)
# 3. TLS version mismatch: ssl.enabled.protocols=TLSv1.2
# 4. Cipher suite mismatch

# Verify keystore/truststore
keytool -list -keystore client.truststore.jks -storepass changeit
keytool -list -keystore client.keystore.jks -storepass changeit
```

---

## Common Errors

### LEADER_NOT_AVAILABLE

```text
Error: LEADER_NOT_AVAILABLE

Meaning:
  - The partition leader is not available (leader election in progress or failed)
  - This is transient during:
    a) Initial topic creation (wait for leader election)
    b) Leader failover (broker crashed, new leader being elected)
    c) Preferred leader election (controller reassigning leaders)

Debug:
  1. Check UnderReplicatedPartitions and OfflinePartitionsCount
  2. Check broker logs for leader election errors
  3. Check controller logs

Fix:
  - Usually transient — retry with backoff
  - If persistent: check broker health, ISR state, unf clean leader election
```

### NOT_ENOUGH_REPLICAS

```text
Error: NOT_ENOUGH_REPLICAS (producer) or NOT_ENOUGH_REPLICAS_AFTER_APPEND

Meaning:
  - min.insync.replicas > ISR size
  - OR replication factor > number of available brokers

Debug:
  1. Check ISR: kafka-topics --describe --topic my-topic
  2. Check broker count: kafka-broker-api-versions --bootstrap-server
  3. Check min.insync.replicas config

Fix:
  - Add more brokers (if fewer than replication factor)
  - Increase ISR: wait for replicas to catch up
  - Temporarily reduce min.insync.replicas (if service degradation is acceptable)
```

### Connection refused / Timeout

```text
Error: TimeoutException: Failed to update metadata after 60000 ms

Meaning:
  - Producer can't connect to any broker
  - Or can connect but the metadata request times out

Debug:
  1. Network connectivity test (nc, telnet)
  2. Check bootstrap.servers config
  3. Check if brokers have restarted (advertised.listeners change?)
  4. Check DNS resolution: hostname → correct IP

Fix:
  - Fix bootstrap.servers or network/Firewall
  - If brokers restarted with different listeners, update client config
```

### OutOfMemoryError

```text
Error: java.lang.OutOfMemoryError: Java heap space
       java.lang.OutOfMemoryError: Direct buffer memory

Broker OOM:
  - Broker heap too small: increase KAFKA_HEAP_OPTS
  - Too many partitions: reduce partition count or increase brokers
  - Too many concurrent connections: limit with max.connections
  - Direct memory: increase -XX:MaxDirectMemorySize

Producer OOM:
  - buffer.memory too large for heap: reduce buffer.memory
  - Messages too large: increase max.request.size OR send smaller messages

Consumer OOM:
  - fetch.max.bytes too large: reduce fetch.max.bytes
  - Processing holds references to records: process and release faster
```

### Disk full

```bash
# 1. Check disk usage
df -h /var/lib/kafka

# 2. Identify largest partitions
du -sh /var/lib/kafka/data/* | sort -rh | head -10

# 3. Check partition size by topic
kafka-log-dirs --bootstrap-server localhost:9092 \
  --describe --topic-list orders | grep "{\"version\""

# 4. Reduce retention (takes effect immediately)
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics --entity-name orders \
  --alter --add-config retention.ms=86400000  # 1 day

# 5. Reduce segment retention bytes
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics --entity-name orders \
  --alter --add-config retention.bytes=10737418240  # 10 GB

# 6. Trigger immediate cleanup
kafka-log-cleaner.sh --bootstrap-server localhost:9092
```

---

## Pitfalls

### Metadata parsing error after upgrade

After upgrading Kafka, if `inter.broker.protocol.version` or `log.message.format.version` isn't updated, messages may not be readable. Always set these correctly during upgrades. In KRaft mode, check `metadata.version`.

### Port collision with ZooKeeper

ZooKeeper and Kafka both default to port 2181 (ZK client) and 9092 (Kafka). If running both on the same host, ensure different ports. ZooKeeper: `clientPort=2181`. Kafka: `listeners=PLAINTEXT://:9092`.

---

> [!question]- Interview Questions
>
> **Q: What's the first thing you check when consumer lag spikes?**
> A: Check if a rebalance is happening (`kafka-consumer-groups --describe --state`). If the group is in `PreparingRebalance`, consumers have stopped processing. If the group is `Stable`, check whether lag is increasing across all partitions (consumer processing bottleneck) or specific partitions (partition skew / hot partition).
>
> **Q: How do you debug LEADER_NOT_AVAILABLE?**
> A: Check UnderReplicatedPartitions and OfflinePartitionsCount metrics. If UnderReplicatedPartitions > 0, replicas are lagging — wait for replication or investigate disk/network. If OfflinePartitionsCount > 0, no leader is available — check if brokers are alive and the controller is functioning. LEADER_NOT_AVAILABLE is usually transient; the client should retry with exponential backoff.

---

## Cross-Links

- [[CICD/Kafka/02_Core/04_Performance_Tuning]] for performance tuning metrics
- [[CICD/Kafka/02_Core/03_Consumer_Group_Rebalancing]] for rebalance troubleshooting
- [[CICD/Kafka/03_Advanced/A04_Monitoring_and_Observability]] for metrics collection
