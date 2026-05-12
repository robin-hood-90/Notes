---
tags: [harness, core, gitops, argocd, gitops-agent, application, image-updater, sync-policy, pr-pipeline]
aliases: ["Harness GitOps", "ArgoCD on Harness", "GitOps Agent", "GitOps Application", "Image Updater", "PR Pipeline"]
status: stable
updated: 2026-05-11
---

# CD — GitOps (ArgoCD as Harness)

> [!summary] Goal
> Master Harness GitOps: Harness-managed ArgoCD agents, GitOps applications (repo+path+cluster), GitOps PR pipelines (automated PR creation on env promotion), image updater (auto-promotion on new image), sync policy (auto/manual, prune, self-heal), and GitOps repository setup.

## Table of Contents

1. [GitOps Agent and Cluster Management](#gitops-agent-and-cluster-management)
2. [GitOps Applications](#gitops-applications)
3. [Image Updater and PR Pipelines](#image-updater-and-pr-pipelines)

---

## GitOps Agent and Cluster Management

> [!info] GitOps
> Harness GitOps uses ArgoCD under the hood, managed by Harness agents. The GitOps Agent is an ArgoCD instance deployed in your cluster (or managed by Harness). Agents connect to Git repositories and target clusters. Harness manages agent upgrades, high availability, and monitoring.

### GitOps Agent setup

```yaml
# GitOps Agent YAML (deployed in cluster):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: harness-gitops-agent
  namespace: harness-gitops
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: agent
          image: harness/gitops-agent:latest
          env:
            - name: ACCOUNT_ID
              value: "YOUR_ACCOUNT_ID"
            - name: AGENT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: gitops-agent-token
                  key: AGENT_TOKEN
            - name: SERVER_ENDPOINT
              value: "wss://app.harness.io/gitops"
              # WebSocket connection to Harness
```

### Agent configuration

```text
[Image: Harness UI → GitOps → Agents → + New Agent]

Steps:
  1. Navigate to GitOps → Agents → + New Agent.
  2. Name: "prod-gitops-agent".
  3. Select installation type: Harness Managed (SaaS handles upgrades) or Self-Managed (you handle).
  4. If Harness Managed: provide namespace, Harness generates YAML manifest.
  5. Apply manifest to cluster (`kubectl apply -f agent.yaml`).
  6. Agent connects to Harness via WebSocket.
  7. Verify: Agent shows "Connected" status.

GitOps Cluster (target cluster for deployments):
  GitOps → Clusters → + New Cluster → name: "prod-eks" → connectorRef: prod_eks_connector
```

---

## GitOps Applications

> [!info] GitOps Application
> A GitOps Application maps: Environment + Git Repository (repo + path + revision) + Cluster. Harness syncs the application (ArgoCD ensures the cluster matches the Git state). Multiple environments (dev→staging→prod) point to same repo but different paths/branches.

```yaml
# GitOps Application YAML (stored in Harness):
application:
  name: "payment-service-prod"
  identifier: payment_service_prod
  gitOpsApplication:
    repoURL: "https://github.com/my-org/k8s-manifests.git"
    targetRevision: "main"
    path: "overlays/prod"                     # Kustomize overlay for prod
    destination:
      namespace: payment-prod
      server: "https://kubernetes.default.svc"   # Cluster URL
    syncPolicy:
      automated:
        prune: true          # Delete resources removed from Git
        selfHeal: true       # Revert manual changes to match Git
      syncOptions:
        - CreateNamespace=true
    info:
      - name: "Team"
        value: "Payment"

# In pipeline (GitOps stage):
- stage:
    name: "GitOps Deploy"
    identifier: gitops_deploy
    type: Deployment
    spec:
      deploymentType: Kubernetes
      execution:
        steps:
          - step:
              type: GitOpsPR
              name: "Create PR"
          - step:
              type: GitOpsMergePR
              name: "Merge PR"
          - step:
              type: GitOpsSync
              name: "Wait for Sync"
              spec:
                applicationIdentifier: payment_service_prod
```

---

## Image Updater and PR Pipelines

> [!info] Image Updater
> Harness Image Updater automatically updates a GitOps application's manifest when a new Docker image is pushed. It watches ECR/Docker/GCR for new image tags and creates a PR to update the deployment image tag in the Git repo.

### Image updater configuration

```yaml
# Image updater watches ECR for new tags matching payment-v*:
imageUpdater:
  type: ECR
  spec:
    region: "us-east-1"
    repoName: "my-app"
    tagRegex: "^payment-v\\d+\\.\\d+\\.\\d+$"
    gitOpsAppIdentifier: payment-service-staging
```

### PR pipeline

```yaml
# Full PR pipeline (build → push → update manifest → merge → sync):
pipeine:
  name: "GitOps PR Pipeline"
  stages:
    - stage:
        name: "Build and Push"
        type: CI
        spec:
          execution:
            steps:
              - step: { type: Run, name: "Build" }
              - step: { type: BuildAndPushDockerRegistry, name: "Push Image" }
    - stage:
        name: "Update Manifest"
        type: Custom
        spec:
          execution:
            steps:
              - step:
                  type: GitOpsPR
                  name: "Create PR"
                  spec:
                    sourceBranch: "auto/env-staging-<+pipeline.sequenceId>"
                    targetBranch: "main"
                    prTitle: "Promote image to staging: <+artifacts.primary.tag>"
                    files:
                      - path: "overlays/staging/deployment.yaml"
                        content: |
                          apiVersion: apps/v1
                          kind: Deployment
                          spec:
                            template:
                              spec:
                                containers:
                                  - name: app
                                    image: my-app:<+artifacts.primary.tag>
    - stage:
        name: "Auto Merge"
        type: Approval
        spec:
          approval:
            type: HarnessApproval
            spec:
              approvers:
                userGroups:
                  - account._account_all_users
                minimumCount: 1
              approvalMessage: "Deploy image <+artifacts.primary.tag> to staging?"
    - stage:
        name: "GitOps Sync"
        spec:
          execution:
            steps:
              - step:
                  type: GitOpsMergePR
                  name: "Merge PR"
              - step:
                  type: GitOpsSync
                  name: "Wait for Sync"
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience]] for Git Experience fundamentals
- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for K8s deployments
- [[CICD/Harness/05_Projects/02_GitOps_PR_Pipeline_with_Image_Updater]] for full GitOps project
- [[CICD/Harness/01_Foundations/07_Input_Sets_Overlays_and_Triggers]] for webhook triggers on GitOps
