---
tags: [harness, foundations, pipelines, stages, steps, failure-strategies, looping, matrix, conditional-execution, step-groups]
aliases: ["Harness Pipelines", "Pipeline Stages", "Pipeline Steps", "Failure Strategy", "Step Group", "Matrix Strategy"]
status: stable
updated: 2026-05-11
---

# Pipelines — Stages, Steps, and Execution Flow

> [!summary] Goal
> Master Harness pipelines: stage types (Deploy, Build, Approval, Custom, Pipeline), step types (ShellScript, HTTP, K8s, Helm, Terraform, Wait, Security Scan, Chaos), step groups, failure strategies, looping/ matrix strategies, and conditional execution.

## Table of Contents

1. [Pipeline Structure](#pipeline-structure)
2. [Stage Types](#stage-types)
3. [Step Types and Step Groups](#step-types-and-step-groups)
4. [Failure Strategies](#failure-strategies)
5. [Looping and Matrix Strategies](#looping-and-matrix-strategies)

---

## Pipeline Structure

> [!info] Pipeline
> A pipeline is a sequence of stages that runs on a Harness delegate. Each stage runs steps (CI: build + test + push; CD: deploy + verify + promote; Approval: waiting for sign-off). Pipelines are defined in YAML or the visual editor.

```yaml
pipeline:
  name: "payment-service-deploy"
  identifier: payment_service_deploy
  projectIdentifier: payment
  orgIdentifier: platform_eng
  tags:
    team: "payment"
  variables:
    - name: "environment"
      type: String
      value: "staging"
    - name: "skip_security_scan"
      type: Boolean
      value: false
```

---

## Stage Types

| Stage type | Purpose |
|:-----------|:--------|
| **Deploy** | CD stage — deploys service to environment with artifact + manifest |
| **Build** | CI stage — builds, tests, and pushes artifact (Docker, Java, Node) |
| **Approval** | Manual approval (user group or pipeline executor) or Jira/ServiceNow approval |
| **Custom** | Run custom steps (Shell Script, HTTP, Terraform, Security Scan, Chaos) |
| **Pipeline** | Chain another pipeline (reuse across teams) |

```yaml
# Deploy stage example:
- stage:
    name: "Deploy to Staging"
    identifier: deploy_staging
    type: Deployment
    spec:
      deploymentType: Kubernetes
      service: payment_service
      environment: staging
      infrastructure:
        type: KubernetesDirect
        spec:
          connectorRef: account.staging_eks_cluster
          namespace: payment-staging
      execution:
        steps:
          - step:
              type: K8sRollingDeploy
              name: "Rolling Deploy"
              spec:
                skipDryRun: true
          - step:
              type: K8sDelete
              name: "Cleanup Previews"
              spec:
                deleteResources:
                  - type: "Namespace"
                    spec:
                      namespaces: ["payment-preview"]

# Approval stage:
- stage:
    name: "Approval"
    identifier: approval
    type: Approval
    spec:
      approval:
        type: HarnessApproval
        spec:
          approvers:
            userGroups:
              - account._account_all_users
            minimumCount: 1
          approverInputs:
            - name: "deploy_version"
              defaultValue: "v2.0.1"
          autoApproval: false

# Custom stage (no service or environment — for CI/Chaos/Security):
- stage:
    name: "Security Scan"
    identifier: security_scan
    type: Custom
    spec:
      execution:
        steps:
          - step:
              type: Security
              name: "SonarQube Scan"
              spec:
                mode: extraction
                config:
                  connectorRef: account.sonarqube
```

---

## Step Types and Step Groups

### Step types

| Step type | Category | Purpose |
|:----------|:---------|:--------|
| **ShellScript** | Utility | Run arbitrary bash/sh/cmd scripts |
| **Http** | Utility | Make HTTP requests (REST API calls) |
| **Wait** | Utility | Pause execution for a duration |
| **K8sRollingDeploy** | CD | Rolling deploy to K8s |
| **K8sCanaryDeploy** | CD | Canary deploy to K8s (percentage routing) |
| **K8sBlueGreenDeploy** | CD | Blue/Green deploy to K8s |
| **K8sDelete** | CD | Delete K8s resources |
| **HelmDeploy** | CD | Deploy Helm chart |
| **TerraformApply** | IaC | Run terraform plan + apply |
| **Security** | STO | Security scan (SAST/SCA/DAST) |
| **Chaos** | CE | Run chaos experiment |
| **Command** | SSH | Execute commands on SSH hosts |

### Step groups

```yaml
# Step groups organize steps within a stage. Steps in a group run sequentially.
# Step groups can be parallelized across environments via matrix.

- stage:
    type: Custom
    spec:
      execution:
        steps:
          - stepGroup:
              name: "Build and Push"
              identifier: build_and_push
              steps:
                - step:
                    type: Run
                    name: "Install Dependencies"
                    spec:
                      connectorRef: account.docker_registry
                - step:
                    type: Run
                    name: "Run Tests"
                - step:
                    name: "Docker Build & Push"
                    type: BuildAndPushDockerRegistry
                    spec:
                      connectorRef: account.aws_ecr
                      tags:
                        - "latest"
                        - <+pipeline.sequenceId>
          - stepGroup:
              name: "Deploy Services"
              parallel: true    # Steps run in parallel within group
              steps:
                - step:
                    type: K8sRollingDeploy
                    name: "Deploy API"
                - step:
                    type: K8sRollingDeploy
                    name: "Deploy Worker"
```

---

## Failure Strategies

> [!info] Failure strategy
> Each step/stage can define what happens on failure. Strategies are evaluated in order: the first matching condition triggers the action.

```yaml
- step:
    name: "Rolling Deploy"
    type: K8sRollingDeploy
    failureStrategies:
      - onFailure:
          errors:
            - AllErrors
          action:
            type: RollbackStageOnFailure       # Rollback entire stage
      - onFailure:
          errors:
            - Timeout
          action:
            type: ManualIntervention            # Wait for manual intervention

# Failure action types:
#   Type: RollbackStageOnFailure    → Rollback all K8s/ECS changes.
#   Type: AbortOnFailure            → Stop pipeline (no rollback).
#   Type: AbortAllStages            → Abort ALL running stages in pipeline.
#   Type: ManualIntervention        → Pause for manual approval: skip/retry/rollback.
#   Type: IgnoreFailed              → Continue despite failure (log warning).
#   Type: Retry                     → Retry the step N times with delay.
#   Type: StageRollback             → Only rollback the failed stage.
```

---

## Looping and Matrix Strategies

> [!info] Matrix/for each
> Use looping strategies to run a step or stage multiple times with different inputs. Useful for: deploying to multiple environments, running tests across browsers, building for multiple platforms.

```yaml
# Matrix strategy (cross-product of all axes):
- stage:
    type: Deployment
    strategy:
      matrix:
        axes:
          - name: "region"
            values: ["us-east-1", "eu-west-1", "ap-southeast-1"]
          - name: "type"
            values: ["blue", "green"]
        exclude:
          - region: "ap-southeast-1"
            type: "green"         # Exclude ap-southeast-1 + green combo
    spec:
      environment: production-<+matrix.region>
      infrastructure:
        spec:
          connectorRef: account.eks_<+matrix.region>

# For each strategy (loop over a list):
- step:
    name: "Deploy to each cluster"
    strategy:
      forEach:
        items:
          - "cluster-a"
          - "cluster-b"
          - "cluster-c"
          - "cluster-d"
    spec:
      script: |
        kubectl apply -f manifests --context <+item>

# Conditional execution:
- step:
    name: "Deploy to Prod"
    when:
      stageStatus: Success
      condition: <+stage.name> == "Deploy to Staging" && <+pipeline.environmentVariable> == "production"
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/07_Input_Sets_Overlays_and_Triggers]] for pipeline triggers with variables
- [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience]] for pipeline templates
- [[CICD/Harness/04_Playbooks/02_Troubleshoot_Pipeline_Failures]] for pipeline debugging
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for complete pipeline project
