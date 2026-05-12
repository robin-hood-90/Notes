---
tags: [harness, project, gitops, argocd, pr-pipeline, image-updater, auto-promotion, manifest-update]
aliases: ["GitOps PR Pipeline Project", "Image Updater Promotion Pipeline"]
status: stable
updated: 2026-05-11
---

# Project: GitOps PR Pipeline with Image Updater

> [!summary] Goal
> Build a GitOps-driven pipeline: CI build → push image → image updater detects new image → creates PR to update deployment manifest in Git → merge PR → ArgoCD auto-syncs. Covers GitOps agent, application, image updater registration, and PR pipeline stages.

## Architecture

```text
CI: Build Docker Image → Push to ECR
  → Image Updater watches ECR tag regex
    → Creates PR on manifests repo (new image tag)
      → PR approved and merged
        → ArgoCD syncs → deploys new image to cluster
```

### GitOps Application

```yaml
application:
  name: "payment-gitops-app"
  identifier: payment_gitops_app
  gitOpsApplication:
    repoURL: "https://github.com/my-org/k8s-manifests.git"
    targetRevision: "main"
    path: "overlays/prod"
    destination:
      namespace: payment-prod
    syncPolicy:
      automated:
        prune: true
        selfHeal: true
```

### PR Pipeline

```yaml
pipeline:
  name: "GitOps PR Pipeline"
  stages:
    - stage:
        name: "Build"
        type: CI
        spec:
          cloneCodebase: true
          runtime:
            type: Cloud
          execution:
            steps:
              - step:
                  type: Run
                  name: "Build Binary"
              - step:
                  type: BuildAndPushDockerRegistry
                  name: "Push to ECR"
    - stage:
        name: "Create PR"
        type: Custom
        spec:
          execution:
            steps:
              - step:
                  type: GitOpsPR
                  name: "Open PR"
                  spec:
                    sourceBranch: "auto/promotion-<+pipeline.sequenceId>"
                    targetBranch: "main"
                    prTitle: "Promote <+artifacts.primary.tag> to production"
                    files:
                      - path: "overlays/prod/deployment.yaml"
                        content: |
                          apiVersion: apps/v1
                          kind: Deployment
                          spec:
                            template:
                              spec:
                                containers:
                                  - name: app
                                    image: my-org/payment-service:<+artifacts.primary.tag>
    - stage:
        name: "Auto-Merge"
        type: Approval
        spec:
          approval:
            type: HarnessApproval
            spec:
              approvers:
                userGroups:
                  - account._account_all_users
                minimumCount: 1
    - stage:
        name: "Sync"
        type: Custom
        spec:
          execution:
            steps:
              - step:
                  type: GitOpsMergePR
                  name: "Merge"
              - step:
                  type: GitOpsSync
                  name: "Sync App"
                  spec:
                    applicationIdentifier: payment_gitops_app
```

---

## Cross-Links

- [[CICD/Harness/02_Core/03_CD_GitOps_ArgoCD_as_Harness]] for GitOps agent and apps
- [[CICD/Harness/05_Projects/03_Multi_Stage_CI_CD_with_Security_and_SLO]] for CI stages
- [[CICD/Harness/01_Foundations/07_Input_Sets_Overlays_and_Triggers]] for webhook triggers
