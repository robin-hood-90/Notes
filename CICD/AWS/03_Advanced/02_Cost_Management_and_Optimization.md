---
tags: [aws, advanced, cost, savings-plans, reserved-instances, spot, budget, compute-optimizer, cost-explorer]
aliases: ["Cost Management", "AWS Cost Optimization", "Savings Plans", "Reserved Instances", "Compute Optimizer"]
status: stable
updated: 2026-05-11
---

# Cost Management and Optimization

> [!summary] Goal
> Master AWS cost management: Cost Explorer (usage/cost analysis), Budgets (cost/usage/reserved coverage), Savings Plans (compute/EC2), Reserved Instances (standard/convertible), Compute Optimizer (right-sizing), spot pricing, cost allocation tags, and Trusted Advisor.

## Table of Contents

1. [Cost Explorer and Budgets](#cost-explorer-and-budgets)
2. [Savings Plans and Reserved Instances](#savings-plans-and-reserved-instances)
3. [Compute Optimizer and Spot Pricing](#compute-optimizer-and-spot-pricing)
4. [Cost Allocation Tags and Trusted Advisor](#cost-allocation-tags-and-trusted-advisor)

---

## Cost Explorer and Budgets

> [!info] Cost Explorer
> Cost Explorer provides default cost/usage reports. You can filter by service, region, account, tag, or usage type. Visualize trends, identify anomalous spikes, and forecast future costs.

```text
Cost Explorer views:
  - Monthly costs by service.
  - Daily costs for the last 14 days.
  - Hourly costs (for EC2, RDS, EMR).
  - Cost by tag (tag-based cost allocation).
  - EC2 instance usage by family, region, OS, tenancy.

Budgets types:
  - Cost budget: track spending against a target ($).
  - Usage budget: track usage against a target (GB, hours).
  - RI coverage budget: track RI coverage (%).
  - Savings Plans coverage budget: track SP coverage (%).
  - Budget alerts: at 50%, 80%, 90%, 100% of budget (SNS notification).

Anomaly detection: CloudWatch anomaly detection on cost metrics.
```

---

## Savings Plans and Reserved Instances

| Commitment | Discount vs on-demand | Flexibility | Duration |
|:-----------|:---------------------:|:-----------:|:--------:|
| **Compute Savings Plan** | Up to 66% | EC2, Fargate, Lambda | 1 or 3 years |
| **EC2 Instance Savings Plan** | Up to 72% | EC2 within region (family flex) | 1 or 3 years |
| **Standard RI** | Up to 72% | EC2 (specific family, AZ/region) | 1 or 3 years |
| **Convertible RI** | Up to 54% | EC2 (change family, OS, tenancy) | 1 or 3 years |

```text
Savings Plans hierarchy:
  1. All compute usage first applies to Compute Savings Plan.
  2. Remaining EC2 usage applies to EC2 Instance Savings Plan.
  3. Remaining usage at on-demand rates.

Recommendations: Cost Explorer shows three recommendation types:
  - Savings Plans: recommended hourly commitment.
  - Reserved Instances: recommended RI purchase by family/region.
  - Rightsizing: above-recommended EC2 instances.

Compute Savings Plans are more flexible (apply to Fargate/Lambda).
EC2 Instance Savings Plans give higher discount but less flexibility.
```

---

## Compute Optimizer and Spot Pricing

### Compute Optimizer

```text
Compute Optimizer uses ML to analyze utilization and recommend:
  - EC2: over-provisioned (reduce instance size) or under-provisioned (increase size).
  - ASG: recommended launch template changes.
  - ECS: recommended task CPU/memory settings.
  - Lambda: recommended memory size (based on duration vs cost).
  - EBS: recommended volume type (gp3 vs gp2).

Recommendation categories:
  - Over-provisioned: reduce cost without performance impact.
  - Under-provisioned: increase size to avoid performance issues.
  - Optimized: current size is optimal.
  - Not optimized: no data yet.

Enrolled: default enabled for EC2 (require `OptimizedInfrastructure` option enabled).
```

### Spot pricing

```text
Spot instance prices vary by instance type, region, and time of day.
  - Spot price history: Cost Explorer shows historical spot prices.
  - Spot interruptions: 2-minute warning via instance metadata + EventBridge.
  - Spot Fleet: diversified requests across multiple instance types.

Cost comparison (example):
  On-demand: $0.0964/hr (t3.medium, us-east-1).
  Spot: $0.0288/hr (70% savings, varies).

Maximize savings: use spot for stateless, fault-tolerant workloads.
  - EKS with Karpenter: spot + on-demand mix.
  - ECS capacity providers: weight-based spot/on-demand.
```

---

## Cost Allocation Tags and Trusted Advisor

### Cost allocation tags

```text
Tags are the foundation of cost allocation:
  - AWS-generated tags: aws:createdBy, aws:cloudformation:stack-name.
  - User-defined tags: Environment, Team, Project, CostCenter.
  - Cost Explorer: group by tag for cost reports.
  - Activate: must activate tags in Cost Explorer console (tag keys appear after activation).

Tag strategies:
  - Environment: dev, staging, prod.
  - Team: team-name, cost-center.
  - Project: project-name, project-id.
  - Automation: auto-delete, auto-stop (for cleanup scripts).
```

### Trusted Advisor

```text
Trusted Advisor inspects your account and provides recommendations in five categories:
  - Cost optimization: idle instances, underutilized EBS, reserved instance expiration.
  - Performance: EC2 to EBS throughput, CloudFront TTL, over-provisioned instances.
  - Security: SG rules open to 0.0.0.0/0, MFA on root, S3 bucket public access.
  - Fault tolerance: EC2 without ASG, RDS without Multi-AZ, ELB across multiple AZs.
  - Service limits: approaching AWS service limits (EC2 instances, VPCs, etc.).

Tiers:
  - Basic: 47 checks (security + service limits) available to all accounts.
  - Business/Enterprise: full 106 checks (cost + performance + fault tolerance).
```

---

## Cross-Links

- [[CICD/AWS/04_Playbooks/06_Cost_Investigation]] for cost troubleshooting
- [[CICD/AWS/01_Foundations/02_EC2_Instances_Storage_and_Networking]] for spot instances
- [[CICD/AWS/02_Core/09_CloudTrail_Config_and_Compliance]] for cost tracking via Config
- [[CICD/AWS/05_Projects/03_Multi_Region_Active_Passive]] for multi-region cost considerations
