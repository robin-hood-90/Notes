---
tags: [terraform, playbook, refactoring, migration, state-mv, moved, state-split, merge, provider-upgrade, version-upgrade]
aliases: ["Terraform Refactoring", "State Migration", "State Split", "Provider Upgrade", "Module Migration"]
status: stable
updated: 2026-05-11
---

# Playbook: Refactoring and Migration

> [!summary] Goal
> Step-by-step guides for common state refactoring scenarios: moving resources between modules, renaming resources, splitting/merging states, upgrading providers, and upgrading Terraform versions.

## Moving Resources Between Modules

### Scenario: promote a resource from root module to child module

```bash
# 1. Create the module structure and move the resource block into it.
# 2. Add a moved block in the root module:

# moved.tf (in root module):
moved {
  from = aws_s3_bucket.data
  to   = module.storage.aws_s3_bucket.data
}

# 3. Run terraform plan → shows "Move" operation (no destroy/create).
# 4. terraform apply → state is updated.

# If terraform version < 1.1, use state mv:
terraform state mv aws_s3_bucket.data module.storage.aws_s3_bucket.data
```

---

## Splitting a Large State

### Scenario: move some resources from a shared state to a dedicated state

```bash
# 1. Create new directory with new backend config:
infra/
├── network/backend.tf   # State key: network/terraform.tfstate
├── services/backend.tf  # State key: services/terraform.tfstate
└── old-shared/          # Current state (will be retired)

# 2. Remove resources from old state:
terraform state rm -state=old-shared/terraform.tfstate \
  module.networking.aws_vpc.main
terraform state rm -state=old-shared/terraform.tfstate \
  module.networking.aws_subnet.private

# 3. In new directory, import them into the new state:
# (cd network && terraform init)
terraform import -state=network/terraform.tfstate \
  module.networking.aws_vpc.main vpc-abc123
```

---

## Provider Upgrades

### Scenario: major provider version (hashicorp/aws 4.x → 5.x)

```bash
# 1. Update required_providers:
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"    # From ~> 4.0
    }
  }
}

# 2. Review the provider UPGRADE GUIDE for breaking changes.
#    Check: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/guides/version-5-upgrade

# 3. Update providers:
terraform init -upgrade

# 4. Check for issues:
terraform plan
# If there are changes, review and apply.
```

---

## Cross-Links

- [[CICD/Terraform/03_Advanced/01_Import_Refactor_and_State_Surgery]] for moved blocks and import
- [[CICD/Terraform/02_Core/02_State_Backends_and_Locking]] for state backend migration
- [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] for drift detection after migration
- [[CICD/Terraform/04_Playbooks/01_Troubleshoot_State_Lock_Issues]] for locking during migration
