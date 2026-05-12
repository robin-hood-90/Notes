---
tags: [terraform, core, plan, apply, safety, drift, lifecycle, precondition, postcondition, check, refresh-only, parallelism]
aliases: ["Terraform Plan", "Terraform Apply", "Lifecycle Meta-Argument", "Drift Detection", "Precondition Postcondition", "terraform plan output"]
status: stable
updated: 2026-05-11
---

# Plan, Apply, Safety, and Drift

> [!summary] Goal
> Master reading plan output, safe apply strategies, the `lifecycle` meta-argument (`create_before_destroy`, `prevent_destroy`, `ignore_changes`), custom conditions (`precondition`, `postcondition`), `check` blocks, and drift detection with `-refresh-only` and external tools.

## Table of Contents

1. [Reading Plan Output](#reading-plan-output)
2. [Apply Strategies](#apply-strategies)
3. [Lifecycle Meta-Argument Deep Dive](#lifecycle-meta-argument-deep-dive)
4. [Custom Conditions and Check Blocks](#custom-conditions-and-check-blocks)
5. [Drift Detection](#drift-detection)

---

## Reading Plan Output

> [!info] Plan output
> A plan shows the diff between the current state and desired configuration. Understanding the symbols is essential for safe reviews.

```text
# Plan output symbols:
  +    create
  -    delete (destroy)
  ~    update in-place (modify attributes)
 -/+  destroy first, then create (replace)
 +/-  create first, then destroy (replace with create_before_destroy)
  <=  read (data source)
```

```text
terraform plan output example:

Terraform will perform the following actions:

  # aws_instance.web will be updated in-place
  ~ resource "aws_instance" "web" {
      ~ instance_type = "t3.micro" -> "t3.small"       # Changed attribute
        tags           = { ... }                          # Unchanged
    }

  # aws_s3_bucket.data will be destroyed
  # (because aws_s3_bucket.data is not in configuration)
  - resource "aws_s3_bucket" "data" { ... }

  # aws_vpc.main will be created
  + resource "aws_vpc" "main" {
      + cidr_block       = "10.0.0.0/16"
      + enable_dns_hostnames = true
      + id               = (known after apply)           # Value unknown until apply
      + tags             = { Name = "my-vpc" }
    }

  # aws_db_instance.db will be replaced (force new)
 -/+ resource "aws_db_instance" "db" {
      ~ engine_version = "14.0" -> "15.0"      # Forces replacement
      + db_subnet_group_name = (known after apply)
    }

Plan: 2 to add, 1 to change, 1 to destroy.
```

### Plan options

```bash
# Save plan to file (for atomic apply):
terraform plan -out=tfplan

# Show plan as JSON (for policy engines):
terraform show -json tfplan > plan.json

# Plan destruction only:
terraform plan -destroy

# Plan with refresh only (no changes, check for drift):
terraform plan -refresh-only

# Plan targeting a specific resource (⚠️ see pitfalls):
terraform plan -target="aws_instance.web"

# Plan with variable:
terraform plan -var="instance_type=t3.large"
```

---

## Apply Strategies

### Safe apply patterns

```text
CI/CD (recommended):
  1. terraform plan -out=tfplan      → Review plan (PR comment).
  2. terraform apply tfplan           → Apply the exact plan (no drift).

Interactive:
  1. terraform plan                   → Review plan in terminal.
  2. terraform apply                  → Prompts "yes" before applying.

Emergency:
  terraform apply -auto-approve       → Skip prompt (only in CI/CD).
```

### `-auto-approve` — when it's safe

```bash
# Safe in CI: plan was already reviewed in PR, apply uses the plan:
terraform apply tfplan
# `-auto-approve` is NOT needed when using a plan file.

# Only use -auto-approve without a plan in non-production or emergency:
terraform apply -auto-approve
```

### `-parallelism=N`

```bash
# Controls how many resources Terraform creates/updates concurrently.
# Default: 10. Lower for rate-limited APIs, higher for fast APIs.

terraform apply -parallelism=5       # Slower, less API pressure
terraform apply -parallelism=20      # Faster, more API calls
```

### `-replace=resource` (Terraform 1.1+)

```hcl
# Force recreation of a specific resource (like old taint):
terraform apply -replace="aws_instance.web"

# The resource is destroyed then re-created (or create-before-destroy if specified).
```

### `-target` — why to avoid it

```bash
# ❌ Bad pattern:
terraform apply -target="aws_vpc.main"

# Problems with -target:
#   1. State inconsistency: resources that depend on aws_vpc.main are NOT updated.
#   2. Partial apply: next full `plan` may show unexpected changes.
#   3. Hidden dependencies: you may miss resources that must change together.

# ✅ When it's acceptable:
#   - Emergency hotfix (single resource).
#   - Isolating a specific change during complex refactoring (use sparingly).

# ✅ Better: use a plan file that includes only the intended changes.
terraform plan -out=tfplan
terraform apply tfplan
```

---

## Lifecycle Meta-Argument Deep Dive

> [!info] Lifecycle
> The `lifecycle` meta-argument controls how Terraform handles resource creation, update, and deletion. It has six settings: `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by` (Terraform 1.2+), `precondition`, and `postcondition`.

### `create_before_destroy`

```hcl
resource "aws_instance" "web" {
  # ...

  lifecycle {
    create_before_destroy = true    # Create new instance before destroying old
  }
}

# This is for zero-downtime deployments.
# Requires the resource to support having two simultaneous instances (e.g., ALB target groups).
# If the new instance fails, the old one is still running.
```

### `prevent_destroy`

```hcl
resource "aws_s3_bucket" "critical_data" {
  bucket = "my-org-critical-data"

  lifecycle {
    prevent_destroy = true          # Any terraform destroy/apply that deletes this will ERROR
  }
}

# Protects against accidental deletion of critical resources (databases, DNS zones, admin IAM roles).
# To actually destroy: remove the block, terraform apply, then terraform destroy.
```

### `ignore_changes`

```hcl
resource "aws_instance" "web" {
  # ...

  lifecycle {
    # Ignore tag changes made by AWS Auto Scaling or other scripts:
    ignore_changes = [
      tags["Name"],
      tags["AutoScaled"],
    ]

    # Ignore AMI ID changes (AMI is managed by a separate process):
    ignore_changes = [ami]
  }
}

# ⚠️  ignore_changes can hide real drift. Use it only when:
#   - An external system (not Terraform) modifies the attribute.
#   - The change is safe and expected.
#   - You have another way to detect the change (monitoring, CloudTrail).
```

### `replace_triggered_by` (Terraform 1.2+)

```hcl
# Force resource replacement when a referenced resource changes:
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  lifecycle {
    # Any change to the launch template triggers AMI-based instance replacement:
    replace_triggered_by = [
      aws_launch_template.web.version
    ]
  }
}
```

---

## Custom Conditions and Check Blocks

### Precondition

```hcl
# Precondition: validate BEFORE the resource is created/modified.
# If the condition fails, Terraform does NOT create/update the resource.

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  lifecycle {
    # Validate that we found an AMI (not zero results):
    precondition {
      condition     = length(data.aws_ami.ubuntu.id) > 0
      error_message = "No matching Ubuntu AMI found."
    }
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  lifecycle {
    # Validate the instance type exists (simulated guard):
    precondition {
      condition     = var.instance_type != "t2.micro" || can(regex("^t3", var.instance_type))
      error_message = "t2.micro is not available in this region. Use t3.micro instead."
    }
  }
}
```

### Postcondition

```hcl
# Postcondition: validate AFTER the resource is created.
# If the condition fails, Terraform marks the resource as failed (but has already created it).

resource "aws_lb" "main" {
  name = "my-alb"
  internal = false
  subnets  = var.public_subnets

  lifecycle {
    # After creating the ALB, verify it got a DNS name:
    postcondition {
      condition     = length(self.dns_name) > 0
      error_message = "ALB did not assign a DNS name."
    }
  }
}
```

### `check` blocks (Terraform 1.5+)

> [!info] check blocks
> `check` blocks validate infrastructure AFTER apply WITHOUT blocking. If a check fails, the resource is not destroyed — Terraform marks the check as a warning. Use for: post-deployment validation, SLA monitoring, and external dependencies.

```hcl
# Check block: validates without blocking apply:
check "health" {
  data "http" "api_health" {
    url = "https://${aws_lb.main.dns_name}/health"
  }

  # This runs after every apply.
  # If health check returns non-200, terraform shows a warning but does NOT destroy the ALB.
  assert {
    condition     = data.http.api_health.status_code == 200
    error_message = "${aws_lb.main.dns_name} is not healthy after deployment."
  }
}
```

### Precondition/Postcondition vs Check

```text
                Precondition        Postcondition       Check Block
────────────────────────────────────────────────────────────────────────
When           Before create/update After create/update  After apply (separate)
Failure effect BLOCKS operation     BLOCKS operation    WARNING only (apply succeeds)
Use case       Validate inputs       Validate result    Validate external reachability
Countersigned  Error message shown   Error + resource    Warning + resource NOT destroyed
```

---

## Drift Detection

> [!info] Drift
> Drift occurs when infrastructure changes outside of Terraform. A `terraform plan` after drift shows unexpected diffs. Terraform 1.6+ introduced `-refresh-only` mode to detect drift without proposing changes.

```bash
# Detect drift (Terraform 1.6+):
terraform apply -refresh-only
# Refreshes state from real infrastructure and shows changes, but executes NO actions.

# Old method (deprecated):
terraform refresh

# Using plan:
terraform plan          # Shows if state differs from configuration AND infrastructure
terraform plan -refresh-only  # Only refresh, no plan comparison

# CI/CD drift detection:
#   cron: every 6 hours → terraform plan → if changes, create a PR or alert.
```

### Drift remediation

```bash
# Option 1: Import the drifted resource back into Terraform control:
terraform import <resource_address> <resource_id>
# Then: terraform plan → terraform apply (to reconcile if needed)

# Option 2: Update configuration to match reality:
# Because infrastructure changed — if the change is intentional, update .tf files to match.

# Option 3: Ignore the change (ignore_changes in lifecycle).

# Option 4: Revert the change manually (outside Terraform).
```

---

## Cross-Links

- [[CICD/Terraform/02_Core/01_Modules_and_Environments]] for multi-environment apply strategies
- [[CICD/Terraform/03_Advanced/01_Import_Refactor_and_State_Surgery]] for importing drifted resources
- [[CICD/Terraform/04_Playbooks/01_Troubleshoot_State_Lock_Issues]] for lock problems during apply
- [[CICD/Terraform/02_Core/02_State_Backends_and_Locking]] for state migration and backend locks
