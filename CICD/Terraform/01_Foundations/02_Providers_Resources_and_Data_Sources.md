---
tags: [terraform, iac, foundations, providers, resources, data-sources, count, for-each, depends-on, lifecycle, provisioner, meta-arguments]
aliases: ["Terraform Providers", "Resources", "Data Sources", "count vs for_each", "lifecycle", "depends_on", "provisioners"]
status: stable
updated: 2026-05-11
---

# Providers, Resources, and Data Sources

> [!summary] Goal
> Master Terraform's building blocks: providers (configuration, versioning, alias, provider-defined functions), resources (all 7 meta-arguments: `count`, `for_each`, `provider`, `depends_on`, `lifecycle`, `provisioner`), data sources (reading existing infrastructure), and the decision framework for choosing the right block type.

## Table of Contents

1. [Providers](#providers)
2. [Resources](#resources)
3. [Resource Meta-Arguments](#resource-meta-arguments)
4. [Data Sources](#data-sources)

---

## Providers

> [!info] Provider
> A provider is a plugin that translates Terraform's resource definitions into API calls to a target platform (AWS, GCP, Azure, GitHub, Cloudflare, etc.). Each provider has its own set of resources (e.g., `aws_instance`, `aws_s3_bucket`) and data sources. Providers are downloaded from the Terraform Registry during `terraform init`.

### Provider configuration

```hcl
# Required providers block (Terraform 0.13+) — always in a versions.tf or main.tf:
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"         # Source address from registry
      version = "~> 5.0"                # Version constraint
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5, < 4.0"         # Range constraint
    }
  }
  required_version = ">= 1.0, < 2.0"    # Terraform CLI version
}
```

### Version constraints

| Constraint | Example | Meaning |
|:-----------|:--------|:--------|
| `>= 1.0` | `>= 5.0` | Version 5.x and above |
| `~> 1.0` | `~> 5.0` | PATCH-only: `5.0 ≤ x < 6.0` |
| `~> 1.2.0` | `~> 5.2.0` | Only `5.2.0` – `5.2.x` |
| `>= 1.0, < 2.0` | `>= 5.0, < 6.0` | Range: excludes minors |
| `!= 1.0.1` | `!= 5.1.0` | Exclude specific version |

### Provider alias — multiple configurations

```hcl
# Default provider (uses default region):
provider "aws" {
  region = "us-east-1"
}

# Alias for a second region:
provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

# Use alias in a resource:
resource "aws_vpc" "primary" {
  cidr_block = "10.0.0.0/16"
  # provider = aws (default — not needed)
}

resource "aws_vpc" "secondary" {
  provider   = aws.west
  cidr_block = "10.1.0.0/16"
}
```

### Provider-defined functions (Terraform 1.8+)

```hcl
# Terraform 1.8 added provider-defined functions — providers can expose custom functions.
# For example, the AWS provider may expose:
# provider::aws::arn_build(partition, service, region, account, resource)

# Call using the `provider::<provider_name>::<function>()` syntax:
locals {
  policy_arn = provider::aws::arn_build("aws", "iam", "", data.aws_caller_identity.current.account_id, "policy/my-policy")
}
```

---

## Resources

> [!info] Resource
> A resource is the most important block — it declares an infrastructure object that Terraform creates, manages, and destroys. Resources have a type (determined by the provider) and a local name (for referencing within the configuration).

```hcl
# Basic resource:
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}
```

### Resource addressing

```text
Address                     Refers to
──────────────────────────────────────────────────────────────
aws_instance.web            Single resource
aws_instance.web[0]         First instance in count
aws_instance.web["key"]     Instance in for_each with key "key"
module.vpc.aws_vpc.main     Resource in a module
data.aws_ami.ubuntu          Data source
```

---

## Resource Meta-Arguments

> [!info] Meta-arguments
> Every resource supports 7 meta-arguments that control how Terraform creates, updates, and destroys it. These are separate from the resource's own arguments.

### 1. `count` — create N instances

```hcl
# Create 3 identical EC2 instances (list-based):
variable "subnet_ids" {
  type = list(string)
}

resource "aws_instance" "app" {
  count         = length(var.subnet_ids)
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  subnet_id     = var.subnet_ids[count.index]

  tags = {
    Name = "app-${count.index + 1}"
  }
}
```

### 2. `for_each` — create instances from map keys

```hcl
# Create instances from a map (key is used as the resource identifier):
variable "instances" {
  type = map(object({
    instance_type = string
    subnet_id     = string
  }))
  default = {
    web = { instance_type = "t3.micro", subnet_id = "subnet-abc" }
    api = { instance_type = "t3.small", subnet_id = "subnet-def" }
  }
}

resource "aws_instance" "app" {
  for_each      = var.instances
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = each.value.instance_type
  subnet_id     = each.value.subnet_id

  tags = {
    Name = each.key
  }
}
# Referencing: aws_instance.app["web"], aws_instance.app["api"]
```

### `count` vs `for_each` — when to use each

```text
                            count                           for_each
──────────────────────────────────────────────────────────────────────────
Source data type            list                            map or set of strings
Resource identity           `count.index`                   `each.key`
Can delete from middle?     NO (shifts all indices!)        YES (by key)
Can have mixed configs?     NO (all same config)            YES (per-key config)
Can reference elsewhere?    `resource.name[0]`              `resource.name["api"]` — clearer

Rule: prefer `for_each` when the set of instances is a map; use `count` only for simple numbered lists.
When the list may shrink → use `for_each` or suffer index shifting.
```

### 3. `depends_on` — explicit dependency

```hcl
# Terraform automatically detects most dependencies via references.
# Use depends_on when the dependency is implicit (e.g., a role needs time to propagate):

resource "aws_iam_role_policy" "s3_policy" {
  name = "s3-access"
  role = aws_iam_role.role.name
  policy = jsonencode({ ... })
}

resource "aws_s3_bucket" "data" {
  depends_on = [aws_iam_role_policy.s3_policy]  # Wait for policy to propagate
}
```

### 4. `provider` — select provider alias

```hcl
provider "aws" {
  region = "us-west-2"
  alias  = "west"
}

resource "aws_vpc" "secondary" {
  provider   = aws.west     # Use west region
  cidr_block = "10.0.0.0/16"
}
```

### 5. `lifecycle` — creation, update, and deletion behavior

```hcl
resource "aws_db_instance" "main" {
  # ... regular arguments ...

  lifecycle {
    create_before_destroy = true   # Create new before destroying old (zero-downtime)
    prevent_destroy       = true   # Terraform will ERROR on destroy of this resource

    ignore_changes = [
      tags,                         # Ignore tag changes made outside Terraform
      engine_version,               # Ignore minor version upgrades applied automatically
    ]
  }
}

# create_before_destroy requires that the resource supports having two live simultaneously.
# prevent_destroy blocks: terraform destroy, terraform apply -destroy, and resource deletion.

# Before removing prevent_destroy: remove the meta-argument, then apply, then destroy.
```

### 6. `provisioner` — run scripts on resources (last resort)

> [!warning] Provisioners are a last resort
> Terraform should be declarative. Provisioners are imperative scripts tied to resource creation/destruction. They introduce side effects that Terraform cannot track. **Prefer**: user data (cloud-init), Packer (custom AMIs), or a configuration management tool.

```hcl
resource "aws_instance" "web" {
  # ... regular arguments ...

  # File provisioner — copy a file to the instance:
  provisioner "file" {
    source      = "app.conf"
    destination = "/etc/myapp/app.conf"

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }

  # Remote-exec — run commands after creation:
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y nginx",
    ]
  }

  # Local-exec — run commands locally after resource creation:
  provisioner "local-exec" {
    command = "aws ecr create-repository --repository-name my-app || true"
  }

  # Destroy-time provisioner (runs on destruction):
  provisioner "local-exec" {
    when    = destroy
    command = "echo 'Resource destroyed: ${self.id}' >> /tmp/destroy.log"
  }
}
```

### 7. `precondition` / `postcondition` (Terraform 1.2+)

```hcl
# Precondition: validate inputs BEFORE the resource is created/updated.
resource "aws_instance" "web" {
  ami           = "ami-abc123"
  instance_type = var.instance_type

  lifecycle {
    precondition {
      condition     = var.instance_type != "t2.micro" || can(regex("^ami-0c55b159cbfafe1f0|^ami-abc", self.ami))
      error_message = "t2.micro can only use specific AMIs. Check ami ID."
    }
    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance did not receive a public IP address."
    }
  }
}
```

---

## Data Sources

> [!info] Data source
> A data source reads information from existing infrastructure that Terraform does NOT manage. It's how you query current state without importing the resource. Common uses: fetch the latest AMI, get VPC IDs by tags, read secrets, find availability zones.

```hcl
# Data source to find the latest Ubuntu AMI:
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Using the data source in a resource:
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}

# Read existing VPC:
data "aws_vpc" "main" {
  tags = {
    Name = "main-vpc"
  }
}

# Read subnets from that VPC:
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  tags = {
    Tier = "private"
  }
}

# Resource vs Data Source:
# resource: "I want Terraform to CREATE and MANAGE this thing."
# data source: "I want to READ this thing. Terraform should NOT manage it."
```

### `terraform_remote_state` — read from another state

```hcl
# Read outputs from another Terraform configuration's state:
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "my-org-tf-state"
    key    = "network/terraform.tfstate"
    region = "us-east-1"
  }
}

# Use the outputs (must be declared as `output` in the remote configuration):
resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.network.outputs.private_subnet_ids[0]
}
```

---

## Cross-Links

- [[CICD/Terraform/01_Foundations/01_Terraform_Workflow_and_State]] for init and apply flow
- [[CICD/Terraform/01_Foundations/03_Variables_Outputs_and_Locals]] for variable types used in resources
- [[CICD/Terraform/02_Core/01_Modules_and_Environments]] for module composition
- [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] for lifecycle conditions
