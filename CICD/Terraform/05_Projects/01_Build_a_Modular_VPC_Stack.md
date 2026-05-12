---
tags: [terraform, project, vpc, module, subnet, nat-gateway, flow-logs, vpc-endpoint, terratest]
aliases: ["Modular VPC Stack Project", "Terraform VPC Module", "VPC with NAT and Endpoints"]
status: stable
updated: 2026-05-11
---

# Project: Build a Modular VPC Stack

> [!summary] Goal
> Build a reusable VPC module with public/private subnets, NAT Gateways, VPC endpoints (S3 + DynamoDB), and VPC Flow Logs. Structure as a Terraform Registry-compatible module with examples, tests, and CI/CD.

## Architecture

```text
VPC (10.0.0.0/16)
├── Public Subnet (10.0.101.0/24) us-east-1a
├── Public Subnet (10.0.102.0/24) us-east-1b
├── Private Subnet (10.0.1.0/24) us-east-1a
├── Private Subnet (10.0.2.0/24) us-east-1b
├── Internet Gateway (IGW)
├── NAT Gateway (in public subnet, per AZ)
├── Gateway Endpoints: S3, DynamoDB
└── VPC Flow Logs → CloudWatch Log Group
```

### Module structure

```text
terraform-aws-vpc/
├── main.tf            # Resources
├── variables.tf       # Input variables
├── outputs.tf          # Output values
├── versions.tf         # Provider constraints
├── README.md           # Module documentation
├── examples/
│   ├── complete/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── outputs.tf
│   └── minimal/
│       └── main.tf
└── tests/
    ├── basic.tftest.hcl   # terraform test
    └── vpc_test.go        # Terratest
```

### Key files

```hcl
# main.tf — VPC resources:
resource "aws_vpc" "main" {
  cidr_block           = var.cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name = var.name
  })
}

resource "aws_subnet" "public" {
  for_each = { for i, az in var.availability_zones : az => az }

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr, 8, var.az_count + index(var.availability_zones, each.key))
  availability_zone = each.key
  map_public_ip_on_launch = true

  tags = merge(var.tags, { Name = "${var.name}-public-${each.key}", Tier = "public" })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = merge(var.tags, { Name = "${var.name}-igw" })
}

resource "aws_nat_gateway" "main" {
  for_each = { for az in var.availability_zones : az => az }

  allocation_id = aws_eip.nat[each.key].id
  subnet_id     = aws_subnet.public[each.key].id
  tags          = merge(var.tags, { Name = "${var.name}-nat-${each.key}" })
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.s3"

  tags = merge(var.tags, { Name = "${var.name}-s3-endpoint" })
}
```

---

## Cross-Links

- [[CICD/Terraform/02_Core/01_Modules_and_Environments]] for module composition patterns
- [[CICD/Terraform/02_Core/02_State_Backends_and_Locking]] for S3 backend for this project
- [[CICD/Terraform/03_Advanced/02_CI_CD_Policy_and_Testing]] for CI/CD setup for this module
- [[CICD/Terraform/05_Projects/02_Multi_Region_EKS_with_CI_CD]] for using this VPC module in a real project
