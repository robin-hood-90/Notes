---
tags: [terraform, iac, cicd, moc]
aliases: ["Terraform MOC", "Terraform Index", "Terraform Learning Path"]
status: stable
updated: 2026-05-11
---

# Terraform

> [!summary] Scope
> Complete Terraform reference from beginner to advanced: HCL syntax, providers, resources, data sources, variables (type system/validation/sensitivity), modules (registry/module composition/Terragrunt), state backends (S3+DynamoDB/GCS/AzureRM/Terraform Cloud), state locking/migration, lifecycle, `precondition`/`postcondition`/`check`, import blocks, `moved` blocks, state surgery, CI/CD (GitHub Actions/Atlantis/Terraform Cloud), policy (Sentinel/OPA/tfsec/checkov), secrets management, `terraform test`, Terratest, troubleshooting playbooks, and production projects.

## Foundations (3 files)

| File | Topics |
|:-----|:-------|
| **F01** [[CICD/Terraform/01_Foundations/01_Terraform_Workflow_and_State]] | Why Terraform (vs Pulumi/CDK/CFN/Ansible), HCL syntax, `init`/`plan`/`apply`/`destroy` workflow, state deep dive (`.tfstate` structure, state commands, security), directory structure, `.gitignore` |
| **F02** [[CICD/Terraform/01_Foundations/02_Providers_Resources_and_Data_Sources]] | Providers (configuration, version constraints, alias, provider-defined functions), resources (type/address), 7 meta-arguments (`count`/`for_each` comparison table, `depends_on`, `provider`, `lifecycle`, `provisioner`, `precondition`/`postcondition`), data sources, `terraform_remote_state` |
| **F03** [[CICD/Terraform/01_Foundations/03_Variables_Outputs_and_Locals]] | Input variables (all type constraints, `optional()`, validation rules with regex), variable precedence table (6 levels), `sensitive`/`nullable`/`ephemeral`, outputs (value, sensitive, precondition), locals (computed values, vs variables), reading outputs in CLI |

## Core (3 files)

| File | Topics |
|:-----|:-------|
| **C01** [[CICD/Terraform/02_Core/01_Modules_and_Environments]] | Module structure (root vs child), module sources (registry/Git/local/S3), version pinning, composition (multiple modules, `providers` pass), directory layouts (env/dir vs workspaces comparison table), Terragrunt intro (DRY config, dependency, run-all) |
| **C02** [[CICD/Terraform/02_Core/02_State_Backends_and_Locking]] | Remote state benefits, backend comparison table (S3/DDB vs GCS vs AzureRM vs TFC vs Consul vs etcd vs HTTP), S3+DynamoDB deep (IAM, KMS, versioning recovery), DynamoDB lock mechanism, force-unlock procedure, state migration (`-migrate-state`), `terraform_remote_state` |
| **C03** [[CICD/Terraform/02_Core/03_Plan_Apply_Safety_and_Drift]] | Plan output symbols (`+`/`-`/`~`/`-/+`/`+/-`), apply strategies (plan file vs auto-approve, `-parallelism`, `-replace`, `-target` pitfalls), lifecycle (create_before_destroy/prevent_destroy/ignore_changes/replace_triggered_by), custom conditions (precondition/postcondition), `check` blocks, drift detection (`-refresh-only`) |

## Advanced (2 files)

| File | Topics |
|:-----|:-------|
| **A01** [[CICD/Terraform/03_Advanced/01_Import_Refactor_and_State_Surgery]] | `import` blocks (Terraform 1.5+ HCL, `-generate-config-out`), `moved` blocks (safe refactoring, vs `terraform state mv` comparison), state CLI (`list`/`show`/`mv`/`rm`/`pull`/`push`), provider replacements (`state replace-provider`), `terraform test` with `.tftest.hcl` |
| **A02** [[CICD/Terraform/03_Advanced/02_CI_CD_Policy_and_Testing]] | GitHub Actions (plan on PR, apply on merge, OIDC), Atlantis (`atlantis.yaml`, PR comments), Terraform Cloud + Sentinel policy, security scanning (tflint/tfsec/checkov/terrascan), secrets (Vault/AWS Secrets Manager/SOPS), Terragrunt deep (dependency, generate, run-all), Terratest | 

## Playbooks (2 files)

| File | Topics |
|:-----|:-------|
| **P01** [[CICD/Terraform/04_Playbooks/01_Troubleshoot_State_Lock_Issues]] | State lock stuck (DynamoDB item, force-unlock), provider/API errors (`TF_LOG=TRACE`), drift detection, state recovery from S3 versioning, credentials/rate-limit fixes |
| **P02** [[CICD/Terraform/04_Playbooks/02_Refactoring_and_Migration_Playbook]] | Moving resources between modules (`moved`/`state mv`), splitting states (`state rm` + `import`), merging states, provider version upgrades, Terraform version upgrades |

## Projects (2 files)

| File | Topics |
|:-----|:-------|
| **Pr01** [[CICD/Terraform/05_Projects/01_Build_a_Modular_VPC_Stack]] | Reusable VPC module with public/private subnets, NAT Gateways, VPC endpoints (S3 + DynamoDB), Flow Logs, `terraform test` + Terratest testing, CI/CD |
| **Pr02** [[CICD/Terraform/05_Projects/02_Multi_Region_EKS_with_CI_CD]] | EKS cluster with managed node groups, add-ons (VPC CNI, CoreDNS, EBS CSI), IRSA, Flux CD, multi-region dev/prod with separate state backends, GitHub Actions CI/CD |

## Cross-Links

- [[CICD/AWS/00_MOC/00_AWS_MOC]] for AWS resource details used in Terraform
- [[CICD/Kubernetes/00_MOC/00_Kubernetes_MOC]] for EKS and K8s concepts
- [[CICD/GitHubActions/00_MOC/00_GitHubActions_MOC]] for CI/CD pipeline configuration
- [[CICD/Harness/02_Core/07_CCM_Cloud_Cost_Management]] for Terraform Cloud cost management

## References

- https://developer.hashicorp.com/terraform/docs
- https://registry.terraform.io/
- https://terragrunt.gruntwork.io/docs/
- https://www.terraform.io/cloud
