---
tags: [terraform, playbook, state-lock, dynamodb, s3, force-unlock, provider-error, drift, recovery]
aliases: ["Terraform State Lock Troubleshooting", "Force Unlock", "TF_LOG", "State Recovery", "Provider Error"]
status: stable
updated: 2026-05-11
---

# Playbook: Troubleshoot State Lock Issues

> [!summary] Goal
> Diagnose and fix state lock issues, provider/API errors, drift, and state corruption. Step-by-step triage with `TF_LOG`, DynamoDB lock debugging, S3 versioning recovery, and force-unlock procedures.

## State Lock Stuck

| Symptom | Likely cause | Check | Fix |
|:--------|:-------------|:------|:-----|
| `Acquiring state lock. Lock Info: ╷ Error: Error acquiring the state lock` | Another terraform process still running, or crashed holding the lock | `aws dynamodb get-item` on lock table | Wait for process; if crashed → `terraform force-unlock <LOCK_ID>` |
| `Failing to acquire lock: ConditionalCheckFailedException` | Lock held by another user | Check `DynamoDB table → Items → lock item Info.Process` | Contact the user; if unresponsive → `terraform force-unlock` |
| `Error locking destination state: AccessDenied` | IAM missing DynamoDB PutItem/DeleteItem | `aws iam simulate-principal-policy` | Add `dynamodb:PutItem`, `dynamodb:DeleteItem`, `dynamodb:GetItem` to role |
| `Force-unlock failed: Lock not held` | Lock already released (stale state cache) | `terraform plan` (should work) | Delete `.terraform` directory and `terraform init` |

### Force unlock procedure

```bash
# 1. Verify no one is actively running terraform:
# Check DynamoDB lock item:
aws dynamodb get-item \
  --table-name terraform-locks \
  --key '{"LockID": {"S": "TF_LOCK_prod/eks/terraform.tfstate"}}'

# 2. Get LOCK_ID from error message or lock info:
# The error shows: "Lock Info: ID: <LOCK_ID>"

# 3. Force unlock:
terraform force-unlock <LOCK_ID>

# 4. Verify:
terraform plan    # Should work now.
```

---

## Provider/API Errors

| Symptom | Check | Fix |
|:--------|:------|:-----|
| `Error configuring the backend "s3": failed to get shared config profile` | AWS credentials not configured | `aws sts get-caller-identity`, check `AWS_PROFILE`, `AWS_ACCESS_KEY_ID` |
| `RequestExpired: Request has expired` | Temporary credentials expired (STS) | Refresh credentials: `aws sts assume-role` again |
| `Throttling: Rate exceeded` (AWS API limit) | Too many API calls in parallel | `terraform apply -parallelism=5` (lower value) |
| `Error creating EKS cluster: operation error EKS: CreateCluster` | Previous cluster in `DELETING` state | Wait for cluster to finish deleting (15-20 min) |
| Provisioner errors via SSH | SSH key not configured, host unreachable, user wrong | Check `connection { type = "ssh" ... }` block |

### Debugging with `TF_LOG`

```bash
# Set log level:
export TF_LOG=INFO                # Default — shows resource changes
export TF_LOG=WARN                # Warnings only
export TF_LOG=DEBUG               # Detailed provider/AWS API calls
export TF_LOG=TRACE               # Every HTTP request/response (VERBOSE)

# Log to file:
export TF_LOG_PATH=/tmp/tf.log

# Log specific components (Terraform 1.7+):
export TF_LOG_CORE=DEBUG          # Terraform core internals
export TF_LOG_PROVIDER_AWS=TRACE  # Only AWS provider trace logs

# Analyze for authentication errors:
#   grep -i "error" /tmp/tf.log
#   grep -i "accessdenied" /tmp/tf.log
```

---

## Drift and State Recovery

| Symptom | Check | Fix |
|:--------|:------|:-----|
| `terraform plan` shows changes you didn't make | Someone modified infrastructure outside Terraform | Verify with `terraform plan -refresh-only`; update config or import |
| `terraform plan` says resources are being deleted (not in .tf) | Resources removed from `.tf` files but still in state | Add them back, or if intentionally removed → `terraform state rm` |
| State file corrupted (JSON parse error) | S3 state file accidentally edited or corrupted | Restore from S3 versioning |
| State file deleted | S3 bucket versioning not enabled | If versioning off → rebuild from scratch or use `terraform import` |

### State recovery from S3 versioning

```bash
# Step 1: List versions:
aws s3api list-object-versions \
  --bucket my-org-tf-state \
  --prefix prod/eks/terraform.tfstate

# Step 2: Download latest good version:
aws s3api get-object \
  --bucket my-org-tf-state \
  --key prod/eks/terraform.tfstate \
  --version-id <VersionId> \
  recovered.tfstate

# Step 3: Push recovered state:
terraform state push recovered.tfstate
```

---

## Cross-Links

- [[CICD/Terraform/02_Core/02_State_Backends_and_Locking]] for DynamoDB locking setup
- [[CICD/Terraform/04_Playbooks/02_Refactoring_and_Migration_Playbook]] for state migration
- [[CICD/Terraform/03_Advanced/01_Import_Refactor_and_State_Surgery]] for import blocks
- [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] for drift detection
