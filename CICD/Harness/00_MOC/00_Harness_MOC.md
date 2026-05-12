---
tags: [harness, cicd, moc]
aliases: ["Harness MOC", "Harness Index", "Harness Learning Path"]
status: stable
updated: 2026-05-11
---

# Harness

> [!summary] Scope
> Complete Harness platform reference: platform hierarchy (account/org/project, RBAC, variables, OPA governance), delegates (installation, sizing, selectors, proxy), connectors (K8s, AWS, Git, Docker, Vault, service now), secrets (SSH, files, Vault), services & environments (manifests, artifacts, config files, overrides), pipelines (stages, steps, failure strategies, matrix/loop, triggers, input sets), templates and Git Experience (step/stage/pipeline templates, remote pipelines), CD (K8s rolling/canary/blue-green, Helm, Kustomize, ECS, Serverless, SSH), GitOps (ArgoCD agents, applications, image updater, PR pipelines), CI (builds, test intelligence, caching, Kaniko, Harness Cloud), Feature Flags (boolean/multivariate, targeting, SDKs, flag pipeline), Chaos Engineering (experiments, faults, probes, steady-state), CCM (perspectives, budgets, anomalies, recommendations, auto-stopping), STO (SAST/SCA/DAST/container/IaC scanning, SBOM, exemptions), SRM (SLOs, SLIs, monitored services, error tracking, change intelligence), IDP (software catalog, scorecards, self-service), SEI (DORA metrics, lead time, MTTR, CFR, insights profiles), and troubleshooting playbooks.

## Foundations (8 files)

| File | Topics |
|:-----|:-------|
| **F01** [[CICD/Harness/01_Foundations/01_Harness_Platform_Account_Org_Project_RBAC\|Account Org Project RBAC]] | Account/Org/Project hierarchy, RBAC (resource groups, roles, user groups, service accounts), SSO (SAML, LDAP, SCIM), audit trail, OPA/Rego governance policies, `<+...>` expressions, built-in variables |
| **F02** [[CICD/Harness/01_Foundations/02_Delegates_Installation_Sizing_Operations\|Delegates]] | K8s/Docker/ECS delegates, sizing CPU/memory/heap (`-Xms`), selectors (tags for task matching), delegate tokens, auto-upgrade, proxy configuration, health monitoring |
| **F03** [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools\|Connectors]] | K8s, AWS (keys/IRSA), GCP, Git (GitHub/GitLab/Bitbucket — SSH/HTTP), Docker/ECR/GCR, Helm, Jira, ServiceNow, PagerDuty, Slack. Delegate selectors, test connection |
| **F04** [[CICD/Harness/01_Foundations/04_Secrets_Managers_SSH_Keys_Files\|Secrets]] | Built-in vs Vault vs AWS Secrets Manager vs GCP vs Azure, text secrets, SSH keys, encrypted files, `<+secrets.getValue("id")>`, secret scope (account/org/project) |
| **F05** [[CICD/Harness/01_Foundations/05_Services_Environments_and_Overrides\|Services and Environments]] | Service (manifests: Helm/Kustomize/raw YAML, artifacts: Docker/ECR, config files), environments (prod/staging), environment overrides, infrastructure definitions (K8s/ECS/SSH), service variables |
| **F06** [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow\|Pipelines]] | Deploy, Build, Approval, Custom, Pipeline stages; step groups; failure strategies (Rollback/Abort/Retry/Ignore/ManualIntervention); matrix/forEach looping; conditional execution; step types reference |
| **F07** [[CICD/Harness/01_Foundations/07_Input_Sets_Overlays_and_Triggers\|Input Sets, Overlays, Triggers]] | Input sets (pre-fill params), overlays (merge input sets), triggers (artifact/ webhook/ scheduled), notifications (Slack, PagerDuty, email) |
| **F08** [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience\|Templates and Git Experience]] | Step/stage/pipeline templates with versioning, Git Sync (store pipelines/input sets in GitHub/GitLab), remote pipelines (branch-based development), template linking |

## Core (8 files)

| File | Topics |
|:-----|:-------|
| **C01** [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen\|CD — K8s Deployments]] | Rolling (incremental), canary (percentage-based with phased rollout + verification), blue/green (full stack swap), Helm, Kustomize, raw YAML manifests, pruning, workload types, version labels |
| **C02** [[CICD/Harness/02_Core/02_CD_ECS_Serverless_SSH_Deployments\|CD — ECS, Serverless, SSH]] | ECS rolling + blue/green (CodeDeploy), Serverless Lambda framework, SSH/WinRM command-based deploys on VMs |
| **C03** [[CICD/Harness/02_Core/03_CD_GitOps_ArgoCD_as_Harness\|CD — GitOps (ArgoCD)]] | GitOps agents, applications (repo+path+cluster), sync policy (auto/manual, prune, self-heal), image updater, PR pipelines |
| **C04** [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence\|CI — Builds and Tests]] | Run, Plugin, BuildAndPushDockerRegistry steps; Harness Cloud vs K8s build pods; Kaniko (no DinD needed); test intelligence (selective test execution); cache intelligence |
| **C05** [[CICD/Harness/02_Core/05_Feature_Flags_Creation_Targeting_and_SDKs\|Feature Flags]] | Boolean/multivariate flags, targeting rules (segments, percentages, custom attributes), flag pipeline with approval, server-side + client-side SDKs, flag proxy |
| **C06** [[CICD/Harness/02_Core/06_Chaos_Engineering\|Chaos Engineering]] | Chaos Hubs, fault library (K8s/AWS/GCP/Azure), experiments (steady-state hypothesis → fault → probes), HTTP/cmd/K8s/Prometheus probes, resilience score |
| **C07** [[CICD/Harness/02_Core/07_CCM_Cloud_Cost_Management\|Cloud Cost Management]] | Perspectives (custom cost views), budgets, anomaly detection, recommendations (EC2 right-size, K8s resource, EBS), AutoStopping rules (idle detection, schedule) |
| **C08** [[CICD/Harness/02_Core/08_STO_Security_Testing_Orchestration\|Security Testing Orchestration]] | SAST/SCA/DAST/Container/IaC scanning, SonarQube/Trivy/Snyk/Grype/Bandit, scan modes (ingestion/orchestration/extraction), SBOM (CycloneDX), exemption management |

