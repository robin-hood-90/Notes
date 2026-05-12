---
tags: [kubernetes, k8s, reference, components, api-server, etcd, scheduler, kubelet, kube-proxy, cni, csi, ingress, addons]
aliases: ["Kubernetes Components Reference", "K8s Components", "Kubernetes Architecture Reference", "K8s Component Table"]
status: stable
updated: 2026-05-11
---

# Kubernetes Components Reference

> [!summary] Goal
> A complete, browsable reference of every Kubernetes component — control plane, worker node, add-ons, networking, storage, security, and ecosystem tools — with definitions, roles, default ports, deployment type, and key details.

## Table of Contents

1. [Control Plane Components](#control-plane-components)
2. [Worker Node Components](#worker-node-components)
3. [Add-on and Ecosystem Components](#add-on-and-ecosystem-components)
4. [Kubernetes API Resources](#kubernetes-api-resources)
   - [Workloads](#workloads)
   - [Configuration](#configuration)
   - [Storage](#storage)
   - [Networking](#networking)
   - [RBAC](#rbac)
   - [Policy and Limits](#policy-and-limits)
   - [Autoscaling and Cluster](#autoscaling-and-cluster)

---

## Control Plane Components

> [!info] Control plane
> The control plane manages the cluster state and orchestrates workloads. Components run on dedicated control plane nodes (or as managed services in EKS/AKS/GKE). They can be deployed as static pods (kubeadm), systemd services (kubeadm), or managed services.

| Component | Role | Port | Deployment | Key details |
|:----------|:----:|:----:|:-----------|:------------|
| **kube-apiserver** | Entry point for all K8s API calls. Handles authentication, authorization, admission control, and CRD serving. | 6443 (HTTPS) | Static pod / systemd | Horizontal scaling (API server is stateless); etcd is the stateful backing store. `--audit-policy-file`, `--enable-admission-plugins`, `--tls-cert-file` config. |
| **etcd** | Distributed key-value store. Stores ALL cluster state (pods, configmaps, secrets, RBAC, CRDs). Uses Raft consensus (quorum = N/2+1). | 2379 (client), 2380 (peer) | Static pod / systemd | Backup is critical (`etcdctl snapshot save`). 3-5 nodes for HA. Defragmentation needed for large clusters. Max request size 1.5MB (pre-3.4) or 10MB (3.4+). |
| **kube-scheduler** | Assigns pods to nodes. Runs filtering (find feasible nodes) and scoring (rank nodes) phases. Supports plugins, extenders, and custom schedulers. | 10259 (HTTPS) | Static pod / systemd | Configurable via `KubeSchedulerConfiguration`. Built-in plugins: `NodeResourcesFit`, `NodeAffinity`, `TaintToleration`, `InterPodAffinity`, `VolumeBinding`. Pod priority + preemption. |
| **kube-controller-manager** | Runs 20+ control loops (controllers) that reconcile desired state with actual state. Key controllers: Deployment, ReplicaSet, Node, Endpoint, ServiceAccount, Namespace, GarbageCollector, CronJob, Job, PV, PVC, HorizontalPodAutoscaler, etc. | 10257 (HTTPS) | Static pod / systemd | Each controller runs in a single process but independently. `--controllers` flag can disable specific controllers. Leader election for HA (only one controller manager acts). |
| **cloud-controller-manager** | Cloud-provider-specific controllers that interact with the cloud API. Controllers: Node (cordon/drain cloud instances), Service (provision load balancers), Route (cloud routing). | 10258 (HTTPS) | Deployment | Optional — not included in kubeadm default. Separate binary per cloud. EKS/GKE/AKS have managed cloud-controller-manager. |

### Control plane deployment patterns

```text
kubeadm (self-managed):
  - Components run as static pods in kube-system.
  - etcd runs alongside or on separate nodes.
  - HA requires multiple control plane nodes + load balancer (HAProxy, NLB).

Managed (EKS / AKS / GKE):
  - API server, etcd, and scheduler are managed by the cloud provider.
  - kube-controller-manager is also managed.
  - Cloud-controller-manager is cloud-specific and managed.
  - You only manage worker nodes (or use Fargate/Serverless).
```

---

## Worker Node Components

> [!info] Worker node
> Each worker node runs the kubelet, kube-proxy, and a container runtime. These components run as systemd services (not static pods). Worker nodes register themselves with the API server.

| Component | Role | Port | Deployment | Key details |
|:----------|:----:|:----:|:-----------|:------------|
| **kubelet** | The primary node agent. Registers the node, creates/deletes pods, checks health (liveness/readiness/startup probes), reports node status (conditions, capacity). | 10250 (HTTPS, Kubelet API), 10255 (read-only, deprecated), 10248 (healthz) | systemd | `--node-ip`, `--kubeconfig`, `--container-runtime-endpoint`. Uses CRI (Container Runtime Interface) to talk to the runtime. Reports to API server via NodeLease (heartbeat). Evicts pods under node pressure (disk, memory, PID). |
| **kube-proxy** | Network proxy for Services. Watches API server for EndpointSlice changes, manages IPtables (or IPVS) rules to route traffic to pods. | 10249 (metricss), 10256 (healthz) | systemd (or DaemonSet) | Modes: `iptables` (default, O(1) per service), `ipvs` (faster, O(1) across services, more features), `userspace` (legacy, deprecated). Detects service/c cluster IP movement. |
| **Container runtime** | Runs containers. Implements CRI (gRPC protocol). Pulls images, manages container lifecycle, sets up cgroups and namespaces. | Unix socket only | systemd | runtimes: containerd (default), CRI-O, Docker (deprecated as of K8s 1.24). RuntimeClass can select gVisor/Kata for sandboxed containers. |
| **containerd** | Industry-standard container runtime (CNCF graduated). Manages image transfer, container lifecycle, storage. | Unix socket (`/run/containerd/containerd.sock`) | systemd | CLI: `ctr` (debug only), `nerdctl` (Docker-compatible). Config: `/etc/containerd/config.toml`. Plugins: `cri` (K8s CRI implementation), `runc` (OCI runtime). |
| **CRI-O** | Lightweight CRI implementation built for K8s. No Docker compatibility (no `docker` CLI). | Unix socket (`/var/run/crio/crio.sock`) | systemd | Default for OpenShift. Smaller footprint than containerd. Uses `conmon` for container monitoring. Supports `runtimeClass` for gVisor/Kata. |
| **runc** | OCI runtime (default). Creates and runs containers by setting up namespaces, cgroups, and rootfs. CLI: `runc run`. | N/A (called by containerd/CRI-O) | Built into containerd/CRI-O | Implements OCI Runtime Spec. Version 1.0+ includes cgroups v2 support. gVisor's `runsc` is a replacement runc that provides kernel sandboxing. |

---

## Add-on and Ecosystem Components

> [!info] Add-ons
> Add-ons extend Kubernetes functionality. They are not part of the K8s binary but are essential for production clusters. Most are deployed as Deployments/DaemonSets in `kube-system` or a dedicated namespace.

### Cluster services

| Component | Category | Role | Port | Deployment | Key details |
|:----------|:--------:|:----:|:----:|:-----------|:------------|
| **CoreDNS** | Service discovery | Provides DNS-based service discovery. Resolves `service.namespace.svc.cluster.local`, pod DNS, and external DNS. | 53 (UDP/TCP), 9153 (metrics) | Deployment (replicas 2) | ConfigMap `coredns` for custom entries. Supports forwarding (`forward . 8.8.8.8`), rewrite, template, and health plugins. Auto-scales via `cluster-proportional-autoscaler`. |
| **metrics-server** | Resource monitoring | Collects CPU and memory metrics per pod/node from the kubelet (via summary API). Used by: `kubectl top`, HPA, VPA. | 10250 (kubelet) | Deployment | In-cluster metrics pipeline: kubelet → metrics-server → API. `--kubelet-insecure-tls` for self-signed certs. `--metric-resolution` (default 60s). |
| **Cluster Autoscaler** | Autoscaling | Scales node groups up/down based on pending pods (scale-up) and node utilization (scale-down). | 8085 (metrics) | Deployment | Works with ASG (AWS), MIG (GCP), VMSS (Azure). `--expander=least-waste`, `--scale-down-enabled=true`. Respects PDBs and pod priority. |
| **Karpenter** | Autoscaling (AWS) | Directly provisions EC2 instances (no ASG). Faster than CA (seconds vs minutes). Supports consolidation, spot/on-demand mixing, and multi-arch. | 8080 (metrics) | Deployment | `Provisioner` CRD defines node requirements. `consolidation.enabled: true` replaces expensive nodes with cheaper ones. Interruption handling for spot instances. |
| **Descheduler** | Scheduling | Evicts pods that are not optimally placed. Strategies: `RemoveDuplicates`, `LowNodeUtilization`, `RemovePodsViolatingInterPodAntiAffinity`, `PodLifeTime`. | 10258 (metrics) | CronJob / Deployment | Respects PDBs, priority, and VPA. Runs periodically or continuously. |
| **VPA** | Autoscaling | Adjusts CPU/memory requests based on historical usage. Modes: Auto, Recreate, Initial, Off. Recommends target/uncapped/lower/upper bounds. | 8942 (recommender), 8943 (updater), 8080 (admission) | Deployment | Recommender (reads metrics), Updater (evicts pods), Admission controller (mutates new pods). VPA + HPA cannot share CPU metric. |

### Networking

| Component | Category | Role | Port | Deployment | Key details |
|:----------|:--------:|:----:|:----:|:-----------|:------------|
| **CNI plugin** | Network fabric | Assigns IP addresses to pods (each pod gets a cluster-unique IP), enforces network policy, optional encryption. | Varies | DaemonSet (per node) | Calico (eBPF or iptables), Cilium (eBPF), Flannel (VXLAN), Weave (encrypted overlay), AWS VPC CNI (ENI per pod), Azure CNI, GCP Dataplane. |
| **Calico** | CNI | Network policy enforcement (full support), IP-in-IP or VXLAN overlay, eBPF dataplane (option). BGP routing (no overlay needed). | 179 (BGP) | DaemonSet | `calico-node` + `calico-kube-controllers`. IPv4+IPv6 dual-stack. WireGuard encryption option. |
| **Cilium** | CNI | eBPF-based networking, observability (Hubble), and security (L7-aware policies, transparent encryption). Replaces kube-proxy mode. | 4244 (Hubble), 9962 (operator) | DaemonSet + Deployment | Performance: 0% overhead vs iptables 5-30%. Hubble: flow visibility, service map, monitoring. Cluster Mesh for multi-cluster networking. |
| **Ingress Controller** | Layer 7 routing | Exposes HTTP/HTTPS routes to services. Supports path-based and host-based routing, TLS, rate limiting, authentication. | 80/443 (NodePort/LB) | Deployment / DaemonSet | nginx-ingress (NGINX, most popular), AWS ALB Ingress Controller (ALB per Ingress), GCE Ingress (GCP LB), Traefik (dynamic config), Contour (Envoy-based), Istio (as Gateway). |
| **ExternalDNS** | DNS | Synchronizes K8s Services/Ingresses with external DNS providers (Route 53, Cloud DNS, Azure DNS). | 7979 (metrics) | Deployment | Watches Ingress and Service resources. Creates/updates/deletes DNS records. `--source=ingress`, `--domain-filter=example.com`. |
| **MetalLB** | Bare-metal LB | Provides LoadBalancer Service type for bare-metal / on-premises clusters. Supports BGP and L2 (ARP/NDP) modes. | 7472 (metrics) | Deployment | L2: one node handles all LB traffic (single point). BGP: all nodes announce, upstream router distributes traffic. |

### Storage

| Component | Category | Role | Port | Deployment | Key details |
|:----------|:--------:|:----:|:----:|:-----------|:------------|
| **CSI Driver** | Storage | Provision and mount storage volumes into pods. Implements Container Storage Interface (gRPC). Each driver handles a specific storage system. | Unix socket | DaemonSet (node plugin) + Deployment (controller) | EBS CSI, EFS CSI, GCE PD CSI, Azure Disk CSI, Azure File CSI, NFS CSI, Ceph CSI (RBD/CephFS), Rook (Ceph operator). `VolumeSnapshotClass` for snapshots. |
| **AWS EBS CSI** | CSI | Provision/attach/detach EBS volumes. Supports gp3, io2, io1. Features: volume expansion, snapshots, cross-AZ restore, NVMe reservation. | Unix socket | DaemonSet + Deployment | Requires EBS CSI Driver IAM role. `StorageClass: ebs.csi.eks.io`. Csi-NodePodTopology: EBS is AZ-bound. |
| **AWS EFS CSI** | CSI | Provision RWX volumes (EFS). Multiple pods across AZs can read/write same volume. | Unix socket | DaemonSet + Deployment | `StorageClass: efs.csi.aws.com`. Access point modes (root, subdirectory). Static provisioning only (dynamic via AccessPoint). |

### Security

| Component | Category | Role | Port | Deployment | Key details |
|:----------|:--------:|:----:|:----:|:-----------|:------------|
| **cert-manager** | Certificate management | Automates TLS certificate provisioning (from Let's Encrypt, private CA, self-signed) and renewal. CRDs: `Certificate`, `Issuer`, `ClusterIssuer`, `CertificateRequest`. | 9402 (metrics) | Deployment | HTTP-01 and DNS-01 challenge types. `ACME` issuer for Let's Encrypt. `CA` issuer for internal PKI. Secret auto-rotation. |
| **External Secrets Operator** | Secrets | Syncs secrets from external providers (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, Vault, 1Password) to K8s Secrets. | 8080 (health) | Deployment | `ExternalSecret` CRD (name, secretStoreRef, target). `ClusterSecretStore` (global) vs `SecretStore` (namespace). Refresh interval: polling. |
| **OPA Gatekeeper** | Policy | Validates/admits resources against Rego policies. CRDs: `ConstraintTemplate`, `Constraint`. Built-in library of 50+ constraints. | 8443 (webhook) | Deployment | `--audit-interval=300`. Audit finds existing violations. Configures Mutating/Validating webhooks. `K8sRequiredLabels`, `K8sRequiredProbes`, `K8sAllowedCapabilities`. |
| **Kyverno** | Policy | Kubernetes-native policy engine (YAML, not Rego). Validates, mutates, generates, and cleans up resources. | 9443 (webhook) | Deployment | `Policy` vs `ClusterPolicy`. `validationFailureAction: Enforce/Audit`. Built-in 200+ policies. Generates ConfigMaps, Secrets, and RBAC from labels. |
| **Pod Security Admission** | Built-in policy | Enforces Pod Security Standards (Privileged, Baseline, Restricted) via namespace labels. Replaces deprecated PSP (PodSecurityPolicy). | Built into API server | Built-in | No controller/deployment to install. Labels: `pod-security.kubernetes.io/enforce`, `---audit`, `---warn`. Levels: `privileged`, `baseline`, `restricted`. |
| **Falco** | Runtime security | Detects anomalous container behavior (process exec, file access, network activity) using eBPF/kernel module. Sends alerts. | 7200 (gRPC) | DaemonSet | Rules in YAML (Falco ruleset). `--modern-bpf` driver (eBPF). `--disable-*` sources. Drivers: eBPF (recommended), kernel module, pcap, k8saudit. |

### Observability

| Component | Category | Role | Port | Deployment | Key details |
|:----------|:--------:|:----:|:----:|:-----------|:------------|
| **Prometheus** | Monitoring | Collects and stores metrics from targets via HTTP pull. Query language: PromQL. TSDB with configurable retention. | 9090 (UI), 10902 (agent mode) | Deployment (or StatefulSet for HA) | `ServiceMonitor` CRD (prometheus-operator). `prometheus.yml` for static targets. Thanos/Mimir for long-term storage. AlertManager for alert routing. |
| **Grafana** | Dashboard | Visualize metrics from Prometheus, Loki, CloudWatch, and 50+ other data sources. | 3000 (UI) | Deployment | ConfigMaps for dashboards (auto-provisioning). Plugins for additional data sources. Alerting (Grafana Alerts vs AlertManager). |
| **Loki** | Log aggregation | horizontally-scalable, multi-tenant log aggregation system. Similar to Prometheus but for logs. | 3100 (HTTP API) | Deployment | Agents: Promtail (tail files), Fluent Bit (pipeline), Grafana Alloy. Queries with LogQL. Index-free (labels only). `chunk_target_size: 1.5MB`. |
| **Fluent Bit** | Log collection | Data pipeline for logs and metrics. Tails log files, parses, filters, and forwards to multiple outputs. | 2020 (HTTP) | DaemonSet | 70+ built-in plugins (input: tail, systemd; output: S3, CloudWatch, Elastic, Loki, Kafka, OpenSearch). Lower memory footprint than Fluentd. |
| **Jaeger** / **Tempo** | Distributed tracing | Collects and queries traces. Jaeger: UI + storage (Elastic, Cassandra, Badger). Tempo: object storage only (S3, GCS), cheaper. | 16686 (Jaeger UI), 3200 (Tempo) | Deployment | Istio + Jaeger: automatic tracing injection (Envoy reports spans). Tempo + Grafana: query traces from service graph. |
| **Kiali** | Service mesh UI | Visualizes Istio service mesh topology, traffic flows, health, configuration validation. | 20001 (UI) | Deployment | Shows services, workloads, versions. Graph: rate, success rate, latency per edge. Validates VirtualService, DestinationRule. |

### Service mesh and Ingress

| Component | Category | Role | Port | Deployment | Key details |
|:----------|:--------:|:----:|:----:|:-----------|:------------|
| **Envoy (Istio sidecar)** | Service mesh proxy | HTTP/1.1/2, gRPC, TCP proxy with hot reload. Transparently intercepts all inbound/outbound traffic from the pod. | 15001 (outbound redirect), 15006 (inbound), 15090 (stats) | Sidecar (injected) | Configuration via xDS APIs from Pilot. Hot reload without restart. Metrics: standard + custom (configurable stats). Tap filters for traffic inspection. |
| **linkerd-proxy (Linkerd)** | Service mesh proxy | Rust-based sidecar proxy. L4 + L7, auto-mTLS (no config needed). Minimal resource usage (~10MB, 0.5 CPU core). | 4143 (inbound), 4140 (outbound) | Sidecar (injected) | Zero-config mTLS. No sidecar container config needed. `ServiceProfile` for per-route metrics. |
| **istiod (Istio control plane)** | Service mesh control | Combines Pilot, Citadel, Galley into one binary. Manages Envoy configuration, TLS issuance, config validation. | 15010/15012 (xDS), 15014 (monitoring) | Deployment | Watches K8s resources (Service, Pod, VirtualService, DestinationRule). Generates Envoy xDS config. Scales horizontally. |

---

---

## Kubernetes API Resources

> [!info] API resources
> These are the standard Kubernetes resource types — objects you create, read, update, and delete via the API server and `kubectl`. Each resource has an API group, version, kind, and scope (Namespaced or Cluster).

### Workloads

| Resource | API | Kind | Scope | Purpose | Key fields |
|:---------|:---:|:----:|:----:|:--------|:-----------|
| **Pod** | `v1` | Pod | Namespaced | Smallest deployable unit — one or more containers sharing network and storage | `spec.containers[]`, `spec.initContainers[]`, `spec.volumes[]`, `spec.nodeName`, `spec.restartPolicy` |
| **Deployment** | `apps/v1` | Deployment | Namespaced | Declarative updates for Pods and ReplicaSets. Supports rolling, recreate, canary, blue/green | `spec.replicas`, `spec.strategy` (RollingUpdate/Recreate), `spec.selector.matchLabels`, `spec.template` |
| **ReplicaSet** | `apps/v1` | ReplicaSet | Namespaced | Ensures a desired number of pod replicas are running. Managed by Deployment — do not create directly | `spec.replicas`, `spec.selector`, `spec.template` |
| **StatefulSet** | `apps/v1` | StatefulSet | Namespaced | Stateful workloads with stable network identity and persistent storage. Ordinal naming, ordered rolling update. | `spec.serviceName`, `spec.volumeClaimTemplates[]`, `spec.podManagementPolicy` (OrderedReady/Parallel), `spec.updateStrategy` (RollingUpdate/OnDelete) |
| **DaemonSet** | `apps/v1` | DaemonSet | Namespaced | Runs one pod on every node (or a subset via nodeSelector). Used for logging, monitoring, networking | `spec.selector`, `spec.template`, `spec.updateStrategy` (RollingUpdate/OnDelete) |
| **Job** | `batch/v1` | Job | Namespaced | Runs a pod to completion. Supports parallelism and retries. | `spec.completions`, `spec.parallelism`, `spec.backoffLimit`, `spec.activeDeadlineSeconds`, `spec.ttlSecondsAfterFinished` |
| **CronJob** | `batch/v1` | CronJob | Namespaced | Runs Jobs on a schedule (cron format). | `spec.schedule`, `spec.jobTemplate`, `spec.concurrencyPolicy` (Allow/Forbid/Replace), `spec.startingDeadlineSeconds` |
| **ReplicationController** | `v1` | ReplicationController | Namespaced | Legacy — replaced by Deployment + ReplicaSet. Ensures pod count. Avoid in new clusters. | `spec.replicas`, `spec.selector`, `spec.template` |

### Configuration

| Resource | API | Kind | Scope | Purpose | Key fields |
|:---------|:---:|:----:|:----:|:--------|:-----------|
| **ConfigMap** | `v1` | ConfigMap | Namespaced | Non-confidential configuration data (key-value pairs, files). Injected as env vars, volumes, or command args. | `data` (string key-value pairs), `binaryData` (base64) |
| **Secret** | `v1` | Secret | Namespaced | Sensitive data (passwords, tokens, SSH keys, TLS certs). Types: `Opaque`, `kubernetes.io/tls`, `kubernetes.io/dockerconfigjson`, `kubernetes.io/basic-auth`, `kubernetes.io/ssh-auth` | `type`, `data` (base64-encoded), `stringData` (plain text in YAML, encoded at write) |
| **ServiceAccount** | `v1` | ServiceAccount | Namespaced | Identity for processes running in a pod. Can be bound to IAM roles (IRSA, Workload Identity). | `automountServiceAccountToken`, `secrets[]` (image pull secrets), `imagePullSecrets[]` |

### Storage

| Resource | API | Kind | Scope | Purpose | Key fields |
|:---------|:---:|:----:|:----:|:--------|:-----------|
| **PersistentVolume (PV)** | `v1` | PersistentVolume | Cluster | Cluster storage resource provisioned by an administrator or dynamically by a StorageClass. | `spec.capacity`, `spec.accessModes` (ReadWriteOnce/ReadOnlyMany/ReadWriteMany/ReadWriteOncePod), `spec.persistentVolumeReclaimPolicy` (Retain/Delete/Recycle), `spec.csi` |
| **PersistentVolumeClaim (PVC)** | `v1` | PersistentVolumeClaim | Namespaced | Request for storage by a user. Binds to a PV matching the request. | `spec.accessModes[]`, `spec.resources.requests.storage`, `spec.storageClassName`, `spec.volumeMode` (Filesystem/Block) |
| **StorageClass** | `storage.k8s.io/v1` | StorageClass | Cluster | Defines a storage class (e.g., `gp3`, `io2`, `efs`, `nfs`). Dynamic provisioning. | `provisioner` (e.g., `ebs.csi.aws.com`, `efs.csi.aws.com`), `parameters`, `reclaimPolicy`, `allowVolumeExpansion`, `volumeBindingMode` (Immediate/WaitForFirstConsumer) |
| **VolumeAttachment** | `storage.k8s.io/v1` | VolumeAttachment | Cluster | Attaches a CSI volume to a specific node. Created automatically when a pod is scheduled. | `spec.attacher`, `spec.nodeName`, `spec.source.persistentVolumeName` |
| **CSIDriver** | `storage.k8s.io/v1` | CSIDriver | Cluster | Registers a CSI driver with the cluster. Declares driver capabilities. | `spec.attachRequired`, `spec.podInfoOnMount`, `spec.requiresRepublish`, `spec.storageCapacity`, `spec.fsGroupPolicy` |
| **VolumeSnapshot** | `snapshot.storage.k8s.io/v1` | VolumeSnapshot | Namespaced | Request to snapshot a PVC. | `spec.volumeSnapshotClassName`, `spec.source.persistentVolumeClaimName` |
| **VolumeSnapshotClass** | `snapshot.storage.k8s.io/v1` | VolumeSnapshotClass | Cluster | Defines a snapshot class (driver, deletion policy). | `driver`, `deletionPolicy` (Delete/Retain) |
| **VolumeSnapshotContent** | `snapshot.storage.k8s.io/v1` | VolumeSnapshotContent | Cluster | Actual snapshot in the storage system (created by CSI). | `spec.volumeSnapshotRef`, `spec.driver`, `spec.source.snapshotHandle` (or `volumeHandle`) |
| **CSIStorageCapacity** | `storage.k8s.io/v1beta1` | CSIStorageCapacity | Namespaced | Reports storage capacity for a CSI driver. Used by the scheduler to find nodes with enough capacity. | `nodeTopology`, `capacity`, `maximumVolumeSize`, `storageClassName` |

### Networking

| Resource | API | Kind | Scope | Purpose | Key fields |
|:---------|:---:|:----:|:----:|:--------|:-----------|
| **Service** | `v1` | Service | Namespaced | Stable network endpoint for a set of pods. Types: ClusterIP (internal), NodePort (node port 30000-32767), LoadBalancer (cloud LB), ExternalName (DNS alias). | `spec.type`, `spec.ports[]`, `spec.selector`, `spec.clusterIP`, `spec.loadBalancerIP` |
| **Endpoints** | `v1` | Endpoints | Namespaced | IP address list for a Service. Deprecated in favor of EndpointSlice. | `subsets[].addresses[].ip`, `subsets[].ports[].port` |
| **EndpointSlice** | `discovery.k8s.io/v1` | EndpointSlice | Namespaced | Scalable endpoint tracking. Breaks large Service endpoint sets into slices of 100 max. | `addressType` (IPv4/IPv6/FQDN), `endpoints[].addresses[]`, `ports[]` |
| **Ingress** | `networking.k8s.io/v1` | Ingress | Namespaced | HTTP/HTTPS routing to Services. Supports host-based, path-based (`Prefix`, `Exact`), TLS, and canary routing. Requires an Ingress controller. | `spec.rules[].host`, `spec.rules[].http.paths[].path`, `spec.tls[].hosts[]`, `spec.defaultBackend` |
| **IngressClass** | `networking.k8s.io/v1` | IngressClass | Cluster | Defines which Ingress controller (e.g., nginx, ALB, Contour) processes an Ingress. | `spec.controller` (e.g., `k8s.io/ingress-nginx`), `spec.parameters` |
| **NetworkPolicy** | `networking.k8s.io/v1` | NetworkPolicy | Namespaced | Firewall rules at the pod level (L3/L4). Supports ingress + egress rules, podSelector, namespaceSelector, ipBlock. Requires a CNI that implements it (Calico, Cilium, Weave, etc.). | `spec.podSelector`, `spec.policyTypes` (Ingress/Egress), `spec.ingress[]`, `spec.egress[]` |
| **GatewayClass** | `gateway.networking.k8s.io/v1` | GatewayClass | Cluster | Defines a Gateway controller (e.g., NGINX, Envoy, Istio). | `spec.controllerName` |
| **Gateway** | `gateway.networking.k8s.io/v1` | Gateway | Namespaced | Network gateway that handles traffic entering/exiting the cluster (L4/L7). | `spec.gatewayClassName`, `spec.listeners[].port`, `spec.listeners[].protocol`, `spec.listeners[].tls` |
| **HTTPRoute** | `gateway.networking.k8s.io/v1` | HTTPRoute | Namespaced | HTTP routing rules for Gateway API. Supports matches, filters, and backendRefs. | `spec.parentRefs[]`, `spec.hostnames[]`, `spec.rules[].matches[]`, `spec.rules[].backendRefs[]` |
| **TCPRoute** | `gateway.networking.k8s.io/v1alpha2` | TCPRoute | Namespaced | TCP routing for Gateway API. | `spec.parentRefs[]`, `spec.rules[].ref` |

### RBAC (Role-Based Access Control)

| Resource | API | Kind | Scope | Purpose | Key fields |
|:---------|:---:|:----:|:----:|:--------|:-----------|
| **ClusterRole** | `rbac.authorization.k8s.io/v1` | ClusterRole | Cluster | Rules that define permissions across all namespaces (or cluster-scoped resources). | `rules[].apiGroups[]`, `rules[].resources[]`, `rules[].verbs[]` (get/list/watch/create/update/patch/delete) |
| **ClusterRoleBinding** | `rbac.authorization.k8s.io/v1` | ClusterRoleBinding | Cluster | Grants a ClusterRole to a user/group/service account across all namespaces. | `roleRef` (ClusterRole), `subjects[].kind` (User/Group/ServiceAccount) |
| **Role** | `rbac.authorization.k8s.io/v1` | Role | Namespaced | Same as ClusterRole but scoped to a namespace. | `rules[]` (same structure) |
| **RoleBinding** | `rbac.authorization.k8s.io/v1` | RoleBinding | Namespaced | Grants a Role (or ClusterRole) to a subject within a namespace. | `roleRef`, `subjects[]` |

### Policy and Limits

| Resource | API | Kind | Scope | Purpose | Key fields |
|:---------|:---:|:----:|:----:|:--------|:-----------|
| **PodDisruptionBudget** | `policy/v1` | PodDisruptionBudget | Namespaced | Limits voluntary disruptions — minAvailable or maxUnavailable pods at any time. | `spec.minAvailable`, `spec.maxUnavailable`, `spec.selector.matchLabels`, `spec.unhealthyPodEvictionPolicy` |
| **LimitRange** | `v1` | LimitRange | Namespaced | Default/ min/ max resource request/limit constraints per container, pod, PVC, or ephemeral container in a namespace. | `spec.limits[].type` (Container/Pod/PersistentVolumeClaim), `spec.limits[].max`, `spec.limits[].min`, `spec.limits[].default`, `spec.limits[].defaultRequest` |
| **ResourceQuota** | `v1` | ResourceQuota | Namespaced | Aggregate resource constraints per namespace (total CPU, memory, storage, pod count, etc.). | `spec.hard.cpu`, `spec.hard.memory`, `spec.hard.pods`, `spec.hard.requests.storage`, `spec.scopeSelector` (BestEffort/NotBestEffort/Terminating/NotTerminating/PriorityClass) |
| **PriorityClass** | `scheduling.k8s.io/v1` | PriorityClass | Cluster | Pod scheduling priority. Higher priority pods schedule before lower, can preempt lower. | `value` (0–1,000,000,000), `globalDefault`, `preemptionPolicy` (PreemptLowerPriority/Never), `description` |
| **HorizontalPodAutoscaler** | `autoscaling/v2` | HorizontalPodAutoscaler | Namespaced | Automatically scales the number of pods based on metrics (CPU, memory, custom, external). | `spec.scaleTargetRef` (Deployment/StatefulSet), `spec.minReplicas`, `spec.maxReplicas`, `spec.metrics[]`, `spec.behavior` (scaleUp/scaleDown, policies, stabilizationWindowSeconds) |
| **VerticalPodAutoscaler** | `autoscaling.k8s.io/v1` | VerticalPodAutoscaler | Namespaced | Adjusts CPU/memory requests based on historical usage. Update modes: Auto, Recreate, Initial, Off. | `spec.targetRef`, `spec.updatePolicy.updateMode`, `spec.resourcePolicy.containerPolicies[]` (minAllowed, maxAllowed, controlledResources) |
| **PriorityLevelConfiguration** | `flowcontrol.apiserver.k8s.io/v1beta3` | PriorityLevelConfiguration | Cluster | API Priority and Fairness — isolates different API requests (e.g., leader election vs list all pods). Prevents one client from overwhelming the API server. | `spec.type` (Limited/Exempt), `spec.limited.nominalConcurrencyShares`, `spec.limited.lendablePercent`, `spec.limited.limitResponse` |

### Autoscaling and Cluster

| Resource | API | Kind | Scope | Purpose | Key fields |
|:---------|:---:|:----:|:----:|:--------|:-----------|
| **ClusterRole** | `rbac.authorization.k8s.io/v1` | ClusterRole | Cluster | (see RBAC section) | |
| **Namespace** | `v1` | Namespace | Cluster | Virtual cluster — isolates resources, provides scoping for names, and can enforce ResourceQuota + LimitRange. | `metadata.name`, `spec.finalizers` (kubernetes) |
| **Node** | `v1` | Node | Cluster | Worker or control plane machine in the cluster. Registered by kubelet. | `spec.podCIDR`, `spec.taints[]`, `status.capacity` (cpu/memory/pods), `status.allocatable` (after kubelet reserved) |
| **CustomResourceDefinition** | `apiextensions.k8s.io/v1` | CustomResourceDefinition | Cluster | Extends the Kubernetes API with custom resource types (CRDs). | `spec.group`, `spec.names.kind`, `spec.scope`, `spec.versions[].schema.openAPIV3Schema`, `spec.versions[].subresources` |
| **ValidatingWebhookConfiguration** | `admissionregistration.k8s.io/v1` | ValidatingWebhookConfiguration | Cluster | Registers a validating webhook that intercepts API requests for validation. | `webhooks[].clientConfig`, `webhooks[].rules[]`, `webhooks[].failurePolicy` (Fail/Ignore), `webhooks[].sideEffects` (None/NoneOnDryRun) |
| **MutatingWebhookConfiguration** | `admissionregistration.k8s.io/v1` | MutatingWebhookConfiguration | Cluster | Registers a mutating webhook that intercepts and can modify API requests. | Same structure as ValidatingWebhookConfiguration |

---

## Cross-Links

- [[CICD/Kubernetes/01_Foundations/04_Cluster_Architecture_and_Components]] for architecture flow and API request flow diagram
- [[CICD/Kubernetes/04_Playbooks/05_Install_a_Kubernetes_Cluster_with_kubeadm]] for installation details of control plane components
- [[CICD/Kubernetes/02_Core/08_PDB_ClusterAutoscaler_AdmissionControllers]] for CA/Karpenter
- [[CICD/Kubernetes/02_Core/09_VPA_PriorityClass_kubeconfig_Descheduler]] for VPA/Descheduler
- [[CICD/Kubernetes/03_Advanced/04_NetworkPolicies_and_Pod_Security]] for OPA Gatekeeper/Kyverno/PSS
- [[CICD/Kubernetes/03_Advanced/07_Service_Mesh_and_Gateway_API]] for Istio/Linkerd/Cilium/Consul deep dive
