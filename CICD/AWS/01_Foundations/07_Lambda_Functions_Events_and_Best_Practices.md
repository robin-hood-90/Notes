---
tags: [aws, foundations, lambda, serverless, functions, events, sam, triggers, cold-start, snapstart]
aliases: ["AWS Lambda", "Lambda Functions", "Lambda Events", "Serverless Functions", "Lambda Best Practices"]
status: stable
updated: 2026-05-11
---

# Lambda — Functions, Events, and Best Practices

> [!summary] Goal
> Master AWS Lambda: function configuration, event sources (SQS, SNS, S3, DynamoDB Streams, API Gateway, EventBridge), concurrency (reserved/provisioned), versions/aliases, VPC integration, cold starts, SnapStart, Lambda extensions, and function URLs.

## Table of Contents

1. [Function Configuration](#function-configuration)
2. [Event Sources](#event-sources)
3. [Concurrency and Scaling](#concurrency-and-scaling)
4. [VPC Integration and Cold Starts](#vpc-integration-and-cold-starts)
5. [Versions, Aliases, and Deployments](#versions-aliases-and-deployments)

---

## Function Configuration

> [!info] Lambda
> Lambda runs your code in response to events. It manages the compute infrastructure, scaling, and availability. Each invocation runs in a sandboxed execution environment. The environment has a lifecycle: **Init** (cold start — download code, start runtime, run init code) → **Invoke** (run handler) → **Shutdown** (freeze, 300ms grace).

```text
Configuration options:
  Memory: 128 MB – 10,240 MB (max 10GB), proportional CPU/network.
    More memory = more CPU = faster execution (not just more memory for the code).
    Cost scales linearly (pay per GB-second) but execution time may decrease faster.
  Ephemeral storage: 512 MB – 10,240 MB in /tmp.
  Timeout: 1s – 900s (15 minutes).
  Runtime: managed (Node.js, Python, Java, Go, .NET, Ruby), custom runtime (provided.al2).
  Architecture: x86_64, arm64 (Graviton2 — up to 34% cheaper, 19% faster).
  VPC: attach to VPC (uses Hyperplane ENI per subnet).
  Reserved concurrency: guarantee capacity (also limits max concurrent executions).
  Environment variables: 4KB total, encrypted at rest with KMS.
  Tags: 50 tags per function (cost allocation, resource grouping).
```

---

## Event Sources

| Service | Trigger type | Invocation mode | Batch |
|:--------|:------------:|:---------------:|:-----:|
| **SQS** | Queue poller | Event (batching) | Yes (up to 10K records) |
| **SNS** | Topic subscription | Event | No (one message) |
| **S3** | Bucket notification | Event (async) | No |
| **DynamoDB Streams** | Stream poller | Event (batching) | Yes (up to 10K records) |
| **Kinesis** | Stream poller | Event (batching) | Yes |
| **API Gateway** | HTTP request | Synchronous | No |
| **EventBridge** | Rule target | Event (async) | No |
| **Step Functions** | Activity/task | Synchronous | No |
| **S3 Object Lambda** | S3 access point | Sync Transform | No |
| **Function URL** | HTTP request | Sync | No |

### SQS polling behavior

```text
Lambda polls SQS (uses long polling), batches messages (batchSize: 1-10, maxBatchingWindow: 0-300s).
When the Lambda fails to process: SQS messages reappear after visibility timeout.
  - Successful messages are deleted from SQS by Lambda (SDK).
  - Failed messages remain in queue.
  - DLQ after max receive count exceeded.
  - ReportBatchItemFailures: report specific failed messages (not all) for partial failure.
```

---

## Concurrency and Scaling

> [!info] Concurrency
> Lambda scales by creating new execution environments in response to events. Account burst limits: 500-3000 per region (varies). After burst, scales by 500 per minute.

```text
Types of concurrency:
  Reserved: set a limit (e.g., 10). Guarantees 10 environments available, but restricts scaling.
  Provisioned: pre-warm N environments (pay for them even when idle). Reduces cold starts.
  Unreserved: the remaining (1000 total minus all reserved).

Provisioned concurrency + auto scaling:
  - Application Auto Scaling schedules target utilization.
  - Good for: predictable traffic patterns (morning peak, campaign launch).
  - Not for: spiky/unpredictable traffic (use on-demand).

Cold start mitigation:
  - Use provisioned concurrency (most expensive but most reliable).
  - Use SnapStart (Java/Python — pre-execute and freeze snapshot, restore ~100ms vs multiple seconds).
  - Keep functions warm (a side effect of provisioned concurrency).
  - Use Graviton (arm64) — faster cold start than x86.
  - Avoid VPC (VPC cold start takes 7-10 seconds). Use RDS Proxy to reduce connections.
```

---

## VPC Integration and Cold Starts

```text
When a Lambda function is in a VPC:
  1. Lambda creates a Hyperplane ENI in each subnet (elastic network interface).
  2. This ENI creation takes ~10 seconds — adds to cold start time.
  3. The ENIs stay alive for ~30-60 minutes of inactivity (warm).
  4. For large subnets, more ENIs are created.

Best practices for VPC Lambdas:
  - Prefer RDS Proxy for DB access (reduces connection churn).
  - Use fewer subnets (but at least 2 for HA across AZs).
  - Use larger subnets (/24 or bigger) to allow for ENI scaling.
  - Cache connections across invocations (static variable).
  - Prefer NAT Gateway for internet access (not VPC endpoints for all services).
  - Put Lambda in the same subnet as the target resource.

VPC endpoints needed for Lambda (for non-internet access):
  - S3 (Gateway Endpoint), DynamoDB (Gateway Endpoint).
  - ECR, CloudWatch Logs, KMS, STS (Interface Endpoints).
  - SSM, Secrets Manager (Interface Endpoints, if needed).
```

---

## Versions, Aliases, and Deployments

```text
Versions: immutable snapshots of function code + configuration. Each has an ARN.
  - $LATEST is the mutable version.
  - Publish a version: it's locked (code and configuration can't change).

Aliases: point to a specific version (or split traffic between two versions).
  - prod → version 4
  - Prod.canary → 90% version 4, 10% version 5 (incremental rollouts).
  - Aliases have their own ARN (use them in event source mappings).

Deployment strategies:
  - All-at-once: deploy then update alias (all traffic immediately).
  - Canary: 10% new, 90% old → after N minutes, 100% new.
  - Linear: 10% every 3 minutes → 100%.
  - CodeDeploy can manage this with CodeDeploy + Lambda.AppSpec.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/10_API_Gateway_REST_HTTP_WebSocket]] for API Gateway triggers
- [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] for Lambda monitoring
- [[CICD/AWS/01_Foundations/06_DynamoDB_NoSQL]] for Lambda + DynamoDB Streams
- [[CICD/AWS/05_Projects/02_Serverless_API_with_Lambda_API_Gateway_DynamoDB]] for full serverless
