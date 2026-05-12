---
tags: [system-design, core, consistency, replication, consensus, cap, raft, paxos]
aliases: ["Consistency", "Replication", "Consensus", "CAP Theorem", "Raft", "Paxos", "Quorum"]
status: stable
updated: 2026-05-09
---

# Consistency, Replication, and Consensus

> [!summary] Goal
> Choose the right consistency model, replication strategy, and consensus algorithm for your distributed system. Understand the tradeoffs between strong consistency, availability, and performance.

## Table of Contents

1. [Consistency Models](#consistency-models)
2. [Replication Strategies](#replication-strategies)
3. [Quorum and Hinted Handoff](#quorum-and-hinted-handoff)
4. [Consensus Algorithms](#consensus-algorithms)
5. [Decision Tree](#decision-tree)
6. [Pitfalls](#pitfalls)

---

## Consistency Models

```mermaid
flowchart TD
    A["Consistency model"] --> B{How strict?}
    B -->|"Strict"| C["Strong consistency<br/>All reads see latest write"]
    B -->|"Medium"| D["Causal consistency<br/>Causally related ops in order"]
    B -->|"Relaxed"| E["Eventual consistency<br/>Replicas converge over time"]
    C --> F["Google Spanner, ZooKeeper, etcd"]
    D --> G["Vector clocks, CRDTs"]
    E --> H["DNS, DynamoDB, Cassandra"]
```

| Model | Guarantee | Latency | Available during partition? | Example |
|-------|-----------|:-------:|:--------------------------:|---------|
| **Strong** | Read returns the latest write | Higher | No (CP) | Spanner, ZK, etcd |
| **Read-your-writes** | Client sees its own writes | Good | Yes (AP) | Session consistency |
| **Monotonic reads** | Reads never go back in time | Good | Yes | User timeline |
| **Causal** | Causally related ops in order | Medium | Yes (AP) | Vector clocks |
| **Eventual** | All replicas eventually converge | Best | Yes (AP) | DNS, DynamoDB |
| **Weak** | No ordering guarantees | Best | Yes | In-memory cache |

---

## Replication Strategies

```mermaid
flowchart TD
    A["Replication strategy"] --> B{Leader or no leader?}
    B -->|"Single leader"| C["One node accepts writes<br/>Others replicate"]
    B -->|"Multi leader"| D["Multiple nodes accept writes<br/>Cross-replicate"]
    B -->|"Leaderless"| E["Any node accepts writes<br/>Read repair + hinted handoff"]
    C --> F["MySQL replication, PostgreSQL streaming"]
    C --> G["Pros: simple, no conflicts"]
    C --> G["Cons: leader is SPOF"]
    D --> H["DynamoDB Global Tables, multi-region"]
    D --> I["Pros: low latency everywhere"]
    D --> I["Cons: write conflicts"]
    E --> J["Cassandra, Riak"]
    E --> K["Pros: high availability"]
    E --> K["Cons: read repair overhead"]
```

### Synchronous vs asynchronous replication

```mermaid
sequenceDiagram
    participant App as Application
    participant L as Leader
    participant F1 as Follower 1
    participant F2 as Follower 2

    Note over L,F2: Synchronous replication
    App->>L: Write
    L->>F1: Replicate
    F1-->>L: Ack
    L->>F2: Replicate
    F2-->>L: Ack
    L-->>App: Write confirmed
    
    Note over L,F2: Asynchronous replication
    App->>L: Write
    L-->>App: Write confirmed
    L->>F1: Replicate (async)
    L->>F2: Replicate (async)
```

| Aspect | Synchronous | Asynchronous |
|--------|:-----------:|:------------:|
| **Data durability** | ✅ All replicas confirmed | ⚠️ Leader failure = data loss |
| **Write latency** | Higher (wait for replicas) | Lower (write to leader only) |
| **Read staleness** | None (all up to date) | Possible (replicas lag) |
| **Availability** | Lower (replica failure blocks writes) | Higher (writes succeed even if replica is down) |
| **Best for** | Strong consistency requirements | High throughput, eventual consistency OK |

---

## Quorum and Hinted Handoff

### Quorum read/write

```mermaid
flowchart LR
    subgraph Cluster["3-node cluster"]
        N1["Node A<br/>v3"]
        N2["Node B<br/>v3"]
        N3["Node C<br/>v2 (stale)"]
    end
    
    W["Write: W=2<br/>Must write to 2 nodes"]
    R["Read: R=2<br/>Must read from 2 nodes<br/>Pick latest version"]
    
    W --> N1
    W --> N2
    R --> N2
    R --> N3
    N3 -->|"v2"| R
    N2 -->|"v3"| R
    R -->|"Return v3 (latest)"| C["Client"]
```

| Quorum setting | Consistency guarantee | Failure tolerance |
|:--------------:|:---------------------:|:----------------:|
| W = 1, R = 1 | No consistency | 0 node failures |
| W = 2, R = 2 (N=3) | Strong consistency | 1 node failure |
| W = 2, R = 1 | Write-heavy — reads may be stale | 1 write node failure |
| W = 1, R = 2 | Read-heavy — reads are consistent | 1 read node failure |
| W = N, R = 1 | Full consistency but no write failure tolerance | — |

> [!tip] For strong consistency with fault tolerance in a 3-node cluster, use `W = R = 2`. This ensures the read set and write set overlap — at least one node in the read set has the latest write.

### Hinted handoff

When a replica is unavailable during a write, another node accepts the write "on behalf" of the downed node and stores a **hint**. When the downed node recovers, the hint is replayed.

```mermaid
sequenceDiagram
    participant C as Client
    participant N1 as Node A (coordinator)
    participant N2 as Node B (down)
    participant N3 as Node C

    C->>N1: Write to key k (replicas: A, B, C)
    N1->>N2: Write (timeout — B is down)
    N1->>N3: Write (success)
    N1-->>C: Write accepted (W=2, with hint)
    Note over N1: Stores hint: "key k → Node B"
    Note over N2: Node B recovers
    N1->>N2: Replay hint for key k
    N2-->>N1: Ack
    N1->>N1: Delete hint
```

---

## Consensus Algorithms

Consensus algorithms allow a group of nodes to agree on a value despite failures. Used for leader election, log replication, and distributed coordination.

```mermaid
sequenceDiagram
    participant C1 as Candidate 1
    participant C2 as Candidate 2
    participant C3 as Voter 3
    
    Note over C1,C3: Leader election — Raft
    C1->>C2: RequestVote (term=2)
    C1->>C3: RequestVote (term=2)
    C2-->>C1: Vote granted
    C3-->>C1: Vote granted
    Note over C1: Becomes leader for term 2
    C1->>C2: AppendEntries (heartbeat)
    C1->>C3: AppendEntries (heartbeat)
```

| Algorithm | Approach | Used by | Performance |
|-----------|----------|---------|:-----------:|
| **Raft** | Leader-based, understandable | etcd, Consul, TiKV | ~10-50K ops/sec |
| **Paxos** | Symmetric, harder to implement | Google Chubby, Spanner | Similar to Raft |
| **Zab** | Leader-based, atomic broadcast | ZooKeeper | ~10K ops/sec |
| **Multi-Paxos** | Optimized Paxos with leader | Cassandra (optional) | Higher throughput |

### Raft in practice

```text
Raft guarantees:
  1. Leader Election: exactly one leader per term
  2. Log Replication: entries are replicated to a majority
  3. Safety: if two logs agree on an entry, all earlier entries also agree

Nodes spend most time in normal operation:
  - Leader accepts client writes
  - Leader replicates to followers
  - Followers are passive (apply entries, respond to heartbeats)
  - If follower doesn't hear from leader → start election

Failure handling:
  - Leader failure: new election in ~150-300ms
  - Network partition: majority side continues, minority is unavailable
  - Split-brain impossible: at most one leader per term
```

---

## Decision Tree

```mermaid
flowchart TD
    A["How to replicate data?"] --> B{Consistency required?}
    B -->|"Strong consistency"| C["Single leader + synchronous replication"]
    B -->|"Eventual consistency OK"| D["Multi-leader or leaderless"]
    B -->|"Causal / read-your-writes"| E["Single leader or client-coordinated"]
    C --> F{Read scaling?}
    F -->|"Yes"| G["Leader for writes, read replicas for reads"]
    F -->|"No"| H["Leader only"]
    D --> I{Writes must succeed during partition?}
    I -->|"Yes"| J["Leaderless (Cassandra, DynamoDB)"]
    I -->|"No"| K["Multi-leader with conflict resolution"]
    G --> L["Needs: load balancer, read replica lag monitoring"]
    J --> M["Needs: read repair, hinted handoff, vector clocks"]
```

---

## Pitfalls

### Stale reads from read replicas

Reading from asynchronous replicas can return stale data. A user who just updated their profile may see the old version when their read hits a lagging replica. Use read-your-writes consistency (read from leader for the user's own data) or synchronous replication for critical reads.

### Write conflicts in multi-leader replication

Multiple leaders accepting writes to the same data can create conflicts. Handle with: last-write-wins (LWW, loses data), CRDTs (conflict-free data types), or application-level conflict resolution.

### Majority loss in a network partition

With Raft/etcd/ZK, a partitioned minority can't accept writes. A 3-node cluster needs 2 nodes to make progress. During a partition that splits 2:1, the side with 2 nodes continues, the side with 1 node is unavailable.

### Hinted handoff accumulation

If a node is down for a long time, hinted handoffs accumulate on other nodes. When the node recovers, replaying all hints can overwhelm it. Monitor hint counts and consider rebuilding the node from a snapshot instead.

### Over-quorum for write-heavy workloads

Setting W=3 and R=3 in a 3-node cluster provides strong consistency but zero failure tolerance (N=3, W+R > N requires 3 for each). Use W=2, R=2 for fault tolerance with strong consistency.

---

> [!question]- Interview Questions
>
> **Q: What is the difference between strong and eventual consistency?**
> A: Strong consistency guarantees that every read returns the latest write — all replicas agree at all times. Eventual consistency guarantees that replicas will converge over time without any ordering guarantee. Strong consistency requires synchronous replication (higher latency, lower availability during partitions). Eventual consistency allows any replica to accept writes (lower latency, higher availability).
>
> **Q: How does Raft consensus work?**
> A: Raft elects a leader that accepts all client writes and replicates them to followers via AppendEntries RPCs. A write is committed when a majority (quorum) of followers acknowledge it. If the leader fails, a new election is triggered — the candidate with the most up-to-date log becomes the new leader. Raft guarantees safety: at most one leader per term, and committed entries are never lost.
>
> **Q: What is quorum and how do you configure W and R for strong consistency?**
> A: Quorum is the minimum number of nodes that must agree on a read (R) or write (W). For strong consistency in a cluster of N nodes, configure W + R > N. In a 3-node cluster, W=2 and R=2 ensures the read set and write set overlap — at least one node in the read set has the latest write.
>
> **Q: What is hinted handoff?**
> A: When a replica is unavailable during a write, another node accepts the write on behalf of the downed node and stores a hint (the data and the target node). When the downed node recovers, the hint is replayed. This improves write availability without requiring all replicas to be up.
>
> **Q: How do you handle conflicts in multi-leader replication?**
> A: Options include: (1) Last-write-wins (LWW) — accept the write with the latest timestamp, loses data from concurrent writes. (2) CRDTs — merge concurrent writes without conflicts using commutative data structures. (3) Application-level resolution — flag conflicting versions, let the application or user decide.

---

## Cross-Links

- [[SystemDesign/01_Foundations/03_Data_Modeling_Basics]] for sharding and partitioning
- [[SystemDesign/02_Core/01_Caching_Strategies]] for cache invalidation and consistency
- [[SystemDesign/03_Advanced/04_Data_Consistency_Playbook]] for diagnosing consistency issues
- [[SQL/02_Core/03_Isolation_Levels_and_Anomalies]] for database transaction isolation
- [[CICD/Kubernetes/01_Foundations/04_Cluster_Architecture_and_Components]] for etcd and Raft in K8s
