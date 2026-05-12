---
tags: [kubernetes, k8s, core, vpa, vertical-pod-autoscaler, priority-class, kubeconfig, kuberconfig, descheduler, kubectx]
aliases: ["VPA", "Vertical Pod Autoscaler", "PriorityClass", "kubeconfig deep dive", "Descheduler", "kubectx", "kubens"]
status: stable
updated: 2026-05-11
---

# VPA, Priority Classes, kubeconfig, and Descheduler

> [!summary] Goal
> Master Vertical Pod Autoscaler (update modes, recommender, VPA + HPA coexistence), Priority Classes (preemption, system critical pods), kubeconfig (merge, auth methods, exec-based auth, kubectx/kubens), and Descheduler (strategies for rebalancing).

## Table of Contents

1. [VPA — Vertical Pod Autoscaler](#vpa-vertical-pod-autoscaler)
2. [Priority Classes and Preemption](#priority-classes-and-preemption)
3. [kubeconfig Deep Dive](#kubeconfig-deep-dive)
4. [Descheduler](#descheduler)

---

## VPA — Vertical Pod Autoscaler

> [!info] VPA
> Vertical Pod Autoscaler adjusts CPU/memory **requests** (and optionally limits) for pods based on historical usage. It's the companion to HPA (which scales horizontally by adding/removing pods). VPA updates pod templates; it requires pods to be recreated to apply new recommendations.

### Update modes

| Mode | Behavior | Use case |
|:-----|:---------|:---------|
| **Auto** | VPA deletes and recreates pods with new resources | Default for long-running services |
| **Recreate** | Same as Auto | Same |
| **Initial** | VPA sets resources only at pod creation time | Batch jobs, first-boot sizing |
| **Off** | VPA only recommends (doesn't apply) | Dry-run, what-if analysis |

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: payment-service-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  updatePolicy:
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
      - containerName: "*"
        minAllowed:
          cpu: 100m
          memory: 256Mi
        maxAllowed:
          cpu: "4"
          memory: 8Gi
        controlledResources: ["cpu", "memory"]
        controlledValues: RequestsAndLimits

# Check VPA recommendations:
kubectl describe vpa payment-service-vpa
# Status:
#   Recommendation:
#     Container Recommendations:
#       Container Name:  payment-service
#       Lower Bound:
#         Cpu:    250m
#         Memory: 300Mi
#       Target:
#         Cpu:    500m           # Recommended CPU request
#         Memory: 600Mi         # Recommended Memory request
#       Upper Bound:
#         Cpu:    1
#         Memory: 1Gi
#   Conditions:
#     ProvisionDone    True
```

### VPA + HPA coexistence

```text
VPA and HPA CANNOT both use the same metric (CPU or memory).
  - ❌ HPA on CPU + VPA on CPU → conflict (VPA changes CPU requests, HPA sees different CPU per request).
  - ✅ HPA on custom metrics (QPS) + VPA on CPU/memory → OK.
  - ✅ HPA on CPU + VPA on memory → OK (different metrics).
  - ✅ HPA on CPU + VPA only for memory → OK.

Rule: if HPA targets CPU utilization, do NOT use VPA for CPU; use VPA only for memory.
```

---

## Priority Classes and Preemption

> [!info] PriorityClass
> A PriorityClass defines the priority of pods. Higher priority pods are scheduled before lower priority ones. If there is not enough capacity, the scheduler may **preempt** (evict) lower priority pods to make room. Predfined system classes: `system-cluster-critical`, `system-node-critical`.

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000                              # High number = high priority
globalDefault: false                     # Only applies to pods using this class
description: "For production-critical application pods"
preemptionPolicy: PreemptLowerPriority   # Preempt lower priority pods (default)
---
apiVersion: v1
kind: Pod
metadata:
  name: payment-api
spec:
  priorityClassName: high-priority
  containers:
    - name: app
      image: payment-service:latest

# Built-in priority classes:
#   system-cluster-critical (value: 2_000_000_000)
#   system-node-critical (value: 2_000_000_001)
# Higher values reserved for system components.
```

### Preemption behavior

```text
Preemption flow:
  1. High-priority pod can't be scheduled (no node with enough resources).
  2. Scheduler finds lower-priority pods that could be evicted.
  3. Scheduler evicts enough lower-priority pods to free resources.
  4. High-priority pod is scheduled on that node.
  5. Evicted lower-priority pods are requeued and re-scheduled.

Preemption + PDB: PDB is checked BEFORE preemption.
  If the PDB says "can't evict," the scheduler tries a different node.

Prevention: set `preemptionPolicy: Never` for priority classes where preemption is unwanted.
```

---

## kubeconfig Deep Dive

> [!info] kubeconfig
> The `~/.kube/config` file defines how to authenticate to clusters. It contains multiple clusters, users, and contexts. The config is a YAML file — `kubectl` merges configs from the `KUBECONFIG` env var and `~/.kube/config`.

```yaml
apiVersion: v1
kind: Config
current-context: prod-eks
contexts:
  - context:
      cluster: prod-eks
      namespace: payment
      user: prod-admin
    name: prod-eks
  - context:
      cluster: staging-gke
      user: staging-admin
    name: staging-gke
clusters:
  - cluster:
      certificate-authority: /etc/ssl/certs/ca-bundle.crt
      server: https://ABC.gr7.us-east-1.eks.amazonaws.com
    name: prod-eks
  - cluster:
      certificate-authority-data: LS0tLS1...   # Base64-encoded CA
      server: https://123.45.67.89
    name: staging-gke
users:
  - name: prod-admin
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1beta1
        command: aws
        args:
          - eks
          - get-token
          - --cluster-name
          - my-prod-cluster
        # exec-based: AWS CLI gets a token (no cert stored)
  - name: staging-admin
    user:
      token: eyJhbGciOiJSUzI1...             # Bearer token (long-lived)
```

### kubeconfig merge logic

```bash
# KUBECONFIG env var supports multiple files (colon-separated):
export KUBECONFIG=~/.kube/config:/path/to/other/config

# Merge algorithm:
#   1. Load all files in KUBECONFIG order (first file wins).
#   2. Merge clusters/users/contexts — duplicates from later files are ignored.
#   3. `current-context` from the FIRST file that defines one.

# View merged config:
kubectl config view
# Flatten (embed cert files as base64):
kubectl config view --flatten > ~/.kube/config-new

# Switch context:
kubectl config use-context prod-eks
# Or with kubectx:
kubectx prod-eks
kubens payment                # Switch namespace

# Set context directly:
kubectl config set-context my-context --cluster=prod-eks --user=admin --namespace=default
```

### Authentication methods

```text
Method            kubeconfig key               Best for
─────────────────────────────────────────────────────────
Token             user.token                    Long-lived tokens (static)
Client cert       user.client-certificate +     mTLS (user cert)
                  user.client-key
OIDC              user.exec.command =           Azure AKS, GCP GKE,
                  kubelogin get-token           custom OIDC providers
Exec              user.exec.command = aws       AWS EKS, GCP GKE,
                  eks get-token                 Azure AKS, Vault
                  (or gcloud, az, vault)
```

---

## Descheduler

> [!info] Descheduler
> The Descheduler evicts pods that are not optimally placed. It runs as a `CronJob` or continuously. It evicts pods (respecting PDBs, priority, and VPA), and the scheduler re-places them. Strategies: `RemoveDuplicates`, `LowNodeUtilization`, `RemovePodsViolatingInterPodAntiAffinity`, `RemovePodsViolatingNodeAffinity`, `RemovePodsViolatingTopologySpreadConstraint`, `PodLifeTime`.

```yaml
apiVersion: descheduler/v1alpha2
kind: DeschedulerPolicy
spec:
  strategies:
    RemoveDuplicates:
      enabled: true                               # Same replicas on same node → evict
    LowNodeUtilization:
      enabled: true
      params:
        nodeResourceUtilizationThresholds:
          thresholds:
            cpu: 20
            memory: 20
          targetThresholds:
            cpu: 50                                # Nodes below 20% → evict pods
            memory: 50                              # Target: spread to other nodes
    RemovePodsViolatingInterPodAntiAffinity:
      enabled: true                                # Evict pods violating anti-affinity
      params:
        nodeFit: true                               # Only if destination node has capacity
    RemovePodsViolatingNodeAffinity:
      enabled: true                                # Evict pods if node labels changed
    PodLifeTime:
      enabled: true
      params:
        maxPodLifeTimeSeconds: 604800              # Evict pods older than 7 days (for rotation)

# Install as CronJob or Deployment (continuous mode):
# helm install descheduler descheduler/descheduler --values policy.yaml
```

---

## Cross-Links

- [[CICD/Kubernetes/02_Core/03_HealthChecks_Resources_and_HPA]] for HPA + VPA interaction
- [[CICD/Kubernetes/02_Core/08_PDB_ClusterAutoscaler_AdmissionControllers]] for PDB + Descheduler interaction
- [[CICD/Kubernetes/02_Core/06_RBAC_and_ServiceAccounts]] for service account auth
- [[CICD/Kubernetes/04_Playbooks/05_Install_a_Kubernetes_Cluster_with_kubeadm]] for kubeconfig from cluster install
