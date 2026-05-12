---
tags: [terraform, project, eks, kubernetes, ci-cd, irsa, flux, addons, vpc, aws]
aliases: ["EKS with CI/CD Project", "Multi-Region EKS", "EKS GitOps Deployment"]
status: stable
updated: 2026-05-11
---

# Project: Multi-Region EKS with CI/CD

> [!summary] Goal
> Deploy an EKS cluster with managed node groups, add-ons (VPC CNI, CoreDNS, EBS CSI), IRSA, and a CI/CD pipeline that builds and deploys a sample app via Flux CD. Includes full Terraform configuration for dev and prod clusters across two regions.

## Architecture

```text
VPC Module → EKS Module → Node Groups → Add-ons → IRSA → Flux CD → Sample App
```

### Project structure

```text
infra/
├── global/
│   ├── main.tf            # IAM roles, OIDC provider for EKS
│   ├── variables.tf
│   └── backend.tf
├── dev/
│   ├── main.tf            # VPC + EKS + node groups + add-ons
│   ├── variables.tf
│   └── backend.tf         # State key: dev/eks/terraform.tfstate
├── prod/
│   ├── main.tf
│   ├── variables.tf
│   └── backend.tf         # State key: prod/eks/terraform.tfstate
└── modules/
    └── eks-cluster/
        ├── main.tf        # Reusable EKS module
        ├── variables.tf
        └── outputs.tf
```

### EKS module

```hcl
# modules/eks-cluster/main.tf:
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.28"

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  # Managed node groups:
  eks_managed_node_groups = {
    main = {
      desired_size = var.node_desired
      min_size     = var.node_min
      max_size     = var.node_max

      instance_types = var.node_instance_types

      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          volume_type = "gp3"
          volume_size = 100
        }
      }

      tags = merge(var.tags, {
        "k8s.io/cluster-autoscaler/enabled" = "true"
      })
    }
  }

  # Add-ons:
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }

  # IRSA for EBS CSI driver:
  enable_irsa = true

  tags = var.tags
}

# EBS CSI driver add-on:
resource "aws_eks_addon" "ebs_csi" {
  cluster_name  = module.eks.cluster_name
  addon_name    = "aws-ebs-csi-driver"
  addon_version = "v1.20.0-eksbuild.1"
}
```

### CI/CD pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy EKS
on:
  push:
    branches: [main]
    paths: ["infra/prod/**"]
permissions:
  id-token: write
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra/prod
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/terraform-apply
          aws-region: us-east-1
      - run: terraform init
      - run: terraform plan
      - run: terraform apply -auto-approve
```

---

## Cross-Links

- [[CICD/Terraform/01_Foundations/02_Providers_Resources_and_Data_Sources]] for provider configuration
- [[CICD/Terraform/02_Core/01_Modules_and_Environments]] for directory layout patterns
- [[CICD/Terraform/03_Advanced/02_CI_CD_Policy_and_Testing]] for CI/CD setup
- [[CICD/Kubernetes/05_Projects/01_Deploy_a_Service_With_HPA_and_Ingress]] for post-EKS app deployment
