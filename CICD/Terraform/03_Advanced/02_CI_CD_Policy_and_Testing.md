---
tags: [terraform, advanced, cicd, github-actions, atlantis, terraform-cloud, sentinel, opa, checkov, tfsec, terragrunt, secrets, vault, test]
aliases: ["Terraform CI/CD", "Terraform Policy", "Terragrunt", "Terraform Testing", "Terraform Security", "terraform plan PR"]
status: stable
updated: 2026-05-11
---

# CI/CD, Policy, and Testing

> [!summary] Goal
> Master CI/CD for Terraform: GitHub Actions (plan on PR, apply on merge), GitLab CI, Atlantis (plan/apply via PR comments), Terraform Cloud (VCS-driven runs, Sentinel policy checks). Security scanning with tfsec/checkov, secrets management (Vault, SOPS), Terragrunt DRY configs, and integration testing with Terratest.

## Table of Contents

1. [CI/CD with GitHub Actions](#ci-cd-with-github-actions)
2. [Atlantis — PR-Driven Terraform](#atlantis-pr-driven-terraform)
3. [Terraform Cloud and Sentinel](#terraform-cloud-and-sentinel)
4. [Security Scanning and Secrets](#security-scanning-and-secrets)
5. [Terragrunt Deep](#terragrunt-deep)
6. [Testing with Terratest and terraform test](#testing-with-terratest-and-terraform-test)

---

## CI/CD with GitHub Actions

> [!info] CI/CD pipeline
> The standard Terraform CI/CD: open a PR → `terraform plan` runs and comments the plan → review → merge to main → `terraform apply` runs. State is stored in S3 + DynamoDB with OIDC role assumption.

```yaml
# .github/workflows/terraform.yml
name: Terraform

permissions:
  id-token: write               # Needed for OIDC
  contents: read
  pull-requests: write          # Needed for plan PR comments

env:
  TF_VERSION: "1.6.0"
  AWS_REGION: "us-east-1"

jobs:
  plan:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/terraform-plan
          aws-region: ${{ env.AWS_REGION }}
      - run: terraform init
      - run: terraform plan -no-color >> plan_output.txt
      - uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('plan_output.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## Terraform Plan\n```hcl\n' + plan.substring(0, 65535) + '\n```'
            });

  apply:
    if: github.ref_name == 'main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/terraform-apply
          aws-region: ${{ env.AWS_REGION }}
      - run: terraform init
      - run: terraform apply -auto-approve
```

### OIDC IAM trust policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:my-org/my-infra:*"
                }
            }
        }
    ]
}
```

---

## Atlantis — PR-Driven Terraform

> [!info] Atlantis
> Atlantis is a self-hosted Terraform workflow tool. When a PR is opened, Atlantis runs `terraform plan` and comments the output directly in the PR. Comment `atlantis apply` to apply the plan. No manual CLI needed by reviewers.

```yaml
# atlantis.yaml — per-repo config:
version: 3
projects:
  - name: dev
    dir: dev
    terraform_version: v1.6.0
    autoplan:
      enabled: true
      when_modified: ["*.tf", "*.tfvars", "modules/**"]
    apply_requirements: [approved, mergeable]    # Require PR approval + no conflicts

  - name: prod
    dir: prod
    apply_requirements: [approved]
    workflow: prod-workflow

workflows:
  default:
    plan:
      steps:
        - init
        - run: terraform fmt -check -diff
        - plan
  prod-workflow:
    plan:
      steps:
        - init
        - plan:
            extra_args: ["-lock-timeout=300s"]
    apply:
      steps:
        - apply
```

### Atlantis PR comments

```text
Developer: opens PR.
Atlantis:  /atlantis plan
           → Bot comments: "Plan: 2 to add, 0 to change, 0 to destroy."
Reviewer:  Approves PR.
Developer: Comments "/atlantis apply" (optional, or auto-approve).
Atlantis:  → terraform apply. Comments: "Apply complete! Resources: 2 added."
```

---

## Terraform Cloud and Sentinel

> [!info] Terraform Cloud
> Terraform Cloud (TFC) manages Terraform runs remotely. Integrates with VCS providers. Runs trigger on PR/merge. Sentinel is a policy-as-code engine for TFC that validates plans before apply.

```hcl
# TFC backend configuration:
terraform {
  cloud {
    organization = "my-org"
    workspaces {
      name = "production-eks"       # Single workspace
      # OR
      tags = ["production", "eks"]  # Tag-based workspace selection
    }
  }
}
```

### Sentinel policy example

```rego
# sentinel.hcl — deny public S3 buckets
import "tfplan/v2" as tfplan

all_s3_buckets = filter tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket"
    rc.change.after.acl is "public-read" or
    rc.change.after.acl is "public-read-write"
}

