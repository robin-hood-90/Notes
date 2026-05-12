---
tags: [aws, foundations, dynamodb, nosql, dax, streams, global-tables, single-table-design, ttl]
aliases: ["DynamoDB Deep Dive", "DynamoDB Streams", "DAX", "DynamoDB Global Tables", "Single Table Design"]
status: stable
updated: 2026-05-11
---

# DynamoDB — NoSQL

> [!summary] Goal
> Master DynamoDB: table design (partition / sort key), secondary indexes (LSI/GSI), capacity modes (on-demand vs provisioned), DAX caching, DynamoDB Streams for event-driven patterns, Global Tables for multi-region, TTL, and single-table design patterns.

## Table of Contents

1. [Table Design — Keys, Indexes, and Query Patterns](#table-design-keys-indexes-and-query-patterns)
2. [Capacity Modes](#capacity-modes)
3. [DAX — Caching Layer](#dax-caching-layer)
4. [DynamoDB Streams](#dynamodb-streams)
5. [Global Tables](#global-tables)
6. [Single-Table Design and Patterns](#single-table-design-and-patterns)

---

## Table Design — Keys, Indexes, and Query Patterns

> [!info] DynamoDB
> DynamoDB is a key-value and document database that delivers single-digit millisecond performance at any scale. It's fully managed, serverless, and replicates data across 3 AZs. The primary key is either a **partition key** (single attribute, hash-based) or a **composite key** (partition + sort key).

### Primary Key

```text
Partition key only:
  - Uniquely identifies each item.
  - Distributes items across partitions via hash.
  - Best for simple key-value lookups: GetItem(partition key).

Partition + sort key:
  - Items with same partition key are grouped, sorted by sort key.
  - Efficient for Query operations (all items with same partition key, sorted).
  - Can query: =, <, >, <=, >=, BETWEEN, BEGINS_WITH on sort key.
  - Items with same partition key share provisioned throughput (hot key risk if not designed well).
```

### Secondary Indexes

| Index | Attribute types | Write throughput | Read consistency | Limit |
|:------|:---------------:|:----------------:|:----------------:|:-----:|
| **LSI** (Local Secondary Index) | Same partition key, different sort key | Same as table | Eventual/strong | 5 per table |
| **GSI** (Global Secondary Index) | Different partition + sort key | Separate (provisioned or on-demand) | Eventual only | 20 per table (default) |

```text
GSI considerations:
  - GSIs have their OWN read/write capacity (separate from table).
  - GSI writes are "eventually consistent" — there's ALWAYS a small replication lag.
  - GSI throttling: if a GSI's capacity is exceeded, the TABLE write will be throttled (dangerous!).
  - Use `warm` GSIs with sufficient capacity, or use auto scaling on GSIs.
  - Selectively project attributes to GSIs (KEYS_ONLY, INCLUDE, ALL).
```

---

## Capacity Modes

| Feature | On-demand | Provisioned |
|:--------|:---------:|:-----------:|
| **Pricing** | Pay per request (read + write) | Pay per provisioned WCU/RCU |
| **Auto scaling** | Built-in (unlimited scaling) | Application Auto Scaling |
| **Cost** | Higher for steady-state workloads | Lower for predictable traffic |
| **Best for** | Unknown/unpredictable traffic | Predictable workloads |

```text
WCU (Write Capacity Unit): 1 KB per second write.
RCU (Read Capacity Unit): 4 KB per second for strongly consistent, 8 KB for eventually consistent.

Burst capacity: DynamoDB reserves 5 minutes of unused capacity for bursting.
  - Sustained traffic above provisioned: get throttled (ProvisionedThroughputExceeded).
  - Auto scaling helps, but scales gradually (not instant).

Throttling errors:
  - Retry with exponential backoff (AWS SDK does this automatically).
  - Increase provisioned capacity or switch to on-demand.
  - Check for hot partitions (a single partition receiving too many requests).
```

---

## DAX — Caching Layer

> [!info] DAX
> DynamoDB Accelerator (DAX) is an in-memory cache for DynamoDB. It provides microsecond latency for reads (vs single-digit ms from DynamoDB). Write-through caching: writes go to DAX first, then asynchronously to DynamoDB. DAX runs in a VPC (cluster of nodes).

```text
DAX considerations:
  - Reduces read latency from single-digit ms to microseconds.
  - Offloads read traffic from DynamoDB (reduces provisioned capacity needed).
  - Write-through: DAX writes to DynamoDB asynchronously.
  - Eventual consistency: DAX reads may return stale data (if not refreshed).
  - Not for: strongly consistent reads (bypass DAX), very large items (> 1MB), items that change very frequently.
  - VPC-based: must be in same VPC as the application (use VPC peering or TGW for cross-VPC).
```

---

## DynamoDB Streams

> [!info] Streams
> DynamoDB Streams captures a time-ordered sequence of item-level changes (INSERT, MODIFY, REMOVE). Streams are ordered within each partition. Data is retained for 24 hours. Streams are the foundation for: event-driven architectures (Lambda + Streams), DynamoDB Global Tables, cross-region sync.

```text
Stream record types:
  - KEYS_ONLY:        only the key attributes.
  - NEW_IMAGE:        entire item after the change.
  - OLD_IMAGE:        entire item before the change.
  - NEW_AND_OLD_IMAGES: both before and after.

Lambda + Streams pattern:
  - Lambda polls the stream shard (like Kinesis).
  - Process items in batches (max 10K records).
  - Retries on error; failed records go to DLQ.
  - Ordering: records from the same partition are processed in order.
  - Use: search indexing (Elasticsearch/Opensearch), cross-region sync, materialized view.

Kinesis Adapter (alternative write): low-level stream consumption for custom consumers.
```

---

## Global Tables

> [!info] Global Tables
> DynamoDB Global Tables replicate data across multiple AWS regions. They provide multi-master, multi-region replication with automatic conflict resolution (last writer wins). Each region can read AND write (low latency for global user base).

```text
Requirements:
  - Must enable DynamoDB Streams (source of the replication).
  - All replica tables must have the same schema.
  - Each region uses its own provisioned capacity (on-demand or provisioned).
  - Replication lag ~1 second under normal conditions.

Conflict resolution:
  - Uses "last writer wins" based on a timestamp in the replication metadata.
  - If two writes happen within the same millisecond, the larger item wins.
  - For stronger consistency: design application-level reconciliation.
```

---

## Single-Table Design and Patterns

> [!info] Single-table design
> DynamoDB recommends storing multiple entity types in the same table using `GSI Overloading` (same GSI partition key but different sort key prefixes). This enables complex access patterns with a single query.

```text
Example: e-commerce application

Table: pk (partition key), sk (sort key), type (entity type), ... attributes

Items:
  pk=user_1   sk=metadata     type=user    name=Alice   email=alice@example.com
  pk=user_1   sk=order_123    type=order   total=49.99  status=shipped
  pk=user_1   sk=order_456    type=order   total=99.99  status=delivered
  pk=user_1   sk=order_123#item_1  type=order_item product=...   qty=2
  pk=order_123 sk=metadata     type=order  total=49.99   customer=user_1

Access patterns:
  - Get user:           Query(pk='user_1', sk='metadata')
  - Get user's orders:  Query(pk='user_1', sk BEGINS_WITH 'order_')
  - Get order details:  Query(pk='user_1', sk='order_123')
  - GSI: gsi1_pk=type   gsi1_sk=attribute  (e.g. query all orders by status)

Adjacency list pattern: for many-to-many relationships (e.g., users following users).
GSI Overloading: same GSI key but different sort key meaning by entity type.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/07_Lambda_Functions_Events_and_Best_Practices]] for Lambda + DynamoDB Streams
- [[CICD/AWS/02_Core/03_ALB_NLB_and_Target_Groups]] for DynamoDB + API Gateway patterns
- [[CICD/AWS/05_Projects/02_Serverless_API_with_Lambda_API_Gateway_DynamoDB]] for full serverless app
- [[CICD/AWS/03_Advanced/02_Cost_Management_and_Optimization]] for DynamoDB on-demand vs provisioned
