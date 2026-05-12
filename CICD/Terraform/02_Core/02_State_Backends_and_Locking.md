---
tags: [terraform, core, state, backend, s3, dynamodb, locking, remote-state, migration]
aliases: ["Terraform State Backends", "S3 Backend", "DynamoDB Locking", "Terraform Cloud Backend", "State Migration"]
status: stable
updated: 2026-05-11
---

# State Backends and Locking

> [!summary] Goal
> Master Terraform state backends: S3 + DynamoDB (AWS), GCS (GCP), AzureRM (Azure), Terraform Cloud, and Consul. Understand state locking (how DynamoDB enforces locks, force-unlock risks), state migration between backends, and `terraform_remote_state` for cross-config reads.

## Table of Contents

1. [Why Remote State](#why-remote-state)
2. [Backend Comparison](#backend-comparison)
3. [S3 + DynamoDB Deep Dive](#s3-dynamodb-deep-dive)
4. [State Locking](#state-locking)
5. [State Migration](#state-migration)
6. [terraform_remote_state](#terraformremotestate)

---

## Why Remote State

> [!info] Remote state
> Local state (`.tfstate` in the working directory) works for solo development. Teams need **remote state**: stored in a shared, encrypted, versioned location with locking. Remote state also enables: `terraform_remote_state` across configurations, collaboration via CI/CD, and disaster recovery.

```text
Problems with local state:
  - Can't share with team members (everyone runs their own state).
  - No locking (two people running terraform simultaneously → corruption).
  - No version history (accidental state delete loses everything).
  - Not encrypted at rest.
  - Bloated Git history if committed accidentally.
```

---

## Backend Comparison

| Backend | Locking | Encryption | Versioning | IAM/ACL | Cost | Best for |
|:--------|:------:|:----------:|:----------:|:-------:|:----:|----------|
| **S3 + DynamoDB** | DynamoDB (optional) | SSE-S3/KMS | S3 versioning | Bucket + KMS policies | Low | AWS-centric teams |
| **GCS** | Native, built into bucket | AES-256 | Object versioning | Cloud IAM | Low | GCP-centric teams |
| **AzureRM** | Azure Blob lease (40-60s) | SSE (Azure managed) | Blob snapshots | Azure RBAC | Low | Azure-centric teams |
| **Terraform Cloud** | Built-in | At rest + in transit | Automatic | TFC teams + SSO | Per workspace (free tier) | Teams using TFC |
| **Consul** | Native session | TLS | No | ACL tokens | Server cost | Existing Consul users |
| **etcd** | Native | TLS | No | RBAC | Server cost | Existing etcd users |
| **HTTP** | Custom (external) | Via HTTPS | External | Token | Varies | Custom implementations |

---

## S3 + DynamoDB Deep Dive

> [!info] S3 + DynamoDB
> The most common production backend. S3 stores the state file; DynamoDB provides locking. S3 versioning enables recovery from deletion. Server-side encryption protects sensitive data at rest.

```hcl
# backend.tf — S3 + DynamoDB:
terraform {
  backend "s3" {
    bucket         = "my-org-tf-state"           # Global unique name
    key            = "prod/eks/terraform.tfstate"  # Path within bucket
    region         = "us-east-1"
    encrypt        = true                        # SSE-S3 encryption
    kms_key_id     = "arn:aws:kms:..."           # Optional: use KMS
    dynamodb_table = "terraform-locks"            # Locking table
    profile        = "my-org-admin"              # AWS CLI profile
  }
}
```

### DynamoDB lock table schema

```hcl
# This is created ONCE per account/region:
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  # No sort key; item is `TF_LOCK-<state_path>` → attribute is a JSON document
  # The LockID is automatically computed from the state path.
}

# IAM permissions needed for state operations:
resource "aws_iam_policy" "terraform_state" {
  # Minimum required permissions:
  # S3:
  #   s3:ListBucket           → `terraform init` (list available keys? actually tf-init just needs GetObject/PutObject)
  #   s3:GetObject             → read state
  #   s3:PutObject             → write state (on apply)
  #   s3:DeleteObject          → `terraform destroy` (optional)
  #   s3:GetObjectVersion      → state recovery from versioning
  # DynamoDB:
  #   dynamodb:GetItem         → check lock
  #   dynamodb:PutItem         → acquire lock (conditional write)
  #   dynamodb:DeleteItem      → release lock
  #   dynamodb:DescribeTable   → init
}
```

### S3 versioning for state recovery

```bash
# Enable versioning on the state bucket:
aws s3api put-bucket-versioning \
  --bucket my-org-tf-state \
  --versioning-configuration Status=Enabled

# List versions of a state file:
aws s3api list-object-versions \
  --bucket my-org-tf-state \
  --prefix prod/eks/terraform.tfstate

# Download a specific version:
aws s3api get-object \
  --bucket my-org-tf-state \
  --key prod/eks/terraform.tfstate \
  --version-id <VersionId> \
  recovered.tfstate
```

---

## State Locking

> [!info] State locking
> When a `terraform apply` runs, the backend acquires a lock to prevent another process from writing to the same state simultaneously. The lock is released when the apply completes (or if it errors). If Terraform crashes while the lock is held, it remains locked.

### How locking works

```text
S3 + DynamoDB locking mechanism:
  1. terraform apply starts → DynamoDB PutItem with condition:
     "Insert LockID=path only if LockID does not already exist."
  2. If another process holds the lock → PutItem fails → terraform waits (up to lock timeout).
  3. Apply completes: DeleteItem on LockID (lock released automatically).
  4. If terraform crashes: lock remains. Manually force-unlock.

Lock item structure:
  LockID: "TF_LOCK_prod/eks/terraform.tfstate"
  Info:   JSON of who holds the lock (principal, terraform version, timestamp)
```

### Forcing unlock

```bash
# Check who holds the lock:
aws dynamodb get-item \
  --table-name terraform-locks \
  --key '{"LockID": {"S": "TF_LOCK_prod/eks/terraform.tfstate"}}'

# Force unlock (⚠️ only use if no other process is running):
terraform force-unlock <LOCK_ID>

# The LOCK_ID is shown in the error message when terraform fails.
# Alternative: delete the DynamoDB item directly:
aws dynamodb delete-item \
  --table-name terraform-locks \
  --key '{"LockID": {"S": "TF_LOCK_prod/eks/terraform.tfstate"}}'

# ⚠️  force-unlock can corrupt state if another process is actively writing.
# Verify no one is running terraform before force-unlocking.
```

### Lock timeout

```bash
# Wait up to 5 minutes for a lock:
terraform apply -lock-timeout=5m
# Default: no timeout (fail fast if locked).
```

---

## State Migration

> [!info] State migration
> Terraform makes it safe to move state between backends using `terraform init -migrate-state`. The `-migrate-state` flag copies the existing state to the new backend without destroying any infrastructure.

```bash
# 1. Update backend.tf to point to new backend:
# (Change bucket, key, region, etc.)
terraform {
  backend "s3" {
    bucket = "my-new-tf-state"      # Changed from old bucket
    key    = "prod/eks/terraform.tfstate"
    region = "us-west-2"            # Changed region
  }
}

# 2. Run init with migration:
terraform init -migrate-state
# Prompts: "Do you want to migrate state to the new backend?"
# Enter "yes" → copies state from old to new.

# 3. Verify migration:
terraform state list   # Should show all resources
terraform plan         # Should show "No changes."

# Migration paths:
# Local → S3:         terraform init -migrate-state
# S3 → Terraform Cloud: terraform init -migrate-state
# S3 bucket A → S3 bucket B: change bucket, terraform init -migrate-state
# Any backend → any other: always use -migrate-state

# Non-interactive migration (CI):
terraform init -migrate-state -force-copy
```

### Migration without `-migrate-state` (manual)

```bash
# 1. Download old state:
terraform state pull > old.tfstate

# 2. Update backend.tf with new backend config.

# 3. Initialize new backend (empty):
terraform init -reconfigure

# 4. Push the old state to the new backend:
terraform state push old.tfstate
```

---

## `terraform_remote_state`

> [!info] Remote state data source
> Read outputs from another Terraform configuration's state. This creates a coupling between two configurations — use it when separation is the right pattern (e.g., read VPC IDs from a networking state in a service state).

```hcl
# Read state from another configuration:
data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "my-org-tf-state"
    key    = "network/terraform.tfstate"
    region = "us-east-1"
  }
}

# Use the outputs:
locals {
  vpc_id             = data.terraform_remote_state.network.outputs.vpc_id
  private_subnet_ids = data.terraform_remote_state.network.outputs.private_subnet_ids
}
```

### `terraform_remote_state` considerations

```text
✅ Good for:
  - Networking outputs consumed by service layers.
  - Cross-team dependencies (network team publishes; app team consumes).
  - Read-only access to a single source of truth.

❌ Avoid for:
  - Tight coupling without APIs (use a data API instead).
  - Frequent reads (each plan run reads the remote state file).
  - Cyclic dependencies (state A reads B, state B reads A).

Alternatives:
  - Direct data sources (read VPC by tags instead of remote state).
  - AWS SSM Parameter Store (publish values via terraform, read via data source).
  - AWS Secrets Manager (for secrets).
```

---

## Cross-Links

- [[CICD/Terraform/01_Foundations/01_Terraform_Workflow_and_State]] for state basics
- [[CICD/Terraform/02_Core/01_Modules_and_Environments]] for per-environment state backends
- [[CICD/Terraform/04_Playbooks/01_Troubleshoot_State_Lock_Issues]] for debugging locks
- [[CICD/Terraform/04_Playbooks/02_Refactoring_and_Migration_Playbook]] for state migration
