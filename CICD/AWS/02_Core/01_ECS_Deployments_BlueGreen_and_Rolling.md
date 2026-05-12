---
tags: [aws, core, ecs, fargate, ec2, task-definition, service, blue-green, service-connect, exec, capacity-provider]
aliases: ["ECS Deep Dive", "ECS Fargate", "ECS Task Definitions", "ECS Service", "ECS Blue Green", "ECS Service Connect"]
status: stable
updated: 2026-05-11
---

# ECS — Clusters, Services, and Deployments

> [!summary] Goal
> Master Amazon ECS: clusters (Fargate vs EC2), task definitions (family, cpu/memory, port mappings, secrets, task role), services (desired count, deployment controller, health checks), Service Connect for mesh, ECS Exec for debugging, capacity providers, and deployment patterns (rolling, blue/green).

## Table of Contents

1. [Launch Types — Fargate vs EC2](#launch-types-fargate-vs-ec2)
2. [Task Definitions](#task-definitions)
3. [Services and Deployments](#services-and-deployments)
4. [Service Connect](#service-connect)
5. [ECS Exec](#ecs-exec)

---

## Launch Types — Fargate vs EC2

| Feature | Fargate | EC2 |
|:--------|:-------:|:---:|
| **Management** | AWS manages infra | You manage instances (ASG, patching) |
| **Pricing** | Per vCPU + GB per second | Per EC2 instance (reserved/spot possible) |
| **Scaling** | Instant (no cluster capacity) | Needs ASG, capacity provider, instance warmup |
| **GPU** | No | Yes (p/g instance families) |
| **Cost optimization** | On-demand only | Spot + Reserved + Savings Plans |
| **Data volume** | EFS, EBS (limited) | EBS, EFS, instance store |
| **ENI per task** | `awsvpc` mode only | `awsvpc` or host/bridge/nat modes |
| **Container logging** | CloudWatch, FireLens | CloudWatch, FireLens, fluentd |

### When to use which

```text
Fargate:
  - No desire to manage server infrastructure.
  - Burstable or unpredictable workloads (pay per task).
  - Small microservices (lower per-task cost).
  - Quick scaling needs (no cluster warmup).

EC2:
  - Large tasks (lots of vCPU/memory — per-instance pricing wins).
  - GPU workloads (ML inference, rendering).
  - Heavy disk I/O (EC2 instance store, large EBS volumes).
  - Cost optimization via Spot + Reserved Instances.
```

---

## Task Definitions

> [!info] Task definition
> A task definition is the blueprint for your application. It describes: container image, CPU/memory, port mappings, environment variables, secrets, logging, volumes, task execution role (for pulling images/CloudWatch), and task role (for permissions).

```json
{
    "family": "my-app",
    "taskRoleArn": "arn:aws:iam::123456789012:role/MyAppTaskRole",
    "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "containerDefinitions": [{
        "name": "app",
        "image": "public.ecr.aws/nginx/nginx:1.27",
        "essential": true,
        "portMappings": [{ "containerPort": 80, "protocol": "tcp" }],
        "environment": [
            { "name": "ENV", "value": "production" }
        ],
        "secrets": [
            { "name": "DB_PASSWORD", "valueFrom": "arn:aws:ssm:us-east-1:123456:parameter/db/password" }
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "/ecs/my-app",
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "ecs"
            }
        }
    }]
}
```

---

## Services and Deployments

> [!info] Service
> An ECS service manages a desired number of task instances, auto-restarts failed tasks, and integrates with load balancers for traffic distribution. Supports rolling update, blue/green (CodeDeploy), and external deployments.

### Deployment controllers

| Controller | Strategy | Use case |
|:-----------|:---------|:---------|
| **ECS** (rolling) | Replace tasks gradually (min/max health) | Simple rollouts |
| **CODE_DEPLOY** (blue/green) | AWS CodeDeploy manages traffic shifting | Canary, linear, all-at-once |
| **EXTERNAL** | Third-party (Terraform, custom) | External orchestrator |

### Rolling update configuration

```text
Minimum healthy percent: minimum tasks that must remain healthy during deployment.
Maximum percent: maximum tasks that can run during deployment (above desired count).

Example: desired=4, min_healthy=100, max=200
  → 4 old + 4 new = 8 tasks during update (blue/green without CodeDeploy).

Deployment circuit breaker: if new tasks fail health checks, roll back automatically.
  - Enable in service configuration.
  - Rollback triggers on: failing health checks, task stopped with error.
```

### Blue/green with CodeDeploy

```text
Blue: current version (stable traffic).
Green: new version (deployed, tested, then traffic shifted).
AppSpec: task definition + container name/port + Lambda validation test.
CodeDeploy: shift traffic (canary 10%, linear by N%, all-at-once).
Auto-rollback: CloudWatch alarm triggers rollback (5XX spike, latency increase).
```

---

## Service Connect

> [!info] Service Connect
> Service Connect provides DNS-based service discovery and traffic management for ECS services. Each service gets a DNS name (e.g., `http://my-app:80`). Traffic is encrypted between services and automatically balanced across tasks.

```text
Service Connect benefits:
  - No need for a separate load balancer for inter-service communication.
  - Built-in circuit breaking (timeout, max retries).
  - Smart load balancing (least outstanding requests, round-robin).
  - Protocol: HTTP/1.1, HTTP/2, gRPC.
  - Proactive health checks (connects to tasks directly, not through ALB).

Configuration:
  - Namespace: Cloud Map namespace.
  - Service discovery: service name + port.
  - Client: configuration at task definition level (port aliases, timeout).
```

---

## ECS Exec

> [!info] ECS Exec
> ECS Exec allows running commands in a running container (SSM Session Manager-based). Useful for debugging: inspect files, run shell commands, test network connectivity. No SSH key required, no public IP needed.

```json
// Prerequisites:
// 1. Enable execute command on the service:
{
    "enableExecuteCommand": true
}
// 2. SSM Agent in the container (managed AWS images include it).
// 3. Task role must allow SSM actions (ssm:StartSession, etc.)
```

```bash
# Start a shell in the container:
aws ecs execute-command \
    --cluster my-cluster \
    --task task-id \
    --container app \
    --command "/bin/bash" \
    --interactive
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for VPC networking with ECS tasks
- [[CICD/AWS/01_Foundations/02_EC2_Instances_Storage_and_Networking]] for EC2-type ECS capacity
- [[CICD/AWS/03_Advanced/04_Autoscaling_ASG_and_TargetTracking]] for ECS Service Auto Scaling
- [[CICD/AWS/04_Playbooks/02_Debug_ECS_EKS_Deployments]] for deployment failure debugging
