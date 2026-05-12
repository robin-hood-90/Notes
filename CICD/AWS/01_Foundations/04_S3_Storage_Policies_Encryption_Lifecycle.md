---
tags: [aws, foundations, s3, storage, glacier, encryption, lifecycle, replication, presigned-url]
aliases: ["S3 Deep Dive", "S3 Storage Classes", "S3 Bucket Policies", "S3 Lifecycle", "S3 Replication"]
status: stable
updated: 2026-05-11
---

# S3 — Storage Classes, Policies, Encryption, and Lifecycle

> [!summary] Goal
> Master Amazon S3: bucket policies vs IAM, storage classes, lifecycle transitions, encryption options, access control (presigned URLs, access points), replication (CRR/SRR), event notifications, versioning, and Object Lock.

## Table of Contents

1. [Buckets and Objects](#buckets-and-objects)
2. [Storage Classes and Lifecycle](#storage-classes-and-lifecycle)
3. [Access Control](#access-control)
4. [Encryption](#encryption)
5. [Versioning and Object Lock](#versioning-and-object-lock)
6. [Replication](#replication)

---

## Buckets and Objects

> [!info] S3
> S3 stores data as **objects** (key, value, metadata, version ID) within **buckets** (globally unique name, region-specific endpoint, unlimited objects). Objects are stored across at least 3 AZs (except One Zone-IA).

```text
Anatomy of an S3 bucket ARN:  arn:aws:s3:::my-bucket
Anatomy of an object ARN:     arn:aws:s3:::my-bucket/path/to/object

Key considerations:
  - Bucket name must be globally unique (across all accounts, all regions).
  - Objects max 5TB. For > 5TB use multipart upload (parts 5MB–5GB).
  - PUT ≤ 5GB single upload, > 5GB must use multipart.
  - No slash-delimited hierarchy exists (it's a flat key-value store).
  - Console / SDK shows "folders" by convention (prefix + delimiter).
```

---

## Storage Classes and Lifecycle

> [!info] Storage classes
> S3 tiers trade durability/availability for cost. All classes offer 99.999999999% (11 9's) durability (except One Zone-IA). Lifecycle policies automatically transition objects between classes or expire them.

| Class | Availability | Min storage duration | Retrieval cost | Use case |
|:------|:------------:|:--------------------:|:--------------:|----------|
| **S3 Standard** | 99.99% | None | None | Frequent access, production data |
| **S3 Intelligent-Tiering** | 99.99% | 30 days | None at access tier | Unknown/ changing access patterns |
| **S3 Standard-IA** | 99.9% | 30 days | Per GB retrieved | Infrequent but immediate access |
| **S3 One Zone-IA** | 99.5% (single AZ) | 30 days | Per GB retrieved | Re-creatable data, lower cost |
| **S3 Glacier Instant** | 99.9% | 90 days | Per GB (higher than IA) | Archive with sub-second retrieval |
| **S3 Glacier Flexible** | 99.99% | 90 days | Free (bulk, 5-12h) / per GB (expedited) | Archives with 1–5 min or 5–12h access |
| **S3 Glacier Deep Archive** | 99.99% | 180 days | Per GB | Long-term archives (12h retrieval) |

### Lifecycle rules

```json
{
    "Rules": [
        {
            "Id": "TransitionToIAThenGlacier",
            "Status": "Enabled",
            "Filter": { "Prefix": "logs/" },
            "Transitions": [
                { "Days": 30, "StorageClass": "STANDARD_IA" },
                { "Days": 90, "StorageClass": "GLACIER" }
            ],
            "Expiration": { "Days": 365 }
        }
    ]
}
```

```text
Lifecycle transitions:
  - Standard → Standard-IA:      after 30+ days.
  - Standard → Glacier:            after 90+ days.
  - Standard → Deep Archive:       after 180+ days.
  - Smaller objects (< 128KB): not charged for transition (but not cost-effective to transition).
  - NoncurrentVersionTransition: for versioned objects.
  - Expiration: delete objects (or delete markers for versioned buckets).
```

---

## Access Control

### Bucket policies vs IAM vs ACLs

```text
IAM identity-based policies:  "User/Role has permission to do X on Y."
Resource-based policies:      "S3 bucket allows principal P to do X on Y."

S3 bucket policy (resource-based):
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": { "AWS": "arn:aws:iam::ACCOUNT:user/User" },
        "Action": ["s3:GetObject", "s3:PutObject"],
        "Resource": "arn:aws:s3:::my-bucket/*",
        "Condition": { "Bool": { "aws:SecureTransport": "true" } }
    }]
}

Key conditions:
  - aws:SourceIp             — restrict to IP range.
  - s3:x-amz-server-side-encryption — require SSE-S3/SSE-KMS/SSE-C.
  - s3:versionid             — restrict operations to a specific object version.

Block Public Access settings (recommended defaults):
  - BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets.
  - When enabled, COMPLETELY prevents any public access (even if bucket policy grants it).
```

### Presigned URLs

```bash
# Enable time-limited access without AWS credentials in the app.

# Create a presigned URL for GET:
aws s3 presign s3://my-bucket/file.txt --expires-in 3600
# Output: https://my-bucket.s3.amazonaws.com/file.txt?X-Amz-Algorithm=...&X-Amz-Signature=...

# Python SDK:
import boto3
url = boto3.client('s3').generate_presigned_url(
    'get_object',
    Params={'Bucket': 'my-bucket', 'Key': 'file.txt'},
    ExpiresIn=3600
)
```

---

## Encryption

| Type | Description | Key management | Use case |
|:----:|:------------|:--------------:|----------|
| **SSE-S3** | AES-256 managed by S3 | AWS manages keys | Default, no additional cost |
| **SSE-KMS** | KMS customer managed key | You manage (via KMS) | Compliance, key rotation, audit |
| **SSE-C** | Customer-provided key | You provide key in each request | Must manage keys yourself |
| **Client-side** | Encrypt before upload | You handle keys | End-to-end encryption |

```text
SSE-KMS billing considerations:
  - Each API call (PutObject, GetObject) incurs a KMS API charge.
  - KMS has a request quota (default 5500/10000 per second).
  - For high-throughput workloads, SSE-S3 may be cheaper and avoid throttling.

Enforce encryption at the bucket policy level:
  "Condition": { "StringNotEquals": { "s3:x-amz-server-side-encryption": "AES256" } }
```

---

## Versioning and Object Lock

### Versioning

```text
Versioning protects against accidental deletion/overwrites:
  - Enabled per bucket (once enabled, cannot disable — only suspend).
  - PUT with same key creates NEW version (keeping the old one).
  - DELETE creates a Delete Marker (to permanently delete, specify version ID).
  - MFA Delete: require MFA to (1) change versioning state, (2) permanently delete versions.

Cost: each version is stored separately. Versioning a frequently-updated file can increase costs.
Use Lifecycle rules to clean old noncurrent versions:
  - NoncurrentVersionTransition: transition old versions to Glacier.
  - NoncurrentVersionExpiration: delete old versions after N days.
```

### Object Lock (WORM)

```text
Object Lock prevents objects from being deleted or overwritten for a fixed period.
  - Governance mode: special permissions can bypass (s3:BypassGovernanceRetention).
  - Compliance mode: no one can bypass (including root).
  - Legal Hold: prevents deletion/overwrite, no time limit (can add/remove by authorized users).

Retention period: specified per-object or via default bucket setting.
Use for: financial records, medical data, SEC compliance.
```

---

## Replication

| Mode | Description | Use case |
|:----:|:------------|----------|
| **CRR** (Cross-Region) | Replicate to a bucket in another region | DR, compliance, latency |
| **SRR** (Same-Region) | Replicate within the same region | Log aggregation, dev/test sync |

```text
Replication requirements:
  - Source bucket must have versioning enabled.
  - Destination bucket must have versioning enabled.
  - IAM role with permissions to read source, write destination.
  - Can replicate: all objects, or filtered by prefix/tag.
  - Can replicate to different account (destination bucket policy must grant access).
  - Can maintain: same storage class, or specify destination storage class.

Replication Time Control (RTC):
  - Guarantees 99.99% of objects replicated within 15 minutes (SLA).
  - Additional cost.

Delete markers: NOT replicated by default (can be enabled).
Metadata replication: user-defined metadata is replicated; system metadata different.
```

---

## Cross-Links

- [[CICD/AWS/04_Playbooks/04_Debug_S3_and_CloudFront]] for S3 troubleshooting
- [[CICD/AWS/02_Core/06_KMS_and_Secrets_Manager]] for SSE-KMS
- [[CICD/AWS/02_Core/03_ALB_NLB_and_Target_Groups]] for S3 as ALB target
- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for S3 Gateway Endpoints
