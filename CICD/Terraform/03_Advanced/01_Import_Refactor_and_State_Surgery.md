---
tags: [terraform, advanced, import, moved, state-mv, state-rm, replace-provider, terraform-test, state-surgery]
aliases: ["Terraform Import", "terraform import", "moved blocks", "state surgery", "terraform test", "state mv", "state rename"]
status: stable
updated: 2026-05-11
---

# Import, Refactor, and State Surgery

> [!summary] Goal
> Master state refactoring: `import` blocks (Terraform 1.5+, HCL-based import), `moved` blocks (safe resource renaming), CLI commands (`terraform state mv`, `terraform state rm`), provider replacements, `terraform test` for module validation, and state surgery for recovery scenarios.

## Table of Contents

1. [import Blocks (Terraform 1.5+)](#import-blocks)
2. [moved Blocks — Safe Refactoring](#moved-blocks-safe-refactoring)
3. [State CLI Commands](#state-cli-commands)
4. [Provider Replacements](#provider-replacements)
5. [terraform test — Module Testing](#terraform-test-module-testing)

---

## `import` Blocks (Terraform 1.5+)

> [!info] import
> Importing brings an existing resource under Terraform management without re-creation. Terraform 1.5+ introduced `import` blocks — declarative HCL configuration instead of CLI commands. The block tells Terraform the resource address and its real-world ID. After `terraform plan`, Terraform writes the resource configuration (if using `generate-config`) or you must write it manually.

```hcl
# Step 1: Write an import block (add to main.tf or imports.tf):
import {
  to = aws_s3_bucket.existing_data
  id = "my-existing-bucket"
}

# Step 2: Write the resource block (or let Terraform generate it):
resource "aws_s3_bucket" "existing_data" {
  # Terraform will fill in attributes after import
  # You must write this yourself, OR use -generate-config-out
}

# Step 3: Plan and apply:
terraform plan -generate-config-out=generated_resources.tf
# OR (if you wrote the resource block):
terraform plan
terraform apply
# After import: the bucket is now managed by Terraform.
# Next `terraform plan` shows "No changes" if configuration matches.
```

### Import with `-generate-config-out` (auto-generate HCL)

```bash
# Terraform can auto-generate HCL for the imported resource:
terraform plan -generate-config-out=generated.tf

# This creates generated.tf with the full configuration of the imported resource.
# Review and edit: reduce to essential attributes, add lifecycle, etc.
# Then: terraform apply (completes the import).
```

### Import without `import` block (CLI — pre-1.5)

```bash
# Old style (still works):
terraform import aws_s3_bucket.existing_data my-existing-bucket

# Import with module prefix:
terraform import module.vpc.aws_vpc.main vpc-0a1b2c3d4e5f

# Import with count index:
terraform import 'aws_instance.web[0]' i-0abcd1234

# Import with for_each key:
terraform import 'aws_instance.app["web"]' i-0abcd1234
```

### Import best practices

```text
1. Write the resource block FIRST (minimal — just type+name+essential id fields).
2. Run `terraform plan` (shows "import will happen").
3. Use `-generate-config-out` to get the full config (TFC/Terraform 1.5+).
4. Clean up generated config (remove computed-only attributes, sensitive defaults).
5. Review `terraform plan` again — should show "No changes."
6. Apply.

Limitations:
  - Some attributes (especially computed-only) cannot be imported.
  - Sensitive attributes (like archive keys) are not stored in state.
  - Nested resources may need multiple imports.
```

---

## `moved` Blocks — Safe Refactoring

> [!info] moved
> `moved` blocks (Terraform 1.1+) rename or relocate resources in state without destroying them. The old address is mapped to a new address; Terraform automatically updates the state on the next `terraform apply`. This enables safe refactoring: move resources between modules, rename resources, and reorganize configurations without `terraform state mv`.

### Rename a resource

```hcl
# Before: resource "aws_instance" "web_server" { ... }
# After:  resource "aws_instance" "application" { ... }

# moved.tf:
moved {
  from = aws_instance.web_server
  to   = aws_instance.application
}
```

### Move into a module

```hcl
# Before: resource "aws_vpc" "main" { ... } (in root module)
# After:  module "vpc" has aws_vpc.main inside it.

# moved.tf:
moved {
  from = aws_vpc.main
  to   = module.vpc.aws_vpc.main
}
```

### Module version upgrades with `moved`

```hcl
# When upgrading a module that renamed resources:
moved {
  from = module.old_vpc.aws_vpc.main
  to   = module.new_vpc.aws_vpc.main
}
```

### `moved` vs `terraform state mv`

```text
             moved block                     terraform state mv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Declarative   Yes (HCL, in version control)  No (CLI, not tracked)
Safe for CI   Yes (plan shows move)          Needs manual command
Rollback      Revert commit                   State mv back (messy)
Batch moves   Yes multiple                     Manual per resource
Best for      Version-controlled refactoring  Emergency recovery, backends
```

---

## State CLI Commands

> [!info] State CLI
> `terraform state` commands read and modify the state directly. Use them for import, rename, remove, and recovery.

### `terraform state list`

```bash
# List all resources in state:
terraform state list

# List resources matching a module prefix:
terraform state list module.vpc

# List specific resource types:
terraform state list aws_instance
```

### `terraform state show`

```bash
# Show attributes of a specific resource:
terraform state show aws_instance.web

# With module:
terraform state show module.vpc.aws_vpc.main
```

### `terraform state mv`

```bash
# Rename a resource:
terraform state mv aws_instance.old_name aws_instance.new_name

# Move resource into a module:
terraform state mv aws_vpc.main module.vpc.aws_vpc.main

# Move between module addresses:
terraform state mv module.old_vpc.aws_vpc.main module.new_vpc.aws_vpc.main

# With count:
terraform state mv 'aws_instance.web[0]' 'aws_instance.app[0]'

# With for_each:
terraform state mv 'module.old.aws_instance.app["web"]' 'module.new.aws_instance.app["web"]'

# Move all resources from one module to another:
terraform state mv module.old module.new
```

### `terraform state rm`

```bash
# Remove a resource from state (does NOT destroy the resource):
terraform state rm aws_s3_bucket.existing_data

# Remove a module and all its resources:
terraform state rm module.temp_deployment
```

### `terraform state pull` / `push`

```bash
# Download latest state (for debugging or backup):
terraform state pull > backup.tfstate

# Push a state file (⚠️ dangerous — overwrites remote state):
terraform state push backup.tfstate

# Use push only when:
# - Recovering from corrupted state.
# - Restoring from versioned S3 backup.
# - Never: during active terraform operations.
```

---

## Provider Replacements

> [!info] Provider replacement
> When a provider changes its source (e.g., splitting from a merged provider, migrating from community to official), use `terraform state replace-provider` to update all resource references.

```bash
# Replace all provider references:
terraform state replace-provider \
  -auto-approve \
  "registry.terraform.io/hashicorp/aws" \
  "registry.terraform.io/myorg/aws"
```

### When to replace providers

```text
Scenario                             Command
──────────────────────────────────────────────────────────────────
Provider source changed               terraform state replace-provider
hashicorp/consul → mycorp/consul

Provider split into two               terraform state replace-provider
hashicorp/tls + new custom

Moving from community to official     terraform state replace-provider
community/custom → hashicorp/custom
```

---

## `terraform test` — Module Testing

> [!info] terraform test
> `terraform test` (Terraform 1.6+) runs integration tests for modules. Test files (`.tftest.hcl`) define `run` blocks that execute `terraform plan`/`apply`, assert conditions, and verify outputs. Tests run in isolated directories — no impact on real infrastructure.

```hcl
# tests/basic.tftest.hcl
run "test_vpc_creation" {
  command = plan

  variables {
    name = "test-vpc"
    cidr = "10.0.0.0/16"
    azs  = ["us-east-1a", "us-east-1b"]
    private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  }

  # Assert the plan produces expected outputs:
  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block does not match input."
  }
}

run "test_production_settings" {
  command = plan

  variables {
    name = "prod-vpc"
    cidr = "10.0.0.0/16"
    azs  = ["us-east-1a", "us-east-1b", "us-east-1c"]
    private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
    enable_nat_gateway = true
  }

  assert {
    condition     = length(aws_nat_gateway.this) >= 3
    error_message = "Production VPC must have NAT Gateway per AZ."
  }
}
```

```bash
# Run all tests in the module:
terraform test

# Run a specific test file:
terraform test tests/basic.tftest.hcl

# Run tests with verbose output:
terraform test -verbose

# Test output shows pass/fail per run block:
# ✓ test_vpc_creation (plan)
#   - VPC CIDR block matches
# ✓ test_production_settings (plan)
#   - Production VPC has NAT Gateway per AZ
```

---

## Cross-Links

- [[CICD/Terraform/04_Playbooks/02_Refactoring_and_Migration_Playbook]] for step-by-step migration scenarios
- [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] for safe apply after import
- [[CICD/Terraform/03_Advanced/02_CI_CD_Policy_and_Testing]] for CI/CD with import blocks
- [[CICD/Terraform/04_Playbooks/01_Troubleshoot_State_Lock_Issues]] for state recovery
