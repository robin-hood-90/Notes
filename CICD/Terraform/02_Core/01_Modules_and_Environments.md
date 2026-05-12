---
tags: [terraform, core, modules, environments, workspaces, registry, terragrunt, composition]
aliases: ["Terraform Modules", "Environments", "Terraform Registry", "Directory Layouts", "Terragrunt", "Workspaces"]
status: stable
updated: 2026-05-11
---

# Modules and Environments

> [!summary] Goal
> Master Terraform modules: root vs child modules, module sources (registry, Git, local), composition, versioning, directory layouts for multi-environment infrastructure, workspaces vs directories, and Terragrunt for DRY configurations.

## Table of Contents

1. [What Is a Module](#what-is-a-module)
2. [Module Sources](#module-sources)
3. [Module Composition](#module-composition)
4. [Directory Layouts and Environments](#directory-layouts-and-environments)
5. [Workspaces](#workspaces)
6. [Terragrunt](#terragrunt)

---

## What Is a Module

> [!info] Module
> A module is any directory of `.tf` files. Every Terraform configuration has at least one module — the **root module** (the directory where you run `terraform plan`). **Child modules** are called from the root module using `module` blocks. A well-designed module encapsulates a reusable set of resources with inputs and outputs.

```text
modules/vpc/
├── main.tf           # Resources (VPC, subnets, IGW, NAT)
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── versions.tf       # Provider and Terraform version constraints
└── README.md         # Documentation for the registry
```

### Module input/output pattern

```hcl
# Root module (my-infra/main.tf):
module "vpc" {
  source = "./modules/vpc"     # Local path

  vpc_cidr = "10.0.0.0/16"
  name     = "production"

  providers = {
    aws = aws                     # Default provider
  }
}

# Child module (modules/vpc/main.tf):
variable "vpc_cidr" { type = string }
variable "name"     { type = string }

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = var.name
  }
}

output "vpc_id" {
  value = aws_vpc.main.id
}
```

---

## Module Sources

| Source | Example | When to use |
|:-------|:--------|:------------|
| **Local** | `./modules/vpc` | Private modules within a repo, during development |
| **Terraform Registry** | `hashicorp/consul/aws` | Public, well-maintained modules. Use for VPC, EKS, ECS, DB |
| **GitHub (HTTPS)** | `github.com/hashicorp/example` | Private or public repo, tag-based versions |
| **Generic Git** | `git::https://example.com/repo.git?ref=v1.0` | Any Git server, any ref (tag, branch, commit) |
| **HTTP URL** | `https://example.com/module.tar.gz` | Tarball archive |
| **S3** | `s3::https://s3-...terraform_module.tar.gz` | S3-hosted archives |
| **GCS** | `gcs::https://www.googleapis.com/...` | GCS-hosted archives |

```hcl
# Terraform Registry module (recommended for common infrastructure):
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"           # Version constraint — ALWAYS pin

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  tags = { Environment = "production" }
}

# Git module (private, with tag):
module "internal_dns" {
  source = "git::https://github.com/my-org/terraform-dns-module.git?ref=v1.2.0"
  domain = "internal.example.com"
}
```

---

## Module Composition

> [!info] Module composition
> A common pattern is composing multiple modules together — VPC module creates network, EKS module creates cluster, RDS module creates database. Each module is independent, and the root module wires them together.

```hcl
# Root module — composes multiple child modules:
module "vpc" {
  source     = "terraform-aws-modules/vpc/aws"
  version    = "5.0.0"
  name       = "myapp-${var.environment}"
  cidr       = var.vpc_cidr
  azs        = var.availability_zones
  private_subnets = cidrsubnets(var.vpc_cidr, 4, 4, 4)
  public_subnets  = cidrsubnets(var.vpc_cidr, 4, 4, 4)
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.0.0"

  cluster_name    = "myapp-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  tags = { Environment = var.environment }
}

module "rds" {
  source = "terraform-aws-modules/rds/aws"
  version = "6.0.0"

  identifier = "myapp-${var.environment}"

  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.micro"

  db_name  = "myapp"
  username = "app"
  password = random_password.db.result

  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.database_subnets
  allocated_storage   = 100
}

resource "random_password" "db" {
  length  = 16
  special = false
}
```

### Passing providers to modules

```hcl
# Provider alias passed to module:
module "eks_west" {
  source = "terraform-aws-modules/eks/aws"

  providers = {
    aws = aws.west          # Pass the west region alias
  }
}
```

---

## Directory Layouts and Environments

> [!info] Environment isolation
> Each environment (dev, staging, prod) needs isolated infrastructure. Two main approaches: **separate directories** (most explicit), and **workspaces** (best for small, identical environments).

### Directory per environment (recommended for most teams)

```text
infra/
├── global/                   # Shared resources (IAM roles, DNS zones)
│   ├── main.tf
│   ├── variables.tf
│   └── backend.tf
├── dev/
│   ├── main.tf              # Root module calling child modules
│   ├── variables.tf
│   ├── terraform.tfvars      # Dev-specific values
│   └── backend.tf            # State key: dev/terraform.tfstate
├── staging/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── backend.tf
└── prod/
    ├── main.tf
    ├── variables.tf
    ├── terraform.tfvars
    └── backend.tf
```

### Directory vs workspace vs Terragrunt

| Approach | State isolation | Code duplication | Learning curve | Best for |
|:---------|:---------------:|:----------------:|:--------------:|----------|
| **Separate dirs** | ✅ Full isolation | Some (duplicate `main.tf`) | Low | Most teams, complex environments, any env count |
| **Workspaces** | ✅ Full isolation | Shared `main.tf` | Low | ≤5 environments, near-identical config |
| **Terragrunt** | ✅ Full isolation | Zero (DRY config) | Medium | Many accounts/regions, repeatable module usage |

---

## Workspaces

> [!info] Workspace
> Workspaces allow multiple state files for the same configuration. Each workspace has its own `.tfstate` with a unique key (e.g., `env:/dev/terraform.tfstate`, `env:/prod/terraform.tfstate`).

```bash
# Create and switch workspace:
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# List and select:
terraform workspace list
terraform workspace select staging

# In configuration — use the workspace name:
locals {
  environment = terraform.workspace
}

resource "aws_instance" "app" {
  tags = {
    Environment = local.environment
  }
}
```

### When to use workspaces

```text
✅ Good for:
  - Quick dev/staging/prod with identical resource counts/names.
  - Testing module changes before promoting.

❌ Avoid for:
  - Environments with different resource counts.
  - When you need different IAM roles per environment.
  - When you need different backend configurations per environment.
  - Disaster recovery isolation (accidental destroy wipes all workspaces in a single state).

Comparison:

           Separate directories        Workspaces
State      Completely separate          Workspace key in state path
Backend    Different backends possible  Same backend, different workspace key
Isolation  Full (different dirs)        Partial (same directory, same backend)
Destroy    Only one env at a time       Choose workspace
Complexity  More files, less nesting     Less files, nesting via workspace
```

---

## Terragrunt

> [!info] Terragrunt
> Terragrunt is a thin wrapper around Terraform that provides DRY configuration, state management, and multi-module orchestration. Install via `brew install terragrunt` or download the binary. It does not replace Terraform — it generates `.tf` files and runs `terraform` CLI commands.

### Terragrunt directory layout

```text
terragrunt/
├── terragrunt.hcl                   # Root config (remote state, provider config)
├── dev/
│   ├── vpc/
│   │   └── terragrunt.hcl          # include + dependency + inputs
│   ├── eks/
│   │   └── terragrunt.hcl
│   └── rds/
│       └── terragrunt.hcl
└── prod/
    ├── vpc/
    │   └── terragrunt.hcl
    ├── eks/
    │   └── terragrunt.hcl
    └── rds/
        └── terragrunt.hcl
```

```hcl
# Root terragrunt.hcl — remote state config:
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

# Generate provider config for all child modules:
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "us-east-1"
}
EOF
}
```

```hcl
# dev/vpc/terragrunt.hcl — include root + module inputs:
include {
  path = find_in_parent_folders()
}

terraform {
  source = "git::https://github.com/my-org/terraform-aws-vpc.git?ref=v2.0.0"
}

inputs = {
  name = "dev-vpc"
  cidr = "10.0.0.0/16"
  azs  = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
}
```

```bash
# Commands (all work like terraform):
terragrunt plan
terragrunt apply
terragrunt apply-all              # Apply all modules in dependency order
terragrunt run-all plan           # Plan all modules in dependency order
terragrunt output
```

---

## Cross-Links

- [[CICD/Terraform/02_Core/02_State_Backends_and_Locking]] for state per environment
- [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] for safe apply across environments
- [[CICD/Terraform/03_Advanced/02_CI_CD_Policy_and_Testing]] for CI/CD with Terragrunt
- [[CICD/Terraform/05_Projects/01_Build_a_Modular_VPC_Stack]] for project using modules
