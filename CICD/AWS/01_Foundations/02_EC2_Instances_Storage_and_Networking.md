---
tags: [aws, foundations, ec2, ebs, instances, spot, ami, placement-groups, user-data]
aliases: ["EC2 Deep Dive", "EC2 Instances", "EBS Volumes", "Spot Instances", "AMI", "Placement Groups"]
status: stable
updated: 2026-05-11
---

# EC2 — Instances, Storage, and Networking

> [!summary] Goal
> Master Amazon EC2: instance types and families, purchasing options (on-demand, reserved, spot), AMI and user data, EBS volumes and snapshots, placement groups, and instance networking.

## Table of Contents

1. [Instance Types and Families](#instance-types-and-families)
2. [Purchasing Options](#purchasing-options)
3. [AMI and User Data](#ami-and-user-data)
4. [EBS Volumes](#ebs-volumes)
5. [Placement Groups](#placement-groups)

---

## Instance Types and Families

> [!info] Instance family
> EC2 instance types are grouped into families optimized for different workloads. The naming convention: `{family}{generation}.{size}`, e.g., `t3.large`, `c7g.xlarge`, `r5.2xlarge`.

| Family | Use case | Examples | CPU architecture |
|:------:|----------|:--------:|:----------------:|
| **t** (burstable) | General purpose, dev/test, low-CPU web servers | `t3.medium`, `t4g.small` | x86 (t3), Graviton (t4g) |
| **m** (general) | Balanced compute/memory/net | `m7g.large`, `m6i.xlarge` | x86/Graviton |
| **c** (compute) | Batch processing, high-CPU | `c7g.2xlarge`, `c5.4xlarge` | x86/Graviton |
| **r** (memory) | In-memory caches, databases | `r7g.large`, `r5.8xlarge` | x86/Graviton |
| **x** (memory-optimized) | Large SAP HANA, in-memory DB | `x2iedn.32xlarge` | x86 |
| **g** / **p** (GPU) | ML training, rendering | `g5.xlarge`, `p4d.24xlarge` | x86 + NVIDIA GPU |
| **i** (storage) | High I/O, NoSQL DBs | `i3.large`, `i4i.xlarge` | x86 + NVMe |
| **h** (storage) | Throughput-oriented HDD | `h1.16xlarge` | x86 |

### Burstable T instances and CPU credits

```text
T instances accumulate CPU credits when idle (below baseline) and spend credits when busy.
  - Unlimited mode: can burst beyond credits (pay for extra CPU usage), avoid throttling.
  - Standard mode: limited to accrued credits; if exhausted, CPU throttles to baseline.
  - Use T instances for: web servers, dev/test, CI runners, small databases.
  - Avoid T instances for: sustained high CPU workloads, production databases.

Monitoring: `CPUCreditBalance`, `CPUSurplusCreditBalance` (for Unlimited mode).
```

---

## Purchasing Options

| Option | Commitment | Discount vs on-demand | Interruption? |
|:-------|:----------:|:---------------------:|:-------------:|
| **On-Demand** | None | None (pay per hour/sec) | No |
| **Reserved** (Standard) | 1 or 3 years | Up to 72% | No |
| **Reserved** (Convertible) | 1 or 3 years | Up to 54% | No (can change family) |
| **Spot** | None | Up to 90% | Yes (2-minute warning) |
| **Dedicated Host** | None or reserved | N/A (physical server) | No |
| **Capacity Reservation** | None (region/AZ) | None (reserve capacity) | No |

### Spot instances

```bash
# Best practices:
#   - Use spot for: batch jobs, stateless workloads, ML training, CI/CD.
#   - NOT for: stateful databases, long-running interactive workloads.
#   - Spot interruption notice: EC2 sends a 2-minute warning via Instance Metadata + EventBridge.
#   - Diversify: use multiple instance types in a Spot Fleet.
#   - Specify durations: can request blocks of 1–6 hours.
#   - Pricing: bid price is not needed — pay current spot price (usually much lower than on-demand).

# Spot instance request types:
#   - persistent: request stays active after interruption, re-launches when capacity resumes.
#   - one-time: request expires after launching once.

# Spot Fleet: mix multiple instance types, allocation strategies (lowestPrice, diversified, capacityOptimized).
# Spot with EKS/ECS: use `capacityProviderStrategy` with weight for mixing spot and on-demand.
```

---

## AMI and User Data

> [!info] AMI
> An Amazon Machine Image (AMI) contains the OS, software, and configuration for launching an EC2 instance. AMIs are region-specific (can copy across regions). Sources: AWS-provided (Amazon Linux 2/2023, Ubuntu, Windows Server), AWS Marketplace, custom AMIs built with EC2 Image Builder or Packer.

```bash
# User data: script that runs on first boot (as root).
# Use: install packages, configure services, register with SSM.

#!/bin/bash
exec > /var/log/user-data.log 2>&1  # Capture all output
set -ex
yum update -y
yum install -y docker
systemctl enable --now docker
aws s3 cp s3://my-bucket/config.json /etc/myapp/config.json
```

```text
User data types:
  - text: Everything up to 16KB (MIME multi-part for longer scripts).
  - MIME multi-part: include cloud-config + shell scripts + cloud-boothook.
  - cloud-init modules: write_files, packages, runcmd, users, and more.

User data is accessible at: curl http://169.254.169.254/latest/user-data
```

### Instance metadata (link-local address)

```bash
# Query instance metadata without AWS credentials:
curl http://169.254.169.254/latest/meta-data/
# - instance-id, instance-type, ami-id, local-ipv4, public-ipv4
# - iam/security-credentials/rolename  → temporary credentials from instance profile
# - network/interfaces/macs/          → MAC-specific metadata
# - placement/availability-zone       → AZ location
```

---

## EBS Volumes

> [!info] EBS
> Elastic Block Store provides persistent block storage for EC2. Volumes are replicated within an AZ. Snapshots are stored in S3 (incremental). Root device volume can be EBS or instance store (ephemeral).

### Volume types

| Type | Max IOPS | Max throughput | Use case |
|:----:|:--------:|:--------------:|----------|
| **gp3** | 16,000 | 1,000 MB/s | General purpose SSD (default — balances price/performance) |
| **gp2** | 16,000 | 250 MB/s | Older generation gp3 is cheaper |
| **io1** | 64,000 | 1,000 MB/s | High IOPS for databases (IOPS provisioned separately) |
| **io2** | 256,000 | 4,000 MB/s | Block Express, high durability, critical workloads |
| **st1** | 500 | 500 MB/s (burst) | Throughput-optimized HDD (big data, logs) |
| **sc1** | 250 | 250 MB/s | Cold HDD (infrequent access) |

### Snapshots

```text
Snapshots are incremental (only changed blocks saved after first full snapshot).
  - Use: backups, DR via cross-region copy, share with other accounts, AMI creation.
  - EBS Snapshot Archive: store in "archive" tier for 90+ days (up to 75% cheaper).
  - EBS Snapshot Recycle Bin: retain deleted snapshots for 1–365 days.
  - Fast Snapshot Restore (FSR): instant first access after restoring (pay per minute).
  - Lifecycle Manager: automate snapshot creation/retention at schedule (tag-based).
```

### Encryption

```text
Encryption at rest:
  - By default: EBS encryption is enabled at account level (per region).
  - Uses KMS (Customer Managed Key or AWS managed `aws/ebs`).
  - Encrypted snapshots: any snapshot created from an encrypted volume is also encrypted.
  - Encrypted AMI: share with other accounts by sharing the KMS key + AMI permissions.
  - Cannot disable encryption on an encrypted volume; must copy to unencrypted snapshot.
```

---

## Placement Groups

| Type | Pros | Cons | Use case |
|:----:|:----:|:----:|----------|
| **Cluster** | Low latency, 10 Gbps network | Single AZ, limited instances | HPC, tightly-coupled MPIs |
| **Spread** | Fault isolation across HW | 7 instances per AZ max | Critical apps, each on separate rack |
| **Partition** | Fault isolation for groups | 7 partitions per AZ | HDFS, Cassandra, Kafka, distributed systems |

---

## Cross-Links

- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for security groups for EC2
- [[CICD/AWS/03_Advanced/03_SSM_Session_Manager_and_SSH]] for connecting to EC2 via SSM and SSH
- [[CICD/AWS/03_Advanced/04_Autoscaling_ASG_and_TargetTracking]] for EC2 Auto Scaling Groups
- [[CICD/AWS/03_Advanced/02_Cost_Management_and_Optimization]] for spot pricing and right-sizing
