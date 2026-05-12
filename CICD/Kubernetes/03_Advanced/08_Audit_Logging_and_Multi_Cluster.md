---
tags: [kubernetes, k8s, advanced, audit-logging, multi-cluster, cluster-api, capi, karmada, fleet, argocd-application-set]
aliases: ["Audit Logging", "Multi-Cluster", "Cluster API", "CAPI", "Karmada", "Fleet", "ArgoCD ApplicationSet"]
status: stable
updated: 2026-05-11
---

# Audit Logging and Multi-Cluster Management

> [!summary] Goal
> Master Kubernetes API server audit logging (policy, stages, event analysis, security use cases) and multi-cluster management patterns: Cluster API (CAPI) for provisioning, ArgoCD ApplicationSet for deployments, Karmada/Fleet/ACM for workload distribution, and cross-cluster service discovery.

## Table of Contents

1. [Audit Logging](#audit-logging)
2. [Multi-Cluster with Cluster API (CAPI)](#multi-cluster-with-cluster-api)
3. [Multi-Cluster Workload Distribution](#multi-cluster-workload-distribution)

---

## Audit Logging

> [!info] Audit logging
> The Kubernetes API server logs every request. The audit policy controls what is logged and at what level, at each **stage** of the request lifecycle. Audit logs are essential for security, compliance, and debugging unauthorized access.

### Audit policy stages and levels

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Log ALL requests at Metadata level by default
  - level: Metadata
  # Log CREATE pods at Request level (include body)
  - level: Request
    verbs:
      - create
    resources:
      - group: ""
        resources: ["pods"]
  # Log all DELETE requests at RequestResponse level (include body + response)
  - level: RequestResponse
    verbs:
      - delete
    resources:
      - group: ""
        resources: ["pods"]
  # Don't log read-only requests to the health endpoint
  - level: None
    resources:
      - group: ""
        resources: ["healthz", "readyz", "livez"]
```

```text
Audit stages:
  RequestReceived      — The handler has received the request (early stage)
  ResponseStarted      — Response headers sent, but body not yet (for watch/long-running)
  ResponseComplete     — Response body is complete
  Panic                — The request panicked

The level determines WHAT is logged:

  None                — Don't log events at this stage
  Metadata            — Log metadata (user, timestamp, verb, resource)
  Request             — Log metadata + request body
  RequestResponse     — Log metadata + request body + response body
```

### Configuring the API server

```yaml
# kube-apiserver flags:
--audit-policy-file=/etc/kubernetes/audit/audit-policy.yaml
--audit-log-path=/var/log/kubernetes/audit.log
--audit-log-maxage=30            # Days to keep old audit log files
--audit-log-maxbackup=10         # Max number of audit log files to keep
--audit-log-maxsize=100          # Max size (MB) before rotation

# For managed clusters (EKS/GKE/AKS):
# EKS: not configurable directly — use CloudTrail + GuardDuty for Kubernetes.
# GKE: use Cloud Logging with Kubernetes audit logs enabled.
# AKS: use Azure Monitor diagnostic settings for kube-apiserver.
```

### Audit log analysis — security use cases

```sql
-- Parse audit logs with jq (example: find all RBAC changes by a specific user):
kubectl logs -n kube-system kube-apiserver-node-1 --tail=10000 | \
  jq 'select(.user.username=="alice@company.com" and .objectRef.resource=="clusterrolebindings")'

-- Detect suspicious operations:
-- "user deleted a namespace" (could be an attacker trying to hide)
-- "user created a pod with hostNetwork: true" (privilege escalation)
-- "user created a secret" (could be exfiltration)
```

### Log collectors

```text
Audit logs are typically collected by:
  Fluent Bit / Fluentd: DaemonSet that reads api-server logs, sends to S3/Elastic/GCS/Loki.
  Vector: Rust-based log collector, lower overhead, reads file tail.
  AuditSink API (alpha): direct from API server to webhook (not widely used yet).
```

---

## Multi-Cluster with Cluster API (CAPI)

> [!info] CAPI
> Cluster API is a Kubernetes sub-project that declaratively creates, configures, and manages Kubernetes clusters. It uses `Kubernetes-style` APIs: `Cluster`, `Machine`, `MachineDeployment`, `MachineSet`. CAPI supports AWS (CAPA), Azure (CAPZ), GCP (CAPG), vSphere (CAPV), Docker (CAPD — forkind), and others.

```yaml
# Cluster API works with providers (infrastructure+K8s):
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-cluster
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["10.128.0.0/16"]
    services:
      cidrBlocks: ["10.0.0.0/16"]
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
    kind: AWSCluster
    name: prod-cluster
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: prod-cluster-control-plane

---
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSCluster
metadata:
  name: prod-cluster
spec:
  region: us-east-1
  sshKeyName: default
  vpc:
    cidrBlock: 10.0.0.0/16

---
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineDeployment
metadata:
  name: prod-cluster-workers
spec:
  clusterName: prod-cluster
  replicas: 3
  template:
    spec:
      version: v1.28.0
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
        kind: AWSMachineTemplate
        name: prod-cluster-worker-template
```

---

## Multi-Cluster Workload Distribution

> [!info] Multi-cluster patterns
> Once you have multiple clusters, you need to decide WHERE to deploy workloads. Options: **ArgoCD ApplicationSet** (list generators, cluster generators), **Karmada** (K8s-native multi-cloud scheduling), **Fleet** (Azure/Cluster API driven), **ACM** (Red Hat Advanced Cluster Management).

### ArgoCD ApplicationSet

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: payment-service
spec:
  generators:
    - clusters: {}                              # Automatically discovers clusters from ArgoCD
  template:
    metadata:
      name: payment-service-{{name}}
    spec:
      project: default
      source:
        repoURL: https://github.com/my-org/manifests.git
        targetRevision: HEAD
        path: overlays/{{name}}                # Cluster-specific overlay
      destination:
        server: '{{server}}'                   # From cluster generator
        namespace: payment-prod
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

### Karmada

```yaml
# Karmada distributes workloads across clusters using K8s-native APIs:
apiVersion: policy.karmada.io/v1alpha1
kind: PropagationPolicy
metadata:
  name: payment-service-propagation
spec:
  resourceSelectors:
    - apiVersion: apps/v1
      kind: Deployment
      name: payment-service
  placement:
    clusterAffinity:
      clusterNames:
        - prod-us-east-1
        - prod-eu-west-2
    clusterTolerations:
      - key: "topology.kubernetes.io/region"
        operator: Exists
    replicas: 3
    replicaDivisionPreference: Weighted
    replicaScheduling:
      replicaDivision: Aggregated

# Karmada also provides:
#   - OverridePolicy: modify per-cluster (e.g., different image registry for China region)
#   - ResourceTemplate: actual workload definition
#   - PropagationPolicy: placement + scheduling rules
```

### Multi-cluster service discovery

```text
Cross-cluster service discovery patterns:
  1. DNS-based: external-dns creates DNS records for services (service.example.com → multi-cluster).
  2. Service Mesh federation: Istio primary-remote, Linkerd multi-cluster, Consul admin partitions.
  3. Karmada: built-in cross-cluster service discovery.
  4. Global Load Balancer: Route 53 / CloudFront / Global DNS with health checks.

Cluster API flux pattern:
  - Production clusters created via CAPI (GitOps).
  - Pods deployed via ArgoCD ApplicationSet.
  - Monitoring via Prometheus federated or Thanos / Grafana Mimir.
```

---

## Cross-Links

- [[CICD/Kubernetes/03_Advanced/07_Service_Mesh_and_Gateway_API]] for service mesh federation
- [[CICD/Kubernetes/04_Playbooks/03_GitOps_with_ArgoCD_and_Flux]] for ArgoCD ApplicationSet
- [[CICD/AWS/02_Core/02_EKS_Clusters_Node_Groups_and_Pods]] for EKS multi-cluster patterns
- [[CICD/Kubernetes/05_Projects/01_Deploy_a_Service_With_HPA_and_Ingress]] for single-cluster baseline
