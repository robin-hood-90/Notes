---
tags: [harness, foundations, delegate, kubernetes, docker, sizing, selector, token, proxy]
aliases: ["Harness Delegate", "Delegate Installation", "Delegate Sizing", "Delegate Selector"]
status: stable
updated: 2026-05-11
---

# Delegates — Installation, Sizing, and Operations

> [!summary] Goal
> Master Harness Delegates: delegate types (Kubernetes, Docker, ECS), sizing CPU/memory and heap (`-g`), selectors (tags for task matching), delegate tokens, auto-upgrade, proxy configuration, and troubleshooting connectivity.

## Table of Contents

1. [Delegate Types](#delegate-types)
2. [Installation and Sizing](#installation-and-sizing)
3. [Selectors and Task Assignment](#selectors-and-task-assignment)
4. [Auto-Upgrade and Proxy](#auto-upgrade-and-proxy)

---

## Delegate Types

> [!info] Delegate
> A Delegate is a Harness agent installed in your infrastructure that performs tasks: connecting to K8s clusters, pulling artifacts, running scripts, executing Helm commands, and running terraform. It's the bridge between Harness SaaS and your resources. Delegates communicate OUTBOUND to Harness (port 443). They never accept inbound connections.

| Delegate type | Infrastructure | Use case |
|:--------------|:--------------|:---------|
| **Kubernetes** | K8s cluster (GKE, EKS, AKS, self-managed) | Default for most CD pipelines |
| **Docker** | Single Docker host | Lightweight, testing |
| **ECS** | ECS Fargate/EC2 | For AWS-centric infrastructure |
| **Helm** | K8s cluster via Helm chart | Managed upgrades via Helm |
| **Docker Compose** | Single host with Docker Compose | Dev/CI environments |

### Kubernetes delegate (recommended)

```yaml
# harness-delegate.yaml (full manifest)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: harness-delegate-ng
  namespace: harness-delegate-ng
spec:
  replicas: 2
  selector:
    matchLabels:
      harness.io/name: harness-delegate-ng
  template:
    spec:
      containers:
        - name: delegate
          image: harness/delegate:latest
          ports:
            - containerPort: 8080
          env:
            - name: ACCOUNT_ID
              value: "YOUR_ACCOUNT_ID"
            - name: DELEGATE_TOKEN
              valueFrom:
                secretKeyRef:
                  name: delegate-token
                  key: DELEGATE_TOKEN
            - name: MANAGER_HOST_AND_PORT
              value: "https://app.harness.io"
            - name: DELEGATE_NAME
              value: "k8s-delegate-prod"
            - name: DELEGATE_TAGS
              value: "env:prod,team:platform-infra"
            - name: JAVA_OPTS
              value: "-Xms1024M -Xmx2048M"   # Heap sizing
      serviceAccountName: harness-delegate-sa
```

---

## Installation and Sizing

### Delegate sizing guidelines

```text
Recommended sizing by workload:

Light workload (1-5 pipelines, small K8s clusters):
  - CPU: 0.5-1 core
  - Memory: 2-4 GB
  - Heap: -Xms512M -Xmx1024M
  - Replicas: 1-2

Medium workload (5-50 pipelines, multiple connectors):
  - CPU: 1-2 cores
  - Memory: 4-8 GB
  - Heap: -Xms1G -Xmx4G
  - Replicas: 2-3

Heavy workload (50+ pipelines, many concurrent tasks):
  - CPU: 2-4 cores
  - Memory: 8-16 GB
  - Heap: -Xms2G -Xmx8G
  - Replicas: 3-5
```

### Installation steps

```bash
# Step 1: Create namespace
kubectl create namespace harness-delegate-ng

# Step 2: Create delegate token
# Harness UI: Account Settings → Delegates → Tokens → + New Token
# OR create a token file:
apiVersion: v1
kind: Secret
metadata:
  name: delegate-token
  namespace: harness-delegate-ng
type: Opaque
stringData:
  DELEGATE_TOKEN: "YOUR_DELEGATE_TOKEN"
```

```bash
kubectl apply -f delegate-token.yaml
kubectl apply -f harness-delegate.yaml

# Verify:
kubectl get pods -n harness-delegate-ng
# NAME                        READY   STATUS    RESTARTS   AGE
# harness-delegate-ng-0       1/1     Running   0          1m
# harness-delegate-ng-1       1/1     Running   0          1m

# Check delegate logs:
kubectl logs -n harness-delegate-ng harness-delegate-ng-0 | tail -20
# "Delegate registered with Harness" = success
```

### Heap tuning (`JAVA_OPTS`)

```yaml
# Critical for delegate stability:
env:
  - name: JAVA_OPTS
    value: "-Xms1024M -Xmx2048M -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# If delegate runs out of memory (OOMKilled):
# - Increase -Xmx value.
# - Reduce concurrent task workers (default: 2*CPU).
# - Add JAVA_OPTS: -XX:+HeapDumpOnOutOfMemoryError for diagnostics.
```

---

## Selectors and Task Assignment

> [!info] Selectors
> Delegates are assigned selectors (tags) like `env:prod` or `team:platform`. Connectors and pipeline steps use `delegateSelectors` to specify which delegate should handle the task. Harness dispatches tasks to delegates whose selectors MATCH the required selectors. If delegates are prioritized — Harness picks the delegate with the most matching selectors.

```yaml
# Delegate tags (set in DELEGATE_TAGS env or YAML):
DELEGATE_TAGS: "env:prod,team:platform,region:us-east-1"

# Connector referencing selectors (K8s connector example):
# Setup → Connectors → K8s Cluster → Delegate Selectors:
connector:
  spec:
    delegateSelectors:
      - env:prod
      - team:platform

# Pipeline step requiring selectors:
- step:
    type: ShellScript
    spec:
      delegateSelectors:
        - env:prod
```

### Selector matching logic

```text
1. Pipeline step declares selectors: ["env:prod", "team:platform"].
2. Delegate A: tags=["env:prod"] → PARTIAL match.
3. Delegate B: tags=["env:prod", "team:platform"] → FULL match → task assigned to B.
4. If no delegate matches: task is queued; no running delegate selected.

Use case: multiple teams share a delegate pool.
  - payment-team: selectors=["team:payment", "env:staging"]
  - platform-team: selectors=["team:platform", "env:prod"]
  → payment-team tasks never run on prod-capable delegate platform.
```

---

## Auto-Upgrade and Proxy

### Auto upgrade

```yaml
# By default, delegates auto-upgrade to match the Harness SaaS version.
# To disable auto-upgrade:
env:
  - name: DELEGATE_UPGRADER
    value: "false"

# Upgrade delegate version manually:
# Account Settings → Delegates → Select delegate → Actions → Upgrade
# Or re-apply YAML with updated image tag.

# Immutable delegate:
#   Harness.io automatically updates delegates when new versions are ready.
#   Delegate restarts with new image — tasks are redistributed.
#   Downtime: seconds (K8s rolling update).
```

### Proxy support

```yaml
# Delegate behind a proxy:
env:
  - name: PROXY_HOST
    value: "proxy.mycompany.com"
  - name: PROXY_PORT
    value: "8080"
  - name: PROXY_SCHEME
    value: "http"
  - name: PROXY_USER
    value: "proxy_user"
  - name: PROXY_PASSWORD
    valueFrom:
      secretKeyRef:
        name: proxy-pass
        key: PROXY_PASSWORD
  - name: NO_PROXY
    value: "kubernetes.default.svc,.local,harness.io"
```

### Delegate health and monitoring

```text
[Image: Harness UI → Delegates → Delegate Listing with heartbeat status]

Delegate states:
  - Connected: green heartbeat icon — delegate is running and receiving tasks.
  - Disconnected: red/gray icon — delegate not heard from for >3 minutes.
  - Yet to connect: still being deployed.

Delegate metrics (visible in Harness):
  - Number of tasks processed.
  - Task processing time (average per task).
  - Memory/CPU usage (if pod resource limits set).
  - Delegate version and upgrade status.
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Repos_and_External_Tools]] for delegate selector usage with connectors
- [[CICD/Harness/04_Playbooks/01_Troubleshoot_Delegates]] for delegate issues
- [[CICD/Harness/01_Foundations/01_Harness_Platform_Account_Org_Project_RBAC]] for delegate token RBAC
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for delegate setup in projects
