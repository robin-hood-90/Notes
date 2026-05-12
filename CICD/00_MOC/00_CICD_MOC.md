---
tags: [cicd, devops, moc]
aliases: ["CI/CD MOC", "DevOps MOC"]
status: stable
updated: 2026-05-11
---

# CI/CD (Tools and Practices)

> [!summary] Scope
> Cross-tool CI/CD concepts (pipelines, artifacts, deployment strategies, secrets, supply chain security) plus pointers to tool-specific sections (AWS, Docker, GitHub, GitHub Actions, Jenkins, Harness, Kafka, Kubernetes, Terraform).

## Tool MOCs

1. [[CICD/AWS/00_MOC/00_AWS_MOC]] — IAM, EC2, VPC, S3, Lambda, ECS, EKS, RDS, DynamoDB, CloudFront, Route 53, CloudWatch, KMS, CloudFormation, WAF, CloudTrail, SSM, Autoscaling, Security
2. [[CICD/Docker/00_MOC/00_Docker_MOC]] — Images, containers, Compose, Dockerfile, volumes, networking, registries, building, signing, security
3. [[CICD/GitHub/00_MOC/00_GitHub_MOC]] — Repos, branches, PRs, Actions, releases, packages, security, project management
4. [[CICD/GitHubActions/00_MOC/00_GitHubActions_MOC]] — Workflows, runners, OIDC, build caching, test matrix, deployment actions, marketplace
5. [[CICD/Jenkins/00_MOC/00_Jenkins_MOC]] — Pipelines, jobs, plugins, shared libraries, master/agent, multibranch, credentials
6. [[CICD/Harness/00_MOC/00_Harness_MOC]] — CD pipelines, GitOps, CI, Feature Flags, Chaos Engineering, CCM, STO, SRM, IDP, SEI
7. [[CICD/Kafka/00_MOC/00_Kafka_MOC]] — Architecture, producers, consumers, topics, partitions, storage, replication, stream processing, Schema Registry, KRaft
8. [[CICD/Kubernetes/00_MOC/00_Kubernetes_MOC]] — Pods, deployments, services, ingress, storage, RBAC, Helm, Kustomize, operators, service mesh, PDB, autoscaling
9. [[CICD/Terraform/00_MOC/00_Terraform_MOC]] — HCL, providers, resources, state, modules, backends, CI/CD, Terragrunt, policy, testing

## Practices

1. [[CICD/01_Foundations/01_Pipelines_Basics]] — CI vs CD, pipeline stages, branch strategies, triggers, artifact promotion
2. [[CICD/01_Foundations/02_Build_Artifacts_and_Versioning]] — Artifact types, registries, SemVer/Git SHA/CalVer, immutable tags, signing, SBOM
3. [[CICD/02_Core/01_Deployment_Strategies]] — Rolling, blue/green, canary, feature flags, database migrations (expand/contract)
4. [[CICD/02_Core/02_Secrets_Management]] — Secret types, OIDC vs access keys, secret injection patterns, secret scanning tools
5. [[CICD/03_Advanced/01_Supply_Chain_Security_SLSA_Basics]] — Supply chain threats, SLSA levels I-IV, provenance/attestation/signing, dependency management

## Playbooks

1. [[CICD/04_Playbooks/01_Triage_Failing_Pipeline]] — Classify failure, triage workflow, fast mitigations
2. [[CICD/04_Playbooks/02_Rollback_and_Stabilize_Production]] — Stop the bleeding, validate rollback, prevent recurrence
3. [[CICD/04_Playbooks/03_Secret_Leak_Response]] — Rotate credentials, remove from git history, add scanning

## Projects

1. [[CICD/05_Projects/01_Build_a_CI_Pipeline_for_React_App]] — Lint → typecheck → test → build → cache → publish. Complete GitHub Actions YAML + config
2. [[CICD/05_Projects/02_Build_a_CD_Pipeline_BlueGreen]] — Build → push → Helm deploy green → smoke test → traffic switch → scale down blue. Complete GitHub Actions YAML + Helm chart

## Cross-Links

- [[SystemDesign/00_MOC/00_SystemDesign_MOC]] for deployment architecture
- [[SystemDesign/02_Core/08_Incident_Response_and_Postmortem]] for incident analysis

## References

- https://slsa.dev/
- https://docs.sigstore.dev/
- https://snyk.io/
