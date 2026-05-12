---
tags: [aws, foundations, sqs, sns, eventbridge, kinesis, messaging, queues, topics, event-driven]
aliases: ["SQS Deep Dive", "SNS Deep Dive", "EventBridge", "Kinesis", "AWS Messaging", "Event-Driven Architecture"]
status: stable
updated: 2026-05-11
---

# SNS, SQS, EventBridge, and Event-Driven Messaging

> [!summary] Goal
> Master AWS messaging services: SQS (standard/FIFO queues, DLQ, visibility timeout, long polling), SNS (standard/FIFO topics, fan-out, filtering), EventBridge (event buses, rules, schemas, pipes), and Kinesis (Data Streams, Firehose, Data Analytics).

## Table of Contents

1. [SQS — Queues](#sqs-queues)
2. [SNS — Topics](#sns-topics)
3. [EventBridge — Event Bus](#eventbridge-event-bus)
4. [Kinesis — Streaming Data](#kinesis-streaming-data)

---

## SQS — Queues

> [!info] SQS
> SQS is a fully managed message queue for decoupling distributed systems. Supports Standard (high throughput, best-effort ordering) and FIFO (exactly-once, strict ordering) queues.

| Feature | Standard | FIFO |
|:--------|:--------:|:----:|
| **Throughput** | Unlimited | 3000 msg/s (with batching) / 300 (without) |
| **Ordering** | Best-effort | Strict first-in-first-out |
| **Exactly-once** | At-least-once | Exactly-once (deduplication) |
| **Deduplication** | Not supported | Content-based or message group + ID |

### Key concepts

```text
Visibility timeout: how long a message is hidden after being received.
  - If the consumer doesn't delete the message within the timeout, it becomes visible again.
  - Default: 30 seconds. Max: 12 hours.
  - Tune for processing time + buffer.

Dead-letter queue (DLQ): messages that exceeded maxReceiveCount go here.
  - Use to capture and analyze failed messages.
  - Redrive: move messages back to the source queue (with "redrive allow policy").
  - DLQ must be same type as source (Standard → Standard, FIFO → FIFO).

Long polling: ReceiveMessageWaitTimeSeconds (1-20s).
  - Reduces empty responses and cost.
  - Default short polling (set 0) returns immediately if no messages.

Delay queues: delay delivery by 0-900s (per queue or per message via DelaySeconds parameter).
  - FIFO queues don't support per-message delay.

Cost: per request (1 request = up to 10 messages for SendMessage/ReceiveMessage/DeleteMessage).
```

---

## SNS — Topics

> [!info] SNS
> SNS is a pub/sub messaging service. A topic is a communication channel. Publishers send messages to the topic; subscribers receive them (fan-out). Supports Standard and FIFO topics.

### Subscriptions

| Protocol | Use case | Delivery |
|:---------|:---------|:---------|
| **SQS** | Fan-out to queue for async processing | SNS pushes to SQS |
| **Lambda** | Trigger function on each message | SNS invokes Lambda |
| **Email** | Simple notifications (not for automation) | SNS sends email |
| **HTTP/HTTPS** | Webhook to external endpoint | SNS POSTs to URL |
| **SMS** | Mobile text messages | SNS sends to phone |

### Message filtering

```text
Filter policy (subscription attribute): filter messages by attribute value.
  If an SQS subscriber only cares about "event_type=order_placed", the filter drops other messages.

  Consumer 1: filter → {"event_type": ["order_placed"]}
  Consumer 2: filter → {"event_type": ["order_shipped"]}
  Total messages published: both consumers receive ONLY their filtered messages.
```

---

## EventBridge — Event Bus

> [!info] EventBridge
> EventBridge is a serverless event bus that connects application data from AWS services, SaaS partners, and custom applications. It routes events based on rules and schedules.

```text
Event bus types:
  - Default: events from AWS services (CloudTrail, EC2 state changes, etc.).
  - Custom: application-specific events.
  - Partner: events from SaaS services (Datadog, PagerDuty, Shopify, etc.).

Rules: match incoming events by pattern (event source, detail-type, detail fields) or schedule (cron/rate).
Targets: Lambda, SQS, SNS, Step Functions, Kinesis, EventBridge API Destinations.

Event replay: archive events and replay them for debugging.

Schema Registry: discover, create, and manage event schemas (code generation for TypeScript/Java).

Pipes: point-to-point event processing with optional enrichment.
  - Source → (filter + enrich using Lambda/StepFunctions/API Destination) → Target.
```

---

## Kinesis

> [!info] Kinesis
> Kinesis provides real-time streaming data processing. Three services: **Data Streams** (real-time, custom consumers), **Data Firehose** (near-real-time, auto-load to S3/Redshift/ES), **Data Analytics** (SQL or Apache Flink on streaming data).

| Service | Model | Latency | Multi-consumer | Cost |
|:--------|:-----:|:-------:|:--------------:|:----:|
| **Data Streams** | Shard-based | 200ms (real-time) | Yes (multiple apps) | Per shard-hour |
| **Firehose** | Auto-scaling | 60s (or 1MB batch) | No (one destination) | Per GB ingested |
| **Data Analytics** | SQL / Flink | Varies | Depends on stream | Per Kinesis Processing Unit |

```text
Data Streams shard:
  - 1 MB/s input, 2 MB/s output per shard.
  - 5 API transactions per second per shard.
  - Data retention: 24h (default) to 8760h (365 days, additional cost).
  - Resharding: split (increase shards) or merge (decrease), limited to 2x per 24h.

Firehose destinations: S3, Redshift (via S3 COPY), Elasticsearch/OpenSearch, Splunk, HTTP endpoints.
Data transformation: Lambda function can transform records before delivery.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/07_Lambda_Functions_Events_and_Best_Practices]] for Lambda + SQS/SNS
- [[CICD/AWS/01_Foundations/10_API_Gateway_REST_HTTP_WebSocket]] for API Gateway + SQS/SNS
- [[CICD/AWS/03_Advanced/05_Security_Encryption_and_Compliance]] for SQS encryption with KMS
- [[CICD/AWS/05_Projects/02_Serverless_API_with_Lambda_API_Gateway_DynamoDB]] for full event-driven app