## Advanced (4 files)

| File | Topics |
|:-----|:-------|
| **A02** [[CICD/Harness/03_Advanced/02_SRM_SLOs_Error_Tracking_and_Change_Intelligence\|SRM — SLOs and Error Tracking]] | SLOs (availability/latency/custom SLI), rolling window/calendar periods, error budget, monitored services (health sources: Prometheus/Datadog/New Relic), change intelligence (deploy → SLO burn correlation), error tracking (APM, smart grouping) |
| **A03** [[CICD/Harness/03_Advanced/03_Internal_Developer_Portal_IDP\|Internal Developer Portal (IDP)]] | Software catalog (Backstage), catalog entities (YAML in Git), scorecards with rules (README/Dockerfile/CI-CD/Security/PagerDuty), self-service actions (create service from template) |
| **A04** [[CICD/Harness/03_Advanced/04_SEI_DORA_Metrics_and_Engineering_Insights\|SEI — DORA Metrics]] | Deployment frequency, lead time for changes, MTTR, change failure rate, integrations (GitHub, GitLab, Jira, Jenkins, PagerDuty), value stream mapping |
| **A05** [[CICD/Harness/03_Advanced/05_Pipelines_as_YAML_Complete_Reference\|Pipeline YAML Reference]] | Full YAML schema reference, identifiers and expressions, variable resolution, template linking, failure strategies, looping strategies |

## Playbooks (5 files)

| File | Topics |
|:-----|:-------|
| **P01** [[CICD/Harness/04_Playbooks/01_Troubleshoot_Delegates\|Troubleshoot Delegates]] | Delegate disconnected, task timeouts (selector mismatch), OOM crashes (`-Xmx`), token expiry, proxy misconfiguration, auto-upgrade disabled |
| **P02** [[CICD/Harness/04_Playbooks/02_Troubleshoot_Pipeline_Failures\|Troubleshoot Pipelines]] | Connector test fails, pipeline timeout, RBAC (permission denied), secret not found (scope mismatch), manifest rendering error, approval timeout |
| **P03** [[CICD/Harness/04_Playbooks/03_Troubleshoot_GitOps_Agents\|Troubleshoot GitOps]] | Agent disconnected (WebSocket), sync error (ComparisonError/Missing/Extra/OutOfSync), image updater not creating PRs, engine OOM |
| **P04** [[CICD/Harness/04_Playbooks/04_Troubleshoot_CI_Builds\|Troubleshoot CI Builds]] | Build pod OOM, test intelligence not running, cache miss every build, DinD not running (K8s build), Kaniko destination error, Harness Cloud capacity |
| **P05** [[CICD/Harness/04_Playbooks/05_Harness_Governance_OPA_Rules\|Governance OPA Rules]] | Pipeline blocked by policy, OPA not evaluated, dry-run vs enforcement, Rego rule scoping, sample Rego rules (naming, approvals, security) |

## Projects (3 files)

| File | Topics |
|:-----|:-------|
| **Pr01** [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback\|CD Pipeline with Approvals & Rollback]] | K8s Helm rolling → chaos experiment → approval → blue/green to prod → rollback on failure. Full service/environment/pipeline YAML |
| **Pr02** [[CICD/Harness/05_Projects/02_GitOps_PR_Pipeline_with_Image_Updater\|GitOps PR Pipeline]] | CI build → push to ECR → image updater creates PR → approve → merge → ArgoCD syncs. GitOps app + PR pipeline YAML |
| **Pr03** [[CICD/Harness/05_Projects/03_Multi_Stage_CI_CD_with_Security_and_SLO\|CI/CD with Security & SLO]] | Maven build → SonarQube → Trivy → Docker → CD staging → Chaos → Load test → Approval → CD prod → SRM SLO update |

## Cross-Links

- [[CICD/GitHubActions/00_MOC/00_GitHubActions_MOC]] for CI/CD with GitHub Actions + Harness
- [[CICD/Docker/00_MOC/00_Docker_MOC]] for container patterns used in Harness CI/CD
- [[CICD/Kubernetes/00_MOC/00_Kubernetes_MOC]] for K8s patterns referenced in Harness CD
- [[CICD/AWS/00_MOC/00_AWS_MOC]] for AWS ECS/EKS deployments from Harness
- [[SystemDesign/02_Core/05_Observability_Logs_Metrics_Traces]] for SRM observability

## References

- https://developer.harness.io/
- https://github.com/harness/harness-core
- https://github.com/harness/harness-cd-community