main = rule {
    length(all_s3_buckets) is 0
}
# If this fails → plan is BLOCKED before apply.
```

---

## Security Scanning and Secrets

### Security tools

```bash
# tflint — linter for common errors:
tflint --init
tflint

# tfsec — static analysis for security issues:
tfsec .                            # Scans all .tf files for security risks
tfsec --format sarif > results.sarif  # SARIF output for GitHub code scanning

# checkov — broader IaC scanning (Terraform, CloudFormation, K8s, Helm):
checkov --directory .
checkov --framework terraform      # Only Terraform checks

# terrascan — compliance and security:
terrascan scan -t aws
```

### Secrets in Terraform

```hcl
# Method 1: Terraform variables with sensitive=true (state still has secrets):
variable "db_password" {
  type      = string
  sensitive = true
}

# Method 2: HashiCorp Vault provider:
data "vault_generic_secret" "db" {
  path = "secret/database"
}

resource "aws_db_instance" "app" {
  password = data.vault_generic_secret.db.data["password"]
}

# Method 3: AWS Secrets Manager:
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "production/db/password"
}

resource "aws_db_instance" "app" {
  password = data.aws_secretsmanager_secret_version.db.secret_string
}

# Method 4: SOPS-encrypted .tfvars (sops + age/KMS):
# .sops.yaml:
# creation_rules:
#   - encrypted_regex: "^(password|secret|key)$"
#     kms: "arn:aws:kms:..."

# Create encrypted var file: sops --encrypt production.tfvars > production.sops.tfvars
# Use: terraform plan -var-file=production.sops.tfvars
```

---

## Terragrunt Deep

> [!info] Terragrunt
> Terragrunt is a thin wrapper around Terraform that DRY's up configurations and orchestrates multi-module applies. It does NOT replace Terraform — it generates `.tf` files and calls `terraform`.

```hcl
# Root terragrunt.hcl (shared state + provider config):
remote_state {
  backend = "s3"
  config = {
    bucket         = "my-org-tf-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "us-east-1"
}
EOF
}

# Child terragrunt.hcl (dev/vpc/terragrunt.hcl):
include {
  path = find_in_parent_folders()
}

terraform {
  source = "git::https://github.com/my-org/terraform-aws-vpc.git?ref=v2.0.0"
}

inputs = {
  name = "dev-vpc"
  cidr = "10.0.0.0/16"
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
}
```

### Terragrunt dependency

```hcl
# read outputs from another module (auto-dependency order):
dependency "vpc" {
  config_path = "../vpc"
}

inputs = {
  vpc_id     = dependency.vpc.outputs.vpc_id
  subnet_ids = dependency.vpc.outputs.private_subnet_ids
}
```

```bash
# Apply all modules in dependency order:
terragrunt run-all apply

# Plan only changed modules:
terragrunt run-all plan
```

---

## Testing with Terratest and `terraform test`

### Terratest

```go
// test/vpc_test.go — Terratest (Go):
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCDeployment(t *testing.T) {
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/simple-vpc",
        Vars: map[string]interface{}{
            "name": "test-vpc",
            "cidr": "10.0.0.0/16",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.Contains(t, vpcID, "vpc-")
}
```

```bash
go test ./test/ -v -timeout 30m
```

### `terraform test` (Terraform 1.6+)

```hcl
# tests/module_test.tftest.hcl
run "test_basic_vpc" {
  command = plan

  variables {
    name = "test-vpc"
    cidr = "10.0.0.0/16"
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR mismatch: expected 10.0.0.0/16."
  }
}

run "test_production_ha" {
  command = plan

  variables {
    name = "prod-vpc"
    cidr = "10.0.0.0/16"
    private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  }

  assert {
    condition     = length(aws_nat_gateway.this) >= 3
    error_message = "Production VPC should have a NAT Gateway per AZ."
  }
}
```

---

## Cross-Links

- [[CICD/Terraform/01_Foundations/01_Terraform_Workflow_and_State]] for init/plan/apply in CI
- [[CICD/Terraform/02_Core/01_Modules_and_Environments]] for Terragrunt integration
- [[CICD/Terraform/03_Advanced/01_Import_Refactor_and_State_Surgery]] for import in CI pipelines
- [[CICD/Terraform/04_Playbooks/01_Troubleshoot_State_Lock_Issues]] for CI lock failures
