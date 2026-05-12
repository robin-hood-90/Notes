---
tags: [terraform, iac, foundations, variables, outputs, locals, type-constraints, validation, sensitive]
aliases: ["Terraform Variables", "Terraform Outputs", "Terraform Locals", "Input Variables", "Variable Validation"]
status: stable
updated: 2026-05-11
---

# Variables, Outputs, and Locals

> [!summary] Goal
> Master Terraform's variable system: input variables (types, constraints, validation, sensitivity), outputs (exposing values, cross-config references, sensitive outputs), and locals (reducing repetition, computed values). Understand variable precedence and when to use each.

## Table of Contents

1. [Input Variables](#input-variables)
2. [Type System](#type-system)
3. [Variable Precedence](#variable-precedence)
4. [Validation and Sensitive Variables](#validation-and-sensitive-variables)
5. [Output Values](#output-values)
6. [Local Values](#local-values)

---

## Input Variables

> [!info] Input variable
> Variables make Terraform configurations reusable across environments. Instead of hard-coding `region = "us-east-1"`, you declare `region` as a variable and set its value per environment in `terraform.tfvars` or via `-var`.

```hcl
# variables.tf — declare variables
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  # No default — MUST be provided at runtime
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

variable "vpc_cidrs" {
  description = "CIDR blocks for VPC subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}
```

### Variable attributes

| Attribute | Purpose | Required |
|:----------|:--------|:--------:|
| `description` | Documents the variable's purpose | No |
| `type` | Type constraint (`string`, `number`, `bool`, `list`, `map`, `object`, `set`, `tuple`, `any`) | No (default `any`) |
| `default` | Default value if none provided | No |
| `validation` | Custom validation rules | No |
| `sensitive` | `true` hides value in plan output and logs | No |
| `nullable` | `false` (default) means variable cannot be null | No |
| `ephemeral` | `true` (Terraform 1.10+) — value never stored in state | No |

---

## Type System

### Primitive types

```hcl
variable "app_name" {
  type    = string
  default = "myapp"
}

variable "replica_count" {
  type    = number
  default = 3
}

variable "enable_monitoring" {
  type    = bool
  default = true
}
```

### Collection types

```hcl
variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "instance_tags" {
  type    = map(string)
  default = { Name = "web", Env = "prod" }
}

variable "unique_ports" {
  type    = set(number)
  default = [80, 443, 8080]
}
```

### Structural types

```hcl
# Object — named fields with specific types:
variable "database" {
  type = object({
    engine         = string
    engine_version = string
    instance_class = string
    storage        = number
    multi_az       = optional(bool, false)     # Terraform 1.3+
    backup_window  = optional(string, "03:00-04:00")
  })
  default = {
    engine         = "postgres"
    engine_version = "15"
    instance_class = "db.t3.micro"
    storage        = 100
  }
}

# Tuple — typed list where each position has its own type:
variable "cdn_config" {
  type = tuple([string, number, bool])
  default = ["standard", 30, true]
  # Index 0: string (price_class)
  # Index 1: number (ttl_seconds)
  # Index 2: bool (enabled)
}

# Optional with defaults (Terraform 1.3+):
# optional(type, default)
# The default for optional() is null if not specified.
# The default for the variable's default is applied if the entire variable is not set.
```

### Type constraint selection

```text
Use case                                      Type
─────────────────────────────────────────────────────────────
Simple value (name, ID, region)               string
Numeric count or port                         number
Toggle                                        bool
List of subdomain names                       list(string)
Map of tag values                             map(string)
Unique set of ports                           set(number)
Complex config with named fields              object({})
Positional heterogeneous data                 tuple([type1, type2])
No constraint (any type)                      any
```

---

## Variable Precedence

> [!info] Variable precedence
> Variables can be set in multiple ways. When multiple sources define the same variable, the **highest precedence wins**.

| Precedence | Source | Example |
|:----------:|:-------|:--------|
| **1 (highest)** | `-var` command line flag | `terraform apply -var='instance_type=t3.large'` |
| **2** | `-var-file` command line flag | `terraform apply -var-file=prod.tfvars` |
| **3** | `*.auto.tfvars` (alphabetical order) | `production.auto.tfvars` |
| **4** | `terraform.tfvars` | Default file loaded automatically |
| **5** | Environment variable `TF_VAR_<name>` | `TF_VAR_region=us-west-2 terraform plan` |
| **6 (lowest)** | `default` in `variable` block | `variable "region" { default = "us-east-1" }` |

```bash
# Environment variable pattern:
export TF_VAR_region="eu-west-1"
export TF_VAR_instance_type="t3.nano"
terraform plan
```

```hcl
# terraform.tfvars — loaded automatically:
region        = "us-east-1"
instance_type = "t3.micro"
tags = {
  Environment = "production"
}

# *.auto.tfvars — loaded automatically, alphabetical precedence:
# dev.auto.tfvars, staging.auto.tfvars, production.auto.tfvars
```

---

## Validation and Sensitive Variables

### Variable validation

```hcl
variable "instance_type" {
  type        = string
  description = "EC2 instance type. Must start with t3, c5, or m5."

  validation {
    condition     = can(regex("^(t3|c5|m5)\\.", var.instance_type))
    error_message = "Instance type must start with t3., c5., or m5. Got: ${var.instance_type}"
  }
}

variable "db_password" {
  type        = string
  description = "Database password (minimum 12 characters, must include number and special char)"

  validation {
    condition     = length(var.db_password) >= 12
    error_message = "DB password must be at least 12 characters."
  }

  validation {
    condition     = can(regex("[0-9]", var.db_password))
    error_message = "DB password must contain at least one number."
  }

  validation {
    condition     = can(regex("[^a-zA-Z0-9]", var.db_password))
    error_message = "DB password must contain at least one special character."
  }
}

variable "environment" {
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}
```

### Sensitive variables

```hcl
variable "db_master_password" {
  type        = string
  description = "RDS master password"
  sensitive   = true    # Hides value in CLI output and logs
}

# In the plan output, sensitive values show as (sensitive).
# To read a sensitive output (Terraform Cloud can output them with restrictions):
terraform output db_password      # Shows: (sensitive)
terraform output -json db_password  # Shows the actual value in JSON
```

### Nullable variables

```hcl
variable "optional_config" {
  type     = string
  nullable = true   # Allows setting null explicitly
  default  = null   # No default if not provided
}

# Usage with conditional:
resource "aws_s3_bucket" "data" {
  bucket = var.bucket_name != null ? var.bucket_name : "default-bucket"
}
```

---

## Output Values

> [!info] Output value
> Outputs return information about your infrastructure after apply. Used for: displaying useful info, sharing values with other Terraform configurations (`terraform_remote_state`), and CI/CD pipelines.

```hcl
# outputs.tf
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "instance_public_ips" {
  description = "Public IPs of web instances"
  value       = aws_instance.web[*].public_ip
}

output "database_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true   # Mark as sensitive
}

output "kubeconfig" {
  description = "Kubeconfig for the EKS cluster"
  value       = aws_eks_cluster.main.kubeconfig
  sensitive   = true
}

# Output with precondition (Terraform 1.2+):
output "load_balancer_dns" {
  value = aws_lb.main.dns_name

  precondition {
    condition     = length(aws_lb_target_group.main.arn) > 0
    error_message = "Load balancer must have at least one target group."
  }
}
```

### Reading outputs

```bash
# CLI:
terraform output                          # All outputs
terraform output vpc_id                   # Specific output
terraform output -json                    # All outputs as JSON
terraform output -raw instance_public_ip  # Raw string value (no quotes)
```

---

## Local Values

> [!info] Local value
> Locals assign a name to an expression for reuse within a module. Unlike variables, locals are NOT set by the caller — they are computed within the module. Use them to avoid repeating complex expressions.

```hcl
# locals.tf
locals {
  # Common tags for all resources:
  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Project     = var.project_name
    Owner       = var.owner
  }

  # Computed name for resources:
  name_prefix = "${var.project_name}-${var.environment}"

  # CIDR blocks computed from input:
  public_subnet_cidrs  = [for i in range(3) : cidrsubnet(var.vpc_cidr, 8, i)]
  private_subnet_cidrs = [for i in range(3) : cidrsubnet(var.vpc_cidr, 8, i + 3)]

  # Conditionally set a value:
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"
}

# Using locals in resources:
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = locals.instance_type

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web"
  })
}
```

### Variables vs locals

```text
           Variables                          Locals
──────────────────────────────────────────────────────────────────────
Set by     Caller (.tfvars, -var, env var)   Module itself (computed)
Purpose    Parameterize module behavior       Reduce repetition
Type       Must be declared with type         Expression evaluated at runtime
Override   Yes (any value at apply time)       No (computed within module)
Use for    User-provided settings              Computed values shared across resources
```

---

## Cross-Links

- [[CICD/Terraform/01_Foundations/01_Terraform_Workflow_and_State]] for applying with -var
- [[CICD/Terraform/01_Foundations/02_Providers_Resources_and_Data_Sources]] for using variables in resources
- [[CICD/Terraform/02_Core/01_Modules_and_Environments]] for passing variables between modules
- [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] for precondition in outputs
