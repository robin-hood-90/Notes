---
tags: [harness, core, cd, kubernetes, canary, blue-green, rolling, helm, kustomize, manifests, workload]
aliases: ["Harness K8s CD", "K8s Canary Deploy", "K8s Blue Green Deploy", "Helm Deploy", "Kustomize Deploy"]
status: stable
updated: 2026-05-11
---

# CD — K8s Deployments (Rolling, Canary, Blue/Green)

> [!summary] Goal
> Master Harness CD for Kubernetes: rolling (incremental), canary (percentage-based, phased rollout with verification), blue/green (full stack swap). Understand Helm, Kustomize, and raw YAML manifest types, K8s pruning, skip versioning, workload types (Deployment, StatefulSet, DaemonSet), and version labels.

## Table of Contents

1. [Rolling Deployments](#rolling-deployments)
2. [Canary Deployments](#canary-deployments)
3. [Blue/Green Deployments](#blue-green-deployments)
4. [Helm, Kustomize, and Manifest Types](#helm-kustomize-and-manifest-types)

---

## Rolling Deployments

> [!info] Rolling deploy
> Rolling deploy replaces pods incrementally with zero downtime. Harness creates a new version label and performs a rolling update. Configurable: max surge (how many pods above desired), max unavailable (how many below desired). If the rolling update fails, Harness automatically rolls back.

```yaml
# Rolling deploy step:
- step:
    type: K8sRollingDeploy
    name: "Rolling Deploy"
    spec:
      skipDryRun: true
      pruningEnabled: true           # Delete old resources not in manifest
      deleteUnReleases: true         # Cleanup old Helm releases

# Rolling rollback step (automatic on failure):
- step:
    type: K8sRollingRollback
    name: "Rolling Rollback"
    spec:
      pruningEnabled: true
```

### Version labels

```yaml
# Harness adds a version label to resources (tracking multiple releases):
metadata:
  labels:
    harness.io/track: "release-42"    # Increments with each deployment

# Apply strategy: Harness creates a NEW deployment (or uses existing one).
# For rolling: updates existing deployment spec (image).
# For Blue/Green: creates entirely new deployment (with different version).
```

---

## Canary Deployments

> [!info] Canary deploy
> Canary deploy rolls out a new version to a subset of pods, runs verification (metrics, HTTP probes, chaos experiment), and then promotes to full rollout OR rolls back. Phases: 1. Deploy canary (e.g., 25% pods), 2. Verify canary, 3. Promote (full rollout), 4. Clean up canary.

```yaml
# Canary deploy step — multiple phases:
- step:
    type: K8sCanaryDeploy
    name: "Canary Deploy"
    spec:
      instanceSelection:
        type: Count                # or Percentage (percentage-based routing)
        spec:
          count: 3                 # Run 3 canary pods initially
      skipDryRun: true

# Canary delete (cleanup before deployment):
- step:
    type: K8sCanaryDelete
    name: "Canary Cleanup"
    spec:
      deleteResources:
        - type: "Deployment"
          spec:
            namespaces: ["<+infra.namespace>"]

# Full pipeline with canary phases:
# 1. Canary Deploy → 2. (Canary Verification via HTTP probe or Chaos experiment)
# → 3. Canary Delete → 4. Stage rollout or rollback

# Canary via percentage (Istio/ service mesh):
# service with virtual service splits traffic:
- step:
    type: K8sCanaryDeploy
    spec:
      instanceSelection:
        type: Percentage
        spec:
          percentage: 20           # 20% traffic to canary version
```

### Canary with verification

```yaml
- stage:
    type: Deployment
    spec:
      execution:
        steps:
          - step:
              type: K8sCanaryDeploy
          - step:
              type: Http                           # Verify canary is healthy
              name: "Canary Verification"
              spec:
                url: "https://canary-test.example.com/healthz"
                method: GET
                assertion: "<+httpResponseCode> == 200"
          - step:
              type: K8sCanaryDelete
```

---

## Blue/Green Deployments

> [!info] Blue/Green deploy
> Blue/Green runs two versions simultaneously. The "blue" (existing) + "green" (new) versions both receive traffic from the service. The service selector label is swapped from blue→green to switch traffic. Stage: 1. Deploy green (new), 2. Route traffic to green (swap service selector), 3. Scale down blue (remove old replicas).

```yaml
# Blue/Green steps:
- step:
    type: K8sBlueGreenDeploy
    name: "Deploy Green"
    spec:
      skipDryRun: true

- step:
    type: K8sBGServices
    name: "Route to Green"
    spec:
      skipDryRun: true

- step:
    type: K8sBGStageScaleDown
    name: "Cleanup Blue"

# Blue/Green rollback:
- step:
    type: K8sBGStageScaleDown
    name: "Scale Down Green"             # If verification fails
```

### Blue/Green service selector

```yaml
# Service YAML (before deployment):
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
    harness.io/track: "green"     # Harness automatically updates this label
```

---

## Helm, Kustomize, and Manifest Types

> [!info] Manifest types
> Harness supports three manifest types for K8s: **Helm chart** (with values overlays — popular for complex apps), **Kustomize** (base + overlay pattern), **raw YAML** (simple deployments).

### Helm deployment

```yaml
# Service with Helm chart:
service:
  serviceDefinition:
    type: Kubernetes
    spec:
      manifests:
        - manifest:
            type: HelmChart
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: Branch
                  repoName: "my-org/helm-charts"
                  files:
                    - "my-app/Chart.yaml"
              valuesPaths:
                - "my-app/values.yaml"
                - "my-app/values/env/<+pipeline.variables.environment>.yaml"
```

### Kustomize deployment

```yaml
service:
  serviceDefinition:
    type: Kubernetes
    spec:
      manifests:
        - manifest:
            type: Kustomize
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: CommitSha            # Pin to exact commit
                  repoName: "my-org/kustomize-configs"
                  folderPath: "overlays/prod"        # Kustomize overlay path
```

### Raw YAML deployment

```yaml
service:
  serviceDefinition:
    type: Kubernetes
    spec:
      manifests:
        - manifest:
            type: OpenshiftTemplate
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: Branch
                  repoName: "my-org/deployment-configs"
                  files:
                    - "deployment.yaml"
                    - "service.yaml"
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/05_Services_Environments_and_Overrides]] for service and env definitions
- [[CICD/Harness/02_Core/02_CD_ECS_Serverless_SSH_Deployments]] for non-K8s deployments
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for full K8s CD pipeline
- [[CICD/Harness/04_Playbooks/02_Troubleshoot_Pipeline_Failures]] for pipeline debugging
