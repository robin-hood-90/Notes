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
> Import brings existing resources under Terraform management without re-creation. Terraform 1.5+ introduced `import` blocks — declarative HCL configuration instead of CLI commands.

```hcl
import {
  to = aws_s3_bucket.existing_data
  id = "my-existing-bucket"
}

resource "aws_s3_bucket" "existing_data" {
  # Write this yourself, or use -generate-config-out
}

terraform plan -generate-config-out=generated_resources.tf
```

```bash
# Pre-1.5 CLI style (still works):
terraform import aws_s3_bucket.existing_data my-existing-bucket
terraform import module.vpc.aws_vpc.main vpc-0a1b2c3d4e5f
terraform import 'aws_instance.web[0]' i-0abcd1234
```

---

## `moved` Blocks — Safe Refactoring

> [!info] moved
> `moved` blocks (Terraform 1.1+) rename or relocate resources in state without destroying them. The old address is mapped to a new address; Terraform updates the state on the next `terraform apply`.

```hcl
# Rename a resource:
moved {
  from = aws_instance.web_server
  to   = aws_instance.application
}

# Move into a module:
moved {
  from = aws_vpc.main
  to   = module.vpc.aws_vpc.main
}

# Module version upgrade:
moved {
  from = module.old_vpc.aws_vpc.main
  to   = module.new_vpc.aws_vpc.main
}
```

| Aspect | `moved` block | `terraform state mv` |
|:-------|:-------------:|:---------------------:|
| Declarative | ✅ HCL, version-controlled | ❌ CLI, not tracked |
| Safe for CI | ✅ Plan shows move | Needs manual command |
| Rollback | Revert commit | State mv back (messy) |
| Best for | Version-controlled refactoring | Emergency recovery |

---

## State CLI Commands

```bash
# List all resources:
terraform state list
terraform state list module.vpc

# Show attributes:
terraform state show aws_instance.web

# Move (rename or re-parent):
terraform state mv aws_instance.old aws_instance.new
terraform state mv aws_vpc.main module.vpc.aws_vpc.main
terraform state mv module.old module.new           # Move all resources

# Remove from state (do NOT destroy):
terraform state rm aws_s3_bucket.data
terraform state rm module.temp_deployment

# Pull/push — for backup, recovery (⚠️ push is dangerous):
terraform state pull > backup.tfstate
terraform state push backup.tfstate   # Overwrites remote state
```

---

## Provider Replacements

```bash
# When a provider changes source (e.g., hashicorp/aws → myorg/aws):
terraform state replace-provider \
  -auto-approve \
  "registry.terraform.io/hashicorp/aws" \
  "registry.terraform.io/myorg/aws"
```

---

## `terraform test` — Module Testing

> [!info] terraform test (1.6+)
> Run integration tests for modules. Test files (`.tftest.hcl`) run `plan`/`apply`, assert conditions, and verify outputs.

```hcl
# tests/basic.tftest.hcl
run "test_vpc_creation" {
  command = plan
  variables = { name = "test-vpc", cidr = "10.0.0.0/16" }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR mismatch."
  }
}
```

```bash
terraform test
terraform test -verbose
```

---

## Cross-Links

- [[CICD/Terraform/04_Playbooks/02_Refactoring_and_Migration_Playbook]] for step-by-step migrations
- [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] for safe apply after import
- [[CICD/Terraform/03_Advanced/02_CI_CD_Policy_and_Testing]] for CI/CD with import blocks
