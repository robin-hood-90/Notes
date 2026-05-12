---
tags: [aws, advanced, autoscaling, asg, target-tracking, step-scaling, scheduled-scaling, lifecycle-hooks, ecs-scaling, lambda-concurrency, karpenter]
aliases: ["Autoscaling Deep Dive", "ASG Scaling", "ECS Auto Scaling", "Lambda Concurrency", "Karpenter", "Scalability"]
status: stable
updated: 2026-05-11
---

# Autoscaling — ASG, ECS, Lambda, and DynamoDB

> [!summary] Goal
> Master AWS autoscaling across all services: EC2 Auto Scaling Groups (ASG with target tracking, step scaling, lifecycle hooks), ECS Service Auto Scaling, Lambda provisioned concurrency, DynamoDB auto scaling, and Karpenter for EKS. Understand cooldowns, thrashing, and capacity planning.

## Table of Contents

1. [EC2 Auto Scaling Groups](#ec2-auto-scaling-groups)
2. [ECS Service Auto Scaling](#ecs-service-auto-scaling)
3. [Lambda and DynamoDB Scaling](#lambda-and-dynamodb-scaling)

---

## EC2 Auto Scaling Groups

> [!info] ASG
> ASG manages EC2 instance count across AZs based on scaling policies, health checks, and schedules. A launch template defines instance configuration (AMI, type, security groups, user data). The ASG maintains the desired count between min and max.

### Launch templates vs launch configurations

```text
Launch template (recommended): newer, versioned, parameter-rich.
  - Supports: EC2 placement groups, Capacity Reservation, multiple instance types (mixed instances policies).
  - Versioning: change template → new version → ASG uses latest or pinned version.

Launch configuration (legacy): not versioned, fewer features. Use launch templates instead.
```

### Scaling policies

| Policy type | When to use | How it works |
|:------------|:------------|:-------------|
| **Target tracking** | Simple metric (CPU, network) | Maintain a target value (e.g., CPU at 50%). AWS auto-creates scale-in/out policies. |
| **Step scaling** | Metric with magnitude sensitivity | Add more instances when breach is large (e.g., CPU 80% → add 4, CPU 60% → add 2). |
| **Simple scaling** | Not recommended | Single adjustment per alarm (no cooldowns coordination). |
| **Scheduled scaling** | Predictable traffic | Change min/max/desired at specific times (e.g., increase during business hours). |
| **Predictive scaling** | ML-based | AWS predicts traffic and pre-scales. Needs 2 weeks of historical data. |

### Lifecycle hooks

```text
Lifecycle hooks pause instance launch or termination to run custom actions:
  - Pending: instance starts, waits until resume (or timeout).
  - Terminating: instance stops, waits until resume.

Use cases:
  - Warm cache: install packages, download container images before registering with ELB.
  - Graceful shutdown: drain connections, upload logs before termination.

Hook timeout: 1h max (can be extended). Default 3600s.
```

### Cooldowns and instance warm-up

```text
Default cooldown: 300s (5min — applies after scaling activity).
  - Scale-in cooldown: time before another scale-in can happen.
  - Scale-out: new instances take 1-3 minutes to launch + warm-up.

Thrashing prevention:
  - Set cooldowns appropriately (longer = safer but slower).
  - Use scale-in protection to prevent recently launched instances from being removed.
  - Monitor scaling activities in CloudWatch.
```

---

## ECS Service Auto Scaling

> [!info] ECS auto scaling
> ECS Service Auto Scaling adjusts the desired count of tasks based on CloudWatch metrics (CPU, memory, ALB request count per target). It uses Application Auto Scaling under the hood.

```text
Supported metrics:
  - ECSServiceAverageCPUUtilization (CPU).
  - ECSServiceAverageMemoryUtilization (memory).
  - ALBRequestCountPerTarget (request count per task).

Scaling configuration:
  - Min/max tasks.
  - Target tracking (e.g., CPU 70%) + scale-out cooldown (60-300s) + scale-in cooldown (60-300s).
  - Scheduled scaling for known peaks.

Fargate considerations:
  - Fargate tasks start in ~1-2 minutes (no warm-up required).
  - No ASG delay (Fargate is serverless).
  - Use capacity providers for mixed Fargate + Fargate Spot.
```

---

## Lambda and DynamoDB Scaling

### Lambda concurrency

```text
Reserved concurrency: set a limit (e.g., 10 concurrent executions).
  - Guarantees capacity for that function.
  - Also caps scaling (no more than N).

Provisioned concurrency: pre-warm N execution environments.
  - Reduces cold starts to zero.
  - Pay for provisioned environments even when idle.
  - Application Auto Scaling can schedule provisioned concurrency.

Burst limits: 500 (per minute) up to 3000 (per region) — first burst then 500/minute addition.
```

### DynamoDB auto scaling

```text
Application Auto Scaling adjusts WCU/RCU based on utilization (target: 70% recommended).

Scale-out: happens quickly (based on consumed capacity vs provisioned).
Scale-in: slow (cooldown ~5 minutes, prevents oscillation).

Capacity modes:
  - Provisioned + auto scaling: best for predictable but spiky traffic.
  - On-demand: best for unpredictable traffic (no planning, but higher cost per request).

GSI scaling: separate capacity. GSIs can throttle even if the table has enough capacity.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/02_EC2_Instances_Storage_and_Networking]] for EC2 instances in ASG
- [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] for ECS Service Auto Scaling
- [[CICD/AWS/02_Core/02_EKS_Clusters_Node_Groups_and_Pods]] for Karpenter scaling
- [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] for scaling metrics and alarms
