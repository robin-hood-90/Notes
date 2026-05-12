---
tags: [aws, core, eks, kubernetes, node-groups, irsa, karpenter, fargate, cni, addons, ebs-csi, sgpp]
aliases: ["EKS Deep Dive", "EKS Clusters", "EKS Node Groups", "IRSA", "Karpenter", "EKS Fargate", "EKS Addons"]
status: stable
updated: 2026-05-11
---

# EKS — Clusters, Node Groups, and Pods

> [!summary] Goal
> Master Amazon EKS: control plane management, node groups (managed, self-managed, Fargate), IRSA (IAM Roles for Service Accounts), Pod Identity, Karpenter vs Cluster Autoscaler, add-ons (VPC CNI, CoreDNS, EBS CSI), security groups for pods, upgrade workflows, and KMS envelope encryption.

## Table of Contents

1. [Node Groups — Managed, Self-Managed, Fargate](#node-groups-managed-self-managed-fargate)
2. [IRSA and Pod Identity](#irsa-and-pod-identity)
3. [Autoscaling — Cluster Autoscaler vs Karpenter](#autoscaling-cluster-autoscaler-vs-karpenter)
4. [EKS Add-ons and CSI Drivers](#eks-add-ons-and-csi-drivers)

---

## Node Groups — Managed, Self-Managed, Fargate

> [!info] Node groups
> EKS runs pods on nodes. Nodes can be in **managed node groups** (EKS handles AMI updates, scaling, and replacement), **self-managed node groups** (you handle everything — for custom AMIs or Karpenter), or **Fargate** (serverless — no node management needed).

| Feature | Managed NG | Self-managed NG | Fargate profile |
|:--------|:----------:|:---------------:|:---------------:|
| **AMI updates** | Automatic (rolling replace) | Manual | N/A |
| **Scaling** | EKS + ASG | ASG or custom | Automatic (per pod) |
| **Custom AMI** | No (EKS-optimized) | Yes (Bottlerocket, custom) | N/A |
| **GPU support** | Yes | Yes | No |
| **Spot instances** | Yes (via ASG) | Yes | N/A |
| **Pod networking** | aws-node (VPC CNI) | aws-node or Calico | aws-node (VPC CNI) |
| **Use case** | Default | Karpenter, custom AMIs | Serverless, no infra |

### Fargate profiles

```text
Fargate profiles run pods WITHOUT nodes:
  - Selector: namespace + optional labels.
  - Pods in selected namespaces run on Fargate if they meet constraints (no DaemonSet, no privileged, etc.).
  - Sizing: Fargate assigns vCPU/memory based on pod resource requests.
  - No node management, no scaling delays, no ASG.
  - Cost: per pod per second (pay for allocated CPU/memory).

Limitations:
  - No DaemonSets (can't run on Fargate).
  - No privileged containers.
  - No HostPort, HostNetwork, or HostPID.
  - GPUs not supported.
```

---

## IRSA and Pod Identity

> [!info] IRSA
> IAM Roles for Service Accounts (IRSA) allows pods to assume IAM roles. Each deployment/ service account gets an IAM role; the pod gets temporary credentials via projected service account token (OIDC-compatible JWT).

```text
How IRSA works:
  1. EKS cluster has an OIDC issuer URL (e.g., oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED).
  2. Create an IAM OIDC identity provider pointing to that URL.
  3. Create an IAM role with a trust policy that allows the OIDC provider to assume the role.
  4. Annotate a Kubernetes service account with the IAM role ARN.
  5. Pods using that service account get the IAM role injected via projected token volume.

Example service account:
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: my-app
    annotations:
      eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/MyAppRole

Pod Identity (EKS Pod Identity Agent):
  - Simpler than IRSA: no OIDC trust policy management.
  - Installed as an add-on (eks-pod-identity-agent).
  - IAM role is assigned to the pod via an aws-auth configmap-like mapping.
  - Supports: EC2, ECS, EKS.
```

---

## Autoscaling — Cluster Autoscaler vs Karpenter

| Feature | Cluster Autoscaler | Karpenter |
|:--------|:------------------:|:---------:|
| **Scaling logic** | ASG-based (node groups) | Direct EC2 launch (no ASG) |
| **Speed** | Minutes (ASG warmup) | Seconds (direct EC2 API) |
| **Instance diversity** | Multi-ASG config | One provisioner = many families/sizes |
| **Spot/OD mix** | Mixed instances policy | Flexible via provisioner requirements |
| **Consolidation** | No (can't replace nodes) | Yes (replaces with cheaper/ smaller) |
| **Multi-arch** | Multiple node groups | Same provisioner (amd64 + arm64) |

```yaml
# Karpenter provisioner example:
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
  limits:
    resources:
      cpu: 1000
  providerRef:
    name: default
```

---

## EKS Add-ons and CSI Drivers

```text
Managed add-ons: EKS installs and manages add-ons; it handles version upgrades.

  VPC CNI (aws-node):
    - Assigns VPC IP addresses to pods (each pod gets a real VPC IP).
    - ENI limits: each EC2 instance type has a maximum number of ENIs and IPs per ENI.
    - Subnet sizing: need enough IPs for max pods.
    - Custom networking: assign pod IPs from a secondary CIDR (to overcome ENI limits).
    - Prefix delegation: assign /28 subnets (16 IPs) per ENI instead of individual IPs.

  CoreDNS:
    - Cluster DNS: service discovery (service.namespace.svc.cluster.local).
    - Auto-scaler: scales CoreDNS based on cluster size.

  EBS CSI Driver:
    - Provision EBS volumes via StorageClass (gp3, io2).
    - Features: volume expansion, snapshots, volume cloning, cross-AZ restore.
    - Requires: IRSA role with EBS permissions.

  EFS CSI Driver:
    - Provides RWX volumes (ReadWriteMany) via NFS.
    - Good for: shared configuration, content management systems.

  EKS Pod Identity Agent: newer IAM integration method (simpler than IRSA).

  AWS Load Balancer Controller:
    - Manages ALB (Ingress) and NLB (Service type=LoadBalancer).
    - IngressGroup: share an ALB across multiple Ingress resources.
    - TargetGroupBinding: direct NLB target registration.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for VPC IP design for EKS (subnet sizing, ENI limits)
- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for IRSA trust policies
- [[CICD/AWS/03_Advanced/04_Autoscaling_ASG_and_TargetTracking]] for Cluster Autoscaler and Karpenter integration
- [[CICD/AWS/04_Playbooks/02_Debug_ECS_EKS_Deployments]] for EKS deployment issues
