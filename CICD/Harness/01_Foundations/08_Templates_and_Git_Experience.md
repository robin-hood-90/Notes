---
tags: [harness, foundations, templates, step-template, stage-template, pipeline-template, git-sync, git-experience, gitops]
aliases: ["Harness Templates", "Step Template", "Stage Template", "Pipeline Template", "Git Sync", "Harness Git Experience", "Remote Pipelines"]
status: stable
updated: 2026-05-11
---

# Templates and Git Experience

> [!summary] Goal
> Master Harness templates (step/stage/pipeline — reusable across projects) and Git Experience (store pipelines/input sets/templates in GitHub/GitLab/Bitbucket for version control, code review, and branching).

## Table of Contents

1. [Templates — Step, Stage, and Pipeline](#templates-step-stage-and-pipeline)
2. [Git Experience — Remote Pipelines](#git-experience-remote-pipelines)
3. [Versioning and Linking](#versioning-and-linking)

---

## Templates — Step, Stage, and Pipeline

> [!info] Template
> A template is a reusable step, stage, or pipeline that can be shared across projects. Templates can have input variables — the consumer sets values when using the template. Templates are stored at account, org, or project scope.

### Step template

```yaml
# Step template: Docker build with tagged push
template:
  name: "Docker Build & Push"
  identifier: docker_build_push
  type: Step
  spec:
    type: BuildAndPushDockerRegistry
    spec:
      connectorRef: <+input>            # Consumer provides connector
      repo: <+input>                    # Consumer provides repo name
      tags:
        - <+input>
        - <+pipeline.sequenceId>        # Auto-tag with build number
    timeout: "10m"

# Using the template in a pipeline:
- step:
    name: "Build Payment Service"
    template:
      name: "Docker Build & Push"
      templateInputs:
        connectorRef: account.aws_ecr
        repo: "my-org/payment-service"
        tags:
          - "latest"
          - <+pipeline.sequenceId>
```

### Stage template

```yaml
# Stage template: K8s deploy with approvals
template:
  name: "K8s Deploy with Approval"
  identifier: k8s_deploy_with_approval
  type: Stage
  spec:
    type: Deployment
    spec:
      service: <+input>
      environment: <+input>
      execution:
        steps:
          - step:
              type: K8sRollingDeploy
          - step:
              type: HarnessApproval
              name: "Manual Approval"
              spec:
                approvers:
                  userGroups:
                    - account._account_all_users
                  minimumCount: 1
```

### Pipeline template

```yaml
# Pipeline template: standard CI pipeline
template:
  name: "Standard CI Pipeline"
  identifier: standard_ci_pipeline
  type: Pipeline
  spec:
    stages:
      - stage:
          type: CI
          name: "Build & Test"
          spec:
            cloneCodebase: true
            platform:
              os: Linux
              arch: Amd64
            runtime:
              type: Cloud
            execution:
              steps:
                - step:                                            #<+input> for custom steps
                    type: Run
                    name: "Build"
                    spec:
                      shell: Sh
                      command: <+input>
```

---

## Git Experience — Remote Pipelines

> [!info] Git Experience
> Instead of storing pipeline YAML inside Harness, you can store pipelines, input sets, and templates in your Git repository (GitHub, GitLab, Bitbucket). Every change goes through your standard Git workflow: branch → commit → PR → merge → pipeline syncs to Harness.

```

[Image: Harness UI → Project Setup → Git Experience → Enable Git Sync]

Setup steps:
  1. Create a Git connector (GitHub/GitLab/Bitbucket with PAT or SSH key).
  2. Navigate to Account or Project Settings → Git Experience.
  3. Enable "Enable Git Experience for ...".
  4. Select connector, repository, target branch (main).
  5. Map Harness entities to Git folder paths:

Folder structure example (repo "harness-configs"):
  harness-configs/
  ├── pipelines/
  │   ├── payment-deploy.yaml
  │   ├── payment-ci.yaml
  │   └── notification-deploy.yaml
  ├── input-sets/
  │   ├── staging.yaml
  │   └── prod.yaml
  ├── templates/
  │   ├── step/
  │   │   └── docker-build.yaml
  │   └── stage/
  │       └── k8s-deploy.yaml
  └── .harness/
      └── harness-sync.yaml          # Sync configuration
```

### Working with remote pipelines

```yaml
# Remote pipeline YAML (in Git repo):
pipeline:
  name: "payment-service-deploy"
  identifier: payment_service_deploy
  store:
    type: Remote
    spec:
      connectorRef: account.github_org
      gitFetcherType: Branch
      repoName: "harness-configs"
      branch: "main"
      filePath: "pipelines/payment-deploy.yaml"
```

```text
Workflow:
  1. Developer branches off "main" in the Git repo.
  2. Edits pipeline YAML (adds a step, changes deploy strategy).
  3. Commits and pushes to branch.
  4. Opens PR to main.
  5. Harness automatically picks up changes from the branch (for live testing).
  6. PR merges to main → Harness syncs the pipeline (new version created).
  7. Old version is retained for rollback.

Branch-specific execution:
  - Pipelines can run from ANY branch in the repo.
  - Useful for testing pipeline changes before merging to main.
```

---

## Versioning and Linking

> [!info] Versioning
> All Harness entities have versions. Templates can be pinned to a specific version ("v2") or auto-updated ("stable"). Pipelines auto-version on each save. Old pipeline versions can be rolled back to.

```yaml
# Template versioning:
# When you update a template, a new version is created.
# Consumers can choose:
template:
  name: "Docker Build & Push"
  versionLabel: "3"              # Version 3 (manual bumped)

# In pipeline, reference specific version:
- step:
    template:
      name: "Docker Build & Push"
      versionLabel: "2"          # Pin to version 2 (won't auto-update)

# Or use "stable" (latest version):
- step:
    template:
      name: "Docker Build & Push"
      versionLabel: "stable"     # Auto-updates to newest version
```

### Template linking

```yaml
# Templates can reference other templates:
template:
  name: "Full Deploy Stage"
  type: Stage
  spec:
    execution:
      steps:
        - step:
            name: "Build Image"
            template:                    # References step template
              name: "Docker Build & Push"
              versionLabel: "stable"
        - step:
            name: "Deploy Canary"
            template:                    # References another step template
              name: "K8s Canary Deploy"
              versionLabel: "stable"
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for pipeline structure
- [[CICD/Harness/01_Foundations/07_Input_Sets_Overlays_and_Triggers]] for storing input sets/overlays in Git
- [[CICD/Harness/03_Advanced/05_Pipelines_as_YAML_Complete_Reference]] for full pipeline YAML reference
- [[CICD/Harness/02_Core/03_CD_GitOps_ArgoCD_as_Harness]] for GitOps based on Git
