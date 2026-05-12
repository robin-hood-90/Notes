---
tags: [aws, core, cloudwatch, logs, metrics, alarms, dashboard, log-insights, synthetics, container-insights]
aliases: ["CloudWatch Deep Dive", "CloudWatch Logs", "CloudWatch Metrics", "CloudWatch Alarms", "Container Insights", "Logs Insights"]
status: stable
updated: 2026-05-11
---

# CloudWatch — Logs, Metrics, Alarms, Dashboards

> [!summary] Goal
> Master CloudWatch: log groups/metrics filters/structured logging, standard/custom metrics, alarms (static/anomaly/composite), dashboards, Logs Insights (SQL-like query), Synthetics canaries, Container Insights, and Lambda Insights.

## Table of Contents

1. [Logs and Metrics](#logs-and-metrics)
2. [Alarms](#alarms)
3. [Logs Insights and Dashboards](#logs-insights-and-dashboards)
4. [Container Insights and Lambda Insights](#container-insights-and-lambda-insights)

---

## Logs and Metrics

> [!info] CloudWatch
> CloudWatch provides observability for AWS resources and applications. Logs: store and search log data from AWS services and custom applications. Metrics: time-series data from AWS services and custom metrics. Alarms: trigger on metric breaches.

### Log groups and streams

```text
Log group: container for log streams (one per application component).
  - Retention: 1 day to 10 years (or never expire).
  - Metric filters: extract values from log text into CloudWatch metrics.
  - Subscription filters: stream logs to Lambda, Kinesis, or Firehose (centralized log analysis).

Log stream: sequence of log events from a single source (one per EC2 instance, Lambda container, or ECS task).
```

### Standard metrics by service

```text
EC2: CPUUtilization, NetworkIn/Out, DiskReadBytes (requires CloudWatch Agent for memory/disk metrics).
ECS: CPUUtilization, MemoryUtilization (per cluster/service/task).
EKS: (via Container Insights) node/pod/container metrics.
Lambda: Invocations, Errors, Duration, Throttles, ConcurrentExecutions.
ALB: RequestCount, TargetResponseTime, HTTPCode_Target_5XX, HealthyHostCount.
RDS: CPUUtilization, DatabaseConnections, FreeableMemory, ReadLatency.
SQS: ApproximateNumberOfMessagesVisible, ApproximateAgeOfOldestMessage.
```

### Custom metrics

```bash
# Put custom metrics (from application code):
aws cloudwatch put-metric-data \
    --namespace "MyApp" \
    --metric-name "RequestLatency" \
    --dimensions Service=Orders,Environment=prod \
    --timestamp $(date +%s) \
    --value 42 \
    --unit Milliseconds

# Embed metric in structured log (using CloudWatch Agent or Lambda):
# { "request_id": "abc", "latency": 42, "status": 200 }
# Metric filter: extract latency > 200ms.
```

### CloudWatch Agent (unified)

```text
The unified CloudWatch Agent collects logs AND metrics from EC2 and on-prem servers.
Configuration at: /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

Metrics collected:
  - CPU: user, nice, system, idle, iowait, irq, steal, guest (per-CPU).
  - Disk: used, total, disk I/O (reads/writes per second).
  - Memory: used, available, cached, buffered, swap.
  - Network: bytes in/out, packets in/out, errors.
  - Netstat: TCP connections, UDP datagrams.
  - Process: process count, per-process CPU/ memory/file descriptors.
```

---

## Alarms

| Alarm type | Description | Use case |
|:-----------|:------------|:---------|
| **Static** | `metric > threshold` | Simple monitoring |
| **Anomaly detection** | ML model of expected range | Metrics with seasonal patterns |
| **Composite** | AND/OR combination of child alarms | Reduce noise (page only when multiple conditions met) |

```bash
# Example alarm: high latency
aws cloudwatch put-metric-alarm \
    --alarm-name "MyApp-HighLatency" \
    --alarm-description "Latency > 500ms for 3 consecutive periods" \
    --namespace "AWS/ApplicationELB" \
    --metric-name "TargetResponseTime" \
    --dimensions Name=LoadBalancer,Value=app/my-alb/abc123 \
    --statistic "p99" \
    --period 60 \
    --evaluation-periods 3 \
    --threshold 0.5 \
    --comparison-operator "GreaterThanThreshold" \
    --alarm-actions "arn:aws:sns:us-east-1:123456:MyAlertTopic"
```

---

## Logs Insights and Dashboards

### Logs Insights

```sql
-- Top 10 slowest requests in the last hour
fields @timestamp, @message, @logStream
| filter @message like /ERROR|request_id/
| parse @message /latency=(?<latency>\d+)/
| sort latency desc
| limit 10

-- Error rate over time (count per 5 minutes)
stats count() as errorCount by bin(5m)
| filter @message like /ERROR/

-- Most common error messages
filter @message like /ERROR/
| stats count() as cnt by @message
| sort cnt desc
| limit 20
```

### Dashboards

```text
CloudWatch Dashboards:
  - Cross-region, cross-account (with monitoring account).
  - Widgets: metric graph, text, alarm status, Logs Insights query.
  - Automatic refresh: every 10s (automatic) or 60s (default).
  - Share with other accounts (read-only).

Example dashboard widgets:
  - Service dashboard: request rate, error rate, p50/p99 latency, concurrent tasks.
  - Infra dashboard: CPU by AZ, memory usage, disk I/O.
  - Cost dashboard: daily cost by service, anomaly tracking.
```

---

## Container Insights and Lambda Insights

### Container Insights

```text
Collects metrics from ECS and EKS:
  - ECS: CPU/memory reservation and utilization per cluster/service/task.
  - EKS: node/pod/container metrics, network, disk.
  - Task-level: network I/O, storage, specific container-level metrics.
  - Performance Logs: detailed breakdown of CPU, memory, network, disk per container.
  - Enable: `ECS_ENABLE_CONTAINER_METRICS=true` (or EKS add-on).

Metrics emitted to CloudWatch: 100+ metrics per container, cluster, service.
```

### Lambda Insights

```text
Lambda Insights provides OS-level metrics for Lambda functions:
  - CPU time (user/system), memory (used/available), network I/O.
  - Disk I/O (/tmp operations), file descriptors, threads.
  - Cold start vs warm start detection.
  - Enable: `--enable-insights` for Lambda function.
  - Metrics in CloudWatch under /aws/lambda-insights.

Cost: per function invocation (billed per GB-second of metric data).
```

---

## Cross-Links

- [[CICD/AWS/04_Playbooks/02_Debug_ECS_EKS_Deployments]] for using CloudWatch to debug deployments
- [[CICD/AWS/04_Playbooks/01_Debug_IAM_AccessDenied]] for CloudTrail + CloudWatch
- [[CICD/AWS/02_Core/09_CloudTrail_Config_and_Compliance]] for CloudTrail + Config integration
- [[CICD/AWS/03_Advanced/02_Cost_Management_and_Optimization]] for CloudWatch cost management
