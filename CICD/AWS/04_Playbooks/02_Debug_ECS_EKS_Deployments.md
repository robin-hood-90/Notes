---
tags: [aws, playbook, ecs, eks, deployment, failure, stopped-tasks, crashloop, irsa, cni]
aliases: ["Debug ECS Deployments", "Debug EKS Pod Failures", "Stopped Tasks", "CrashLoopBackOff"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug ECS/EKS Deployments

> [!summary] Goal
> Diagnose ECS task failures and EKS pod startup issues: stopped tasks (resource limits, image pull, essential container exit), service events, deployment circuit breaker, Karpenter provisioning issues, CNI networking, and IRSA token errors.

## ECS: Stopped Task Reasons

| `StoppedReason` | Fix |
|:----------------|:----|
| `Essential container in task exited` | Check container logs. Container `essential: true` must not exit. |
| `CannotPullContainerError` | Check ECR repository policy, task execution role, VPC endpoint for ECR. |
| `ResourceInitializationError: unable to pull secrets` | Check task execution role for SSM/Secrets Manager permissions. |
| `OutOfMemoryError` | Increase task memory or fix memory leak. |
| `Task failed to start` | Check VPC subnet ENI limits, security group rules. |

## EKS: Pod Status Quick Reference

| Status | Cause |
|:-------|:------|
| `ImagePullBackOff` | Image name wrong, ECR auth, no VPC endpoint |
| `CrashLoopBackOff` | App exits on startup (check logs) |
| `Pending` (CPU) | Insufficient node capacity |
| `Pending` (PVC) | PVC not bound (check StorageClass, CSI driver) |
| `CreateContainerConfigError` | ConfigMap/Secret not found |

---

## Cross-Links

- [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] for ECS service configuration
- [[CICD/AWS/02_Core/02_EKS_Clusters_Node_Groups_and_Pods]] for EKS pod networking
- [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] for logs and metrics
