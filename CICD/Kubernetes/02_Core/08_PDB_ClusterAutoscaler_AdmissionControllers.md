---
tags: [kubernetes, k8s, core, pdb, cluster-autoscaler, admission-webhook, pod-antiaffinity, mutating-webhook, validating-webhook]
aliases: ["Pod Disruption Budgets", "Cluster Autoscaler", "Admission Controllers", "Webhooks", "PDB"]
status: stable
updated: 2026-05-11
---

# PDB, Cluster Autoscaler, and Admission Controllers

> [!summary] Goal
> Master three critical production patterns: Pod Disruption Budgets (PDB) for HA, Cluster Autoscaler (CA) vs Karpenter for scaling, and Admission Controllers (MutatingWebhook, ValidatingWebhook, built-in) for cluster governance.

## Table of Contents

1. [Pod Disruption Budgets](#pod-disruption-budgets)
2. [Cluster Autoscaler vs Karpenter](#cluster-autoscaler-vs-karpenter)
3. [Admission Controllers](#admission-controllers)

---

## Pod Disruption Budgets

> [!info] PDB
> A Pod Disruption Budget limits the number of pods that can be voluntarily disrupted at a time. **Voluntary disruptions**: node drain, Cluster Autoscaler scale-down, Descheduler eviction. **Involuntary disruptions**: node hardware failure, network partition, OOM. PDBs only protect against voluntary disruptions.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-api-pdb
spec:
  minAvailable: 3                # At least 3 pods must remain healthy
  # OR maxUnavailable: 1         # At most 1 pod can be down
  selector:
    matchLabels:
      app: payment-api

# unhealthyPodEvictionPolicy (K8s 1.27+):
#   IfHealthyBudget: only evict if budget is met AND the pod is healthy.
#   AlwaysAllow: evict even if the pod is not healthy (default).
#   Used when you want PDB to protect healthy pods but not block replacement of already-broken ones.
```

### PDB with HPA + Cluster Autoscaler

```text
If PDBs, HPA, and Cluster Autoscaler are not designed together, deadlocks can occur:

Deadlock example:
  1. HPA scales up from 3 to 6 pods.
  2. CA needs to add nodes — but existing nodes have space (no scale-up needed).
  3. HPA scales back to 3 pods (traffic drops).
  4. CA wants to remove nodes — but PDB says "At least 3 pods must be available."
  5. MyApp pods are running on 3 nodes: 1 pod each.
  6. CA cannot drain a node (that would go below 3).
  7. CA cannot scale down. PDB stops CA.

Solutions:
  - Allow CA to evict pods before PDB checking: PDB only blocks voluntary disruptions.
    CA respects PDB and won't evict past the budget.
  - Set `maxUnavailable: 50%` instead of an absolute number.
  - Configure CA `--max-node-provision-time` to avoid long delays.
```

### Node drain with PDB

```bash
# Node drain respects PDB — it will NOT evict a pod if it violates the PDB.
# If it can't evict after timeout, it fails:
kubectl drain node-1 --ignore-daemonsets --grace-period=120 --timeout=120s

# Check PDB status:
kubectl get pdb payment-api-pdb -o yaml
# .status.disruptionsAllowed = how many pods can be evicted right now
# .status.expectedPods = how many pods match the selector
# .status.currentHealthy = currently healthy pods
# .status.desiredHealthy = minAvailable
```

---

## Cluster Autoscaler vs Karpenter

> [!info] Cluster Autoscaler
> Cluster Autoscaler (CA) scales node groups based on pending pods. It works with ASGs (AWS), MIGs (GCP), or other node group providers. Karpenter (AWS) directly launches EC2 instances (no ASG) for faster, more flexible scaling.

| Feature | Cluster Autoscaler | Karpenter |
|:--------|:------------------:|:---------:|
| **Architecture** | Node group-based (ASG) | Direct EC2 API (no ASG) |
| **Speed** | Minutes (ASG warmup) | Seconds (EC2 API) |
| **Instance diversity** | Multiple node groups | Single provisioner (any family/size) |
| **Spot/OD mix** | Mixed instances policy | Flexible via requirements |
| **Consolidation** | No (only scales by pending pods) | Yes (replaces with cheaper/smaller) |
| **Multi-arch** | Multiple node groups | Same provisioner |

### Cluster Autoscaler configuration

```yaml
# CA command line args:
--scale-down-enabled=true
--scale-down-delay-after-add=10m        # Wait 10m after scale-up before considering scale-down
--scale-down-unneeded-time=10m          # Node unneeded for 10m before scale-down
--scale-down-utilization-threshold=0.5  # Node utilization < 50% → eligible for scale-down
--max-nodes-total=100
--cores-min=4 --cores-max=512
--expander=least-waste                  # Picks node group with least wasted CPU/memory
                                        # Options: random, most-pods, least-waste, priority
```

### Karpenter provisioner

```yaml
apiVersion: karpenter.sh/v1beta1
kind: Provisioner
metadata:
  name: default
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot", "on-demand"]
    - key: kubernetes.io/arch
      operator: In
      values: ["amd64", "arm64"]
    - key: karpenter.k8s.aws/instance-generation
      operator: Gt
      values: ["2"]                       # Use at least 3rd gen instances
    - key: karpenter.k8s.aws/instance-family
      operator: NotIn
      values: ["t3", "t2"]               # Skip burstable instances
  limits:
    resources:
      cpu: 1000                           # Max 1000 CPU across all provisioned nodes
  provider:
    subnetSelector:
      karpenter.sh/discovery: "my-cluster"
    securityGroupSelector:
      karpenter.sh/discovery: "my-cluster"
  ttlSecondsAfterEmpty: 30                # Terminate node after 30s with no pods
  consolidation:
    enabled: true                         # Replace nodes with cheaper/smaller ones
  disruption:
    consolidationPolicy: WhenUnderutilized
    expireAfter: 720h                     # Node max lifetime: 30 days
```

---

## Admission Controllers

> [!info] Admission controllers
> Admission controllers intercept requests to the API server AFTER authentication/authorization but BEFORE persistence. They can mutate (modify) or validate the request. There are two types: **built-in** (compiled into kube-apiserver) and **dynamic** (webhooks).

### Built-in admission controllers

```text
Controller                    Purpose
──────────────────────────────────────────────────────────
NamespaceLifecycle            Rejects requests to non-existent namespaces
LimitRanger                   Enforces limits defined in LimitRange
PodSecurity                   Replaces PodSecurityPolicy — enforce by namespace labels
NodeRestriction               Limits kubelet's self-modification
ServiceAccount                Auto-creates service account, automounts token
MutatingAdmissionWebhook      Invokes external mutation webhooks
ValidatingAdmissionWebhook    Invokes external validation webhooks
ResourceQuota                 Enforces namespace ResourceQuota
AlwaysPullImages              Ensures images always pull — no local cache
ImagePolicyWebhook            Image admission control (custom webhook)
DefaultStorageClass           Sets default StorageClass for PVCs
DefaultTolerationSeconds      Sets default toleration for taints
CertificateApproval           
CertificateSigning            
ClusterTrustBundleAttest      
```

### Webhook configuration

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: "pod-security-webhook.example.com"
webhooks:
  - name: "pod-security-webhook.example.com"
    clientConfig:
      service:
        namespace: webhook-system
        name: pod-security-webhook
        path: /validate
      caBundle: LS0tLS1CRUdJTiBDRV...    # CA cert for webhook TLS
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
        scope: "Namespaced"
    admissionReviewVersions: ["v1"]
    sideEffects: NoneOnDryRun
    timeoutSeconds: 10
    failurePolicy: Fail                     # Fail closed: if webhook down, reject request
                                            # Options: Fail, Ignore (for non-critical checks)
    matchConditions:                        # K8s 1.27+: skip if condition evaluates false
      - name: "skip-kube-system"
        expression: "request.namespace != 'kube-system'"
    objectSelector:                         # Skip pods with specific labels
      matchExpressions:
        - key: webhook-policy
          operator: NotIn
          values: ["skip-policy"]
```

### Webhook cert management with cert-manager

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: webhook-tls
  namespace: webhook-system
spec:
  dnsNames:
    - "webhook-service.webhook-system.svc"
    - "webhook-service.webhook-system.svc.cluster.local"
  issuerRef:
    name: selfsigned-issuer
    kind: ClusterIssuer
  secretName: webhook-tls
---
# CA Bundle is automatically injected by cert-manager-csi-driver or manual patch:
kubectl patch validatingwebhookconfigurations webhook-config \
  --patch '{"webhooks":[{"name":"webhook.example.com","clientConfig":{"caBundle":"'$(base64 -w0 < ca.crt)'"}}]}'
```

---

## Cross-Links

- [[CICD/Kubernetes/03_Advanced/04_NetworkPolicies_and_Pod_Security]] for PodSecurity admission
- [[CICD/Kubernetes/02_Core/03_HealthChecks_Resources_and_HPA]] for HPA + PDB + CA interaction
- [[CICD/AWS/02_Core/02_EKS_Clusters_Node_Groups_and_Pods]] for EKS-specific CA/Karpenter config
- [[CICD/Kubernetes/04_Playbooks/01_Troubleshoot_CrashLoopBackOff]] for pod admission failures
